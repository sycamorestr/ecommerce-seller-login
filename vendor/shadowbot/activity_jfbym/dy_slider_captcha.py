import xbot
import os
import xbot_visual
import base64
import json
import io
import http.client
import sqlite3
import ast
import math
import random
import time
from contextlib import closing
from pathlib import Path
from PIL import Image

from urllib.parse import urlparse
from io import BytesIO
from xbot.selector import Selector

if os.name == 'nt':
    from ctypes import windll

from xbot import print, sleep, win32, web
from . import package
from .package import variables as glv

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi


_used = {}
_last_move_target = None

def _shape_features(pts):
    """2026-10-11 离线分析(t≈±2.6 起显著): 窗口外通过轮比被拒轮
    更快更短、Y 抖动更大、微动更少、停顿段略多。返回五元组特征。"""
    dxs = [float(p[0]) for p in pts]
    dts = [float(p[2]) for p in pts]
    total_t = math.fsum(dts)
    net = math.fsum(dxs)
    if total_t <= 0 or net <= 0:
        return None
    ys = [0.0]
    for p in pts:
        ys.append(ys[-1] + float(p[1]))
    n = len(dxs)
    micro = sum(1 for d in dxs if 0 < abs(d) <= 1.5)
    zeros = sum(1 for d in dxs if abs(d) < 1e-9)
    mean_y = math.fsum(ys) / len(ys)
    var_y = math.fsum((v - mean_y) ** 2 for v in ys) / len(ys)
    return (total_t, net / total_t * 1000.0, micro / n, math.sqrt(var_y), zeros / n)


def _pool_stats(rows):
    """rows 为 (tid, distance, pts, ...) 元组列表,pts 恒在索引 2。"""
    feats = []
    for row in rows:
        f = _shape_features(row[2])
        if f is not None:
            feats.append(f)
    if len(feats) < 2:
        return None
    cols = list(zip(*feats))
    stats = []
    for col in cols:
        mean = math.fsum(col) / len(col)
        var = math.fsum((v - mean) ** 2 for v in col) / len(col)
        stats.append((mean, math.sqrt(var) or 1.0))
    return stats


# 权重 ≈ 分析中各特征 |t| 的归一化: 时长 2.59 / 速度 2.69 / 微动 2.86 / Y抖 4.34 / 停顿 3.20
_WEIGHTS = (-0.21, 0.21, -0.23, 0.35, 0.26)


# 2026-10-11 实机标定(滑块, pywin32/HID + weighted 池, 每档 10 轮批次的峰值):
# 各 dpr 下实测最优 y_gain。非单调(1.167→2.5 而 1.3125→1.33),
# 不能用一个公式拟合; 按最近邻线性插值, 区间外取最近端点。
# 同日跨系统缩放复测: dpr 1.0(系统100%)基线 70%→gain 1.75 后 90%(符合
# 1.75/dpr 物理抖动不变量); dpr 1.5(系统150%)基线即 90%, 无需补偿(黄金窗口)。
_GAIN_TABLE = ((0.583, 3.0), (0.875, 2.0), (1.0, 1.75), (1.167, 2.5),
               (1.3125, 1.33), (1.4, 1.0), (1.5, 1.0), (1.575, 1.0), (1.75, 1.25))


def y_gain_for_dpr(dpr):
    """按当前页面 devicePixelRatio 查实测最优 Y 抖动补偿系数。"""
    if not (isinstance(dpr, (int, float)) and math.isfinite(dpr) and dpr > 0):
        raise ValueError('dpr 必须是正的有限数')
    table = _GAIN_TABLE
    if dpr <= table[0][0]:
        return table[0][1]
    if dpr >= table[-1][0]:
        return table[-1][1]
    for (d0, g0), (d1, g1) in zip(table, table[1:]):
        if d0 <= dpr <= d1:
            return g0 + (g1 - g0) * (dpr - d0) / (d1 - d0)
    return 1.0  # pragma: no cover


def _clip_prefix(pts, travel):
    """截取覆盖 travel 净位移的源前缀; 末步内插, 保留原始 dy/dt。"""
    out = [[0.0, 0.0, 0.0]]
    x = 0.0
    for p in pts[1:]:
        dx, dy, dt = float(p[0]), float(p[1]), float(p[2])
        if x >= travel:
            break
        if x + dx >= travel:
            remain = travel - x
            if remain > 0.0 and dx > 0.0:
                frac = remain / dx
                out.append([remain, dy * frac, dt * frac])
            break
        out.append([dx, dy, dt])
        x += dx
    if sum(p[0] for p in out) < travel - 1e-9:
        raise ValueError('源轨迹无法覆盖目标位移')
    return out


def generate_trajectory(distance, db_path=None, max_points=14, probe_dx=8.0, y_gain=1.0):
    """按目标距离选择真人轨迹，返回 (累计x, 累计y, 累计毫秒) 列表。

    2026-10-11 最终版: strict 形状过滤(剔除极端过冲/回撤), 按实际净位移
    ±3px 匹配, weighted 人味特征加权随机, 缩放不超过 1.25 倍(偏短目标截前缀),
    y_gain 为当前 dpr 的 Y 抖动补偿(取 y_gain_for_dpr)。
    2026-10-12: 时长带优选固化(实机: ≤1146ms 全过/≥1262ms 全拒),
    优先 ≤1250ms 快轨迹, 空带回退全池。
    """
    target = float(distance)
    wanted = round(target)
    path = Path(db_path) if db_path is not None else Path(__file__).resolve().parents[1] / "database.db"
    path = path.resolve()
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(tracker)")}
        query = "SELECT id, distance, data FROM tracker"
        if "source" in columns:
            query += " WHERE source='human_ui'"
            if "quality" in columns:
                query += " AND (quality IS NULL OR quality='ok')"
        rows = conn.execute(query).fetchall()

    trajectories = []
    for tid, recorded_distance, data in rows:
        try:
            pts = [tuple(map(float, row)) for row in json.loads(data)]
            if len(pts) < 8 or any(len(p) != 3 for p in pts):
                continue
            if any(not math.isfinite(v) for p in pts for v in p):
                continue
            if any(p[2] < 0 for p in pts) or not 100 <= sum(p[2] for p in pts) <= 10000:
                continue
            if [float(v) for v in pts[0]] != [0.0, 0.0, 0.0]:
                continue
            net = math.fsum(p[0] for p in pts)
            if net <= 1e-9:
                continue
            # strict 形状过滤: 过冲/总回撤超过 max(20px, 净位移50%) 的剔除
            x = peak = 0.0
            for p in pts:
                x += p[0]
                peak = max(peak, x)
            backtrack = math.fsum(-p[0] for p in pts if p[0] < 0)
            limit = max(20.0, 0.5 * net)
            if peak - net > limit or backtrack > limit:
                continue
            if wanted / net > 1.25:  # 缩放不超过 1.25 倍
                continue
            trajectories.append((tid, int(recorded_distance), pts, net))
        except (ValueError, TypeError, OverflowError):
            continue
    if not trajectories:
        raise ValueError("数据库中没有符合形状及缩放限制的真人轨迹")

    used = _used.setdefault(str(path), set())
    available = [t for t in trajectories if t[0] not in used]
    if not available:
        used.clear()
        available = trajectories
    # 时长带优选(2026-10-12 另一台机器实测: 时长≤1146ms 全过/≥1262ms 全拒):
    # 优先 ≤1250ms 的快轨迹候选, 空带时回退全池, 不阻断选样。
    fast = [t for t in available
            if (_shape_features(t[2]) or (1e9,))[0] <= 1250.0]
    if fast:
        available = fast
    # 按实际净位移 ±3px 匹配, 无候选时取最近净位移
    near = [t for t in available if abs(t[3] - wanted) <= 3]
    if not near:
        closest = min(abs(t[3] - wanted) for t in available)
        near = [t for t in available if abs(t[3] - wanted) == closest]

    # weighted: 按人味特征 softmax 加权随机(实机窗口外 60% vs 48%)
    stats = _pool_stats(available)
    if stats is not None:
        scored = []
        for item in near:
            f = _shape_features(item[2])
            z = 0.0 if f is None else sum(
                w * (v - mean) / std
                for w, v, (mean, std) in zip(_WEIGHTS, f, stats))
            scored.append((z, item))
        weights = [math.exp(s) for s, _ in scored]
        tid, _, pts, total = random.choices(scored, weights=weights, k=1)[0][1]
    else:
        tid, _, pts, total = random.choice(near)

    k = wanted / total
    if k < 1.0 / 1.25:
        # 源轨迹远长于目标: 截前缀而不是整体压扁长手势
        points = _clip_prefix(pts, float(wanted))
    else:
        points = [[round(dx * k, 2), dy, dt] for dx, dy, dt in pts]
        points[0] = [0.0, 0.0, 0.0]
    if y_gain != 1.0:
        # Y 抖动随 ~1/dpr 放大(真人抖动是物理尺度的); 时间轴不动
        points = [[p[0], round(float(p[1]) * y_gain, 2), p[2]] for p in points]
    result = build_waypoints(points, max_points, probe_dx, target)
    used.add(tid)
    return result


def build_waypoints(points, max_points=14, probe_dx=8.0, target_distance=None):
    """将 [dx, dy, dt_ms] 增量流变为累计轨迹；与 shadow_solve 算法一致。"""
    if not isinstance(max_points, int) or max_points < 1:
        raise ValueError("max_points must be a positive integer")
    rows = [tuple(float(v) for v in row) for row in points]
    if len(rows) < 2 or any(len(row) != 3 for row in rows):
        raise ValueError("expected origin followed by dx/dy/dt rows")
    if any(not math.isfinite(v) for row in rows for v in row):
        raise ValueError("trajectory must contain finite values")
    if rows[0] != (0.0, 0.0, 0.0) or any(row[2] < 0 for row in rows):
        raise ValueError("expected zero origin and nonnegative time increments")
    total_x = math.fsum(row[0] for row in rows[1:])
    target = total_x if target_distance is None else float(target_distance)
    probe = float(probe_dx)
    if not math.isfinite(target) or not math.isfinite(probe) or abs(total_x) < 1e-9:
        raise ValueError("invalid target, probe or zero displacement")
    if target <= probe or probe < 0:
        raise ValueError("rightward target must exceed nonnegative probe")
    scale = (target - probe) / total_x
    cumulative = []
    x = y = elapsed = 0.0
    for dx, dy, dt in rows[1:]:
        x += dx
        y += dy
        elapsed += dt
        cumulative.append((probe + x * scale, y, elapsed))
    count = len(cumulative)
    n = min(max_points, count)
    indices = [math.ceil((i + 1) * count / n) - 1 for i in range(n)]
    result = [cumulative[i] for i in indices]
    result[-1] = (target, result[-1][1], result[-1][2])
    return result


def _ms_precision(on):
    """Windows 下把系统计时粒度临时提到 1ms(回放期间开启, 结束关闭)。

    time.sleep 默认粒度约 15.6ms, 会把 5~30ms 的航点间隔全部拖偏;
    风控测的事件间隔会呈 15ms 量化。非 Windows 平台为空操作。
    """
    if os.name != 'nt':
        return
    try:
        (windll.winmm.timeBeginPeriod if on else windll.winmm.timeEndPeriod)(1)
    except Exception:
        pass


def _approach_points(x0, y0, x1, y1):
    """人味接近路径: 二次贝塞尔轻微弧线 + 每点抖动 + 减速接近。

    从 (x0,y0)(上一个已知鼠标位置) 滑向按钮 (x1,y1), 16~24 点,
    300~500ms, 前快后慢(t**0.85), 中途点加 ±1.2px 抖动。
    返回 [(x, y, elapsed_ms), ...], 末点精确落在 (x1,y1)。
    """
    dur = random.uniform(0.30, 0.50) * 1000.0
    n = random.randint(16, 24)
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    dist = math.hypot(x1 - x0, y1 - y0) or 1.0
    nx, ny = -(y1 - y0) / dist, (x1 - x0) / dist
    off = random.uniform(-0.12, 0.12) * dist
    cx, cy = mx + nx * off, my + ny * off
    pts = []
    for i in range(1, n + 1):
        t = i / n
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
        if i < n:
            bx += random.uniform(-1.2, 1.2)
            by += random.uniform(-1.2, 1.2)
        pts.append((bx, by, (t ** 0.85) * dur))
    pts[-1] = (float(x1), float(y1), pts[-1][2])
    return pts


def drag(drag_ele, distance: int, y_gain=1.0):
    """按物理像素距离回放真人采样点；移动全程使用影刀 win32。

    False/True 尺寸比换算距离，保留完整采样点；timeBeginPeriod(1)+忙等
    对齐累计时刻再 instant 移动，避免引擎二次插值；重复整数坐标只等待，
    不再次发送。抓取点在按钮内随机偏移, 按下/松手停留随机化(60~120/
    80~200ms), 有上一鼠标位置时先走贝塞尔接近路径再按下。
    y_gain: 当前页面 dpr 的 Y 抖动补偿, 由 handle_captcha 查实测标定表传入。
    """
    def move(x, y, speed="instant"):
        global _last_move_target
        target = (int(x), int(y))
        if target != _last_move_target:
            # SDK 可能先完成移动再抛异常；保留已发送目标避免重复坐标。
            _last_move_target = target
            win32.mouse_move(*target, relative_to="screen",
                             move_speed=speed, delay_after=0)

    def wait_until(deadline):
        # 先睡到 deadline 前 5ms 再忙等, 逐点误差从 ±15.6ms 压到亚毫秒
        wait = deadline - time.perf_counter()
        if wait > 0.006:
            time.sleep(wait - 0.005)
        while time.perf_counter() < deadline:
            pass

    physical = tuple(drag_ele.get_bounding(to96dpi=False))
    logical = tuple(drag_ele.get_bounding(to96dpi=True))
    if (not all(math.isfinite(v) for v in physical + logical)
            or min(physical[2], physical[3], logical[2], logical[3]) <= 0):
        raise ValueError("拖动元素边界无效")
    x, y, width, height = logical
    # 抓取点: 按钮中心 ±20%/±15% 抖动(比例无单位, 跨分辨率一致),
    # 真人不会每次都点正中心
    start_x = int(x + width / 2 + random.uniform(-0.2, 0.2) * width)
    start_y = int(y + height / 2 + random.uniform(-0.15, 0.15) * height)
    scale_x = physical[2] / width

    db_path = package.resources.get_path("dy-database.db")
    distance = float(distance)
    sdk_distance = distance / scale_x
    points = generate_trajectory(sdk_distance, db_path=db_path, max_points=10000,
                                 probe_dx=0.0, y_gain=y_gain)
    source_ms = points[-1][2]
    press_hold = random.uniform(0.06, 0.12)
    settle = random.uniform(0.08, 0.20)
    report = {"planned_physical_dx": distance, "planned_sdk_dx": sdk_distance,
              "bounds_scale_x": scale_x, "waypoints": len(points), "replay": "original_samples",
              "y_gain": y_gain, "grab": [start_x, start_y],
              "press_hold_ms": round(press_hold * 1000, 1),
              "settle_ms": round(settle * 1000, 1),
              "source_duration_ms": source_ms, "planned_replay_ms": source_ms}
    xbot.logging.info("Drag plan:" + json.dumps(report))

    held = False
    _ms_precision(True)
    try:
        # 接近路径: 有上一鼠标位置且距离足够时走贝塞尔弧线滑入(真人
        # 不会瞬移到按钮上); 否则退回直接定位, 相同起点先偏移 1px 再复位。
        prev = _last_move_target
        if (prev is not None and prev != (start_x, start_y)
                and math.hypot(start_x - prev[0], start_y - prev[1]) >= 20):
            ap_start = time.perf_counter()
            for ax, ay, ems in _approach_points(prev[0], prev[1], start_x, start_y):
                wait_until(ap_start + ems / 1000.0)
                move(ax, ay)
        else:
            if prev == (start_x, start_y):
                move(start_x + 1, start_y, "fast")
            move(start_x, start_y, "fast")
        time.sleep(0.15)
        before_x = drag_ele.get_bounding(to96dpi=True)[0]
        before_physical_x = drag_ele.get_bounding(to96dpi=False)[0]
        if not all(math.isfinite(v) for v in (before_x, before_physical_x)):
            raise ValueError("拖动前滑块位置无效")
        held = True  # SDK 可能在实际按下之后抛错，也要尝试松手。
        win32.mouse_click(button="left", click_type="down", delay_after=0)
        pressed_at = time.perf_counter()
        time.sleep(press_hold)

        started = time.perf_counter()
        max_lateness = 0.0
        for dx, dy, elapsed_ms in points:
            deadline = started + elapsed_ms / 1000.0
            wait_until(deadline)
            max_lateness = max(max_lateness, (time.perf_counter() - deadline) * 1000)
            move(start_x + dx, start_y + dy)
        # 给页面一小段跟随时间；这里只测按钮，不代表上方拼块已对齐。
        time.sleep(settle)
        final_physical_x = drag_ele.get_bounding(to96dpi=False)[0]
        if not math.isfinite(final_physical_x):
            raise RuntimeError("无法读取松手前的拖动按钮位置")
        report["actual_handle_physical_dx"] = final_physical_x - before_physical_x
        report["handle_error_physical_px"] = distance - report["actual_handle_physical_dx"]
        report["actual_replay_ms"] = (time.perf_counter() - started) * 1000.0
        report["held_ms"] = (time.perf_counter() - pressed_at) * 1000.0
        report["max_lateness_ms"] = round(max_lateness, 2)
        xbot.logging.info("Drag end:" + json.dumps(report))
    finally:
        if held:
            win32.mouse_click(button="left", click_type="up", delay_after=0)
        _ms_precision(False)
    return report


def yd_captcha_recognition(payload: dict):
    """使用增值服务请求验证码"""
    payload = dict(payload)
    captcha_type = payload.pop("type")

    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc, timeout=20)
    res_payload = json.dumps({
        "thirdPartyInterfaceCode": f"jfbym_{captcha_type}",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": payload,
            "pathVariable": {}
        },
        "bizType": "rpa-command"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        conn.request("POST", "/api/openapi/v2/thirdParty/interface/call",
                     res_payload, headers)
        res = conn.getresponse()
        response_data = res.read().decode('utf-8')
        if res.status != 200:
            raise RuntimeError(f"影刀识别服务 HTTP {res.status}")
        response_json = json.loads(response_data)
    finally:
        conn.close()
    data = response_json.get("data")
    if not data:
        raise RuntimeError("影刀识别服务未返回有效数据")
    return data


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com", timeout=20)
    headers = {'Content-Type': 'application/json'}
    data_json = json.dumps(payload)
    try:
        conn.request("POST", "/api/YmServer/customApi",
                     body=data_json, headers=headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        if response.status != 200:
            raise RuntimeError(f"云码识别服务 HTTP {response.status}")
        response_json = json.loads(response_data)
    finally:
        conn.close()
    return response_json


def handle_captcha(web_page: xbot.web.WebBrowser,
                   background_ele,
                   drag_ele,
                   retry_count: int = 5,
                   offset=0,
                   token="",
                   refresh_ele=None,
                   recognition_kind="distance",
                   piece_ele=None):
    """20225 默认返回截图中的滑动距离；offset 使用物理屏幕像素。

    仅显式 gap_left 模式向服务传 extra=true，并减去拼块初始左边界。
    返回 challenge_closed 只表示背景稳定消失，不代表读取了服务器成功码。
    每轮拖动前自动读取页面 devicePixelRatio, 按 2026-10-11 实机标定表
    计算 Y 抖动补偿(y_gain) 传给 drag; 读取失败按不补偿回放, 不阻断流程。
    """
    retry_count = 5 if retry_count is None else int(retry_count)
    offset = 0.0 if offset is None else float(offset)
    if retry_count < 1 or not math.isfinite(offset):
        raise ValueError("retry_count 必须为正数，offset 必须为有限数值")
    if recognition_kind not in ("distance", "gap_left"):
        raise ValueError("recognition_kind 只支持 distance 或 gap_left")
    if recognition_kind == "gap_left" and piece_ele is None:
        raise ValueError("gap_left 模式必须提供实际拼块的 piece_ele")
    cache_folder = ""
    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
    os.makedirs(cache_folder, exist_ok=True)
    xbot.logging.info(f"Cache Dir:{cache_folder}")

    def capture_stable(save_path):
        deadline = time.monotonic() + 5.0
        previous, stable_count = None, 0
        while time.monotonic() < deadline:
            box = tuple(float(v) for v in web_page.find(background_ele).get_bounding(to96dpi=False))
            if len(box) != 4 or not all(math.isfinite(v) for v in box) or min(box[2:]) <= 0:
                raise RuntimeError("验证码背景边界无效")
            x, y, width, height = box
            left, top, right, bottom = map(round, (x, y, x + width, y + height))
            if right <= left or bottom <= top:
                raise RuntimeError("验证码截图区域为空")
            win32.screenshot.save_screen_to_file(save_path, "png", left, top, right, bottom)
            with Image.open(save_path) as image:
                image_size = image.size
                signature = ((left, top, right, bottom), image_size, image.convert("RGB").tobytes())
            stable_count = stable_count + 1 if signature == previous else 0
            if stable_count >= 2:
                return (left, top, right - left, bottom - top), image_size
            previous = signature
            time.sleep(0.2)
        raise RuntimeError("验证码截图在 5 秒内未稳定，未提交识别或拖动")


    for i in range(retry_count):
        save_path = os.path.join(cache_folder, f"dy_slider_{time.time_ns()}_{i + 1}_before.png")
        background_box, image_size = capture_stable(save_path)
        ready_at = time.monotonic()
        pixel_scale = background_box[2] / image_size[0]
        piece_left = None
        if recognition_kind == "gap_left":
            piece_left = float(web_page.find(piece_ele).get_bounding(to96dpi=False)[0])
            if not math.isfinite(piece_left):
                raise RuntimeError("拼块初始位置无效")
        background_ele_base64 = file2base64(save_path)
        captcha_code = "20225"
        payload = {
            "image": background_ele_base64,
            'token': token,
            'type': captcha_code
        }
        if recognition_kind == "gap_left":
            payload["extra"] = "true"

        if token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)

        if not isinstance(data, dict) or data.get("msg") != "识别成功":
            raise RuntimeError("识别服务未返回成功结果，未拖动")
        try:
            recognized_px = float(data["data"]["data"])
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError("识别服务未返回有效距离数值，未拖动") from error
        distance = recognized_px * pixel_scale + offset
        if recognition_kind == "gap_left":
            distance += background_box[0] - piece_left
        if not math.isfinite(distance) or distance <= 0:
            raise RuntimeError("换算后的拖动距离无效，未拖动")

        # 每轮读取页面 dpr 并查实测标定表; 失败按不补偿回放, 不阻断流程。
        # 注意: execute_javascript 只接受函数形式, 字符串 "return ..."
        # 会报 eval function failed(此前被 except 静默吞掉, y_gain 恒为 1)。
        try:
            dpr = float(web_page.execute_javascript(
                "function(e,a){return window.devicePixelRatio;}"))
            y_gain = y_gain_for_dpr(dpr)
        except Exception:
            dpr, y_gain = None, 1.0

        report = {"attempt": i + 1, "before_image": save_path,
                  "image_width": image_size[0], "image_height": image_size[1],
                  "capture_width_physical": background_box[2],
                  "recognition_px": recognized_px, "image_to_physical_scale": pixel_scale,
                  "planned_physical_dx": distance, "dpr": dpr, "y_gain": y_gain}
        xbot.logging.info("Captcha geometry:" + json.dumps(report))
        # 识别服务很快返回时，也留出页面展示及输入准备时间。
        time.sleep(max(0.0, 1.0 - (time.monotonic() - ready_at)))
        report["drag"] = drag(web_page.find(drag_ele), distance, y_gain=y_gain)

        sleep(3)

        visible = xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele)


        if not visible:
            return

        if i + 1 < retry_count:
            if not refresh_ele:
                raise RuntimeError("未确认通过且未提供刷新元素，停止重复提交同一挑战")
            time.sleep(1.0)
            # 移动到刷新按钮内部的随机位置，避开边缘后点击。
            x, y, width, height = web_page.find(refresh_ele).get_bounding(to96dpi=True)
            win32.mouse_move(int(x + width * random.uniform(0.2, 0.8)),
                             int(y + height * random.uniform(0.2, 0.8)),
                             relative_to="screen", move_speed="middle", delay_after=0.1)
            win32.mouse_click(button="left", delay_after=0)
            time.sleep(0.8)
    raise RuntimeError(f"已完成 {retry_count} 次拖动，但验证码背景未稳定消失；查看 before 截图和 Drag end 日志")

def select_ele(xpath, web_page):
    if "frame" in xpath:
            xpaths = xpath.split(">>")
            data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
            selector = Selector(data)
            return selector
    else:
        data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [xpath]}}
        selector = Selector(data)
        return selector



def test_func():
    """仅供手动调用的固定页面示例；main(args) 不调用此函数。"""
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active("chrome")
    background_ele = select_ele('//iframe>>//img[@class="captcha-verify-image"]', web_page)
    slider_ele = select_ele('//iframe>>//div[@class="captcha-slider-btn"]', web_page)
    refresh_ele = select_ele('//iframe>>//div[@class="vc-captcha-refresh"]', web_page)
    retry_count = 5
    offset = 0
    token = ''
    handle_captcha(web_page, background_ele, slider_ele, retry_count, offset, token, refresh_ele)
    exit()


def main(args):
    test_func()

    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    token = args.get("token")
    refresh_ele = args.get("refresh_ele")

    # web_page = web.get_active(mode='chrome')
    # background_ele = "std_slider_captcha_background"
    # slider_ele = "std_slider_captcha_drag"
    # refresh_ele = "std_slider_refresh_ele"
    # retry_count = 5
    # offset = 0

    handle_captcha(web_page, background_ele, slider_ele, retry_count, offset, token, refresh_ele)
