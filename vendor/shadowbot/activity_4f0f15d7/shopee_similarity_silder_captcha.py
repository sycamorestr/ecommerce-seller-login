# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

# 改进点：
#   a) 剔除"匹配框越出背景"的角度（缺口不可能半截在画面外）；
#   b) 对峰值做抛物线插值，角度细化到亚度，拖拽更准；
#   c) 计算"暗度比"（缺口通常比照片暗，>1 才像真缺口）与交叉验证，
#      并把可信度打日志，真机跑时可据此判断是否需要重试。

import os
import sys
import platform
import base64
import json
import math
import random
import sqlite3
import ast
import xbot
import xbot_visual
from xbot import sleep, win32, web, print
from xbot.web.element import WebElement
from xbot.selector import Selector
from .package import variables as glv
import numpy as np
import cv2
from .utils import get_ppi, _moveTo

# Shopee 旋转拼图常量：滑块 dx 与拼图旋转角线性耦合
DEG_PER_PX = 0.9
# 滑块行程可达到的最大角度（超过则物理上不可达）
MAX_THETA = 204

# 使用platform模块来判断架构类型
machine = platform.machine().lower()
if 'x86_64' in machine or 'amd64' in machine:
    arch = 'x64'
elif 'aarch64' in machine or 'arm64' in machine:
    arch = 'arm64'
else:
    arch = 'x64'

# 设置PYTHONPATH
base_path = os.path.dirname(os.path.dirname(os.environ.get('PYTHONPATH', os.path.abspath(__file__))))
cv_engine_path = os.path.join(base_path, f"support_{arch}/cv-engine/site-packages")
if os.path.exists(cv_engine_path):
    sys.path.append(cv_engine_path)


def decode_data_uri(data_uri: str):
    """将 base64 data URI 解码为 OpenCV 图像（保留 alpha 通道）"""
    _, encoded = data_uri.split(",", 1)
    raw = base64.b64decode(encoded)
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)


def _get_image_src(web_page: xbot.web.WebBrowser, ele):
    """提取图片 data URI，优先 src 属性，失败则从 canvas 截取"""
    el = web_page.find(ele)
    src = el.get_attribute("src")
    if src:
        return src
    # src 不存在，尝试 canvas toDataURL
    w = el.get_attribute("width")
    h = el.get_attribute("height")
    if not w or not h:
        return None
    return web_page.execute_javascript(
        "function(element, args) {"
        "  var d = JSON.parse(args);"
        "  var c = document.querySelector('canvas[width=\"' + d[0] + '\"][height=\"' + d[1] + '\"]');"
        "  if (!c) return null;"
        "  return c.toDataURL('image/png');"
        "}",
        json.dumps([w, h])
    )


def get_captcha_images(web_page: xbot.web.WebBrowser, bg_ele, piece_ele):
    """提取验证码的背景图和拼图块（保留 alpha 通道）"""
    bg_src = _get_image_src(web_page, bg_ele)
    piece_src = _get_image_src(web_page, piece_ele)
    if not bg_src or not piece_src:
        return None, None
    bg = decode_data_uri(bg_src)
    piece = decode_data_uri(piece_src)
    return bg, piece


def _piece_mask(piece: np.ndarray) -> np.ndarray:
    """取拼图块 alpha 遮罩作为"缺口形状"模板"""
    if piece.ndim == 3 and piece.shape[2] == 4:
        return (piece[:, :, 3] > 128).astype(np.uint8)
    gray = cv2.cvtColor(piece, cv2.COLOR_BGR2GRAY)
    return (gray > 128).astype(np.uint8)


def _darkness_map(bg: np.ndarray, local_anomaly: bool = False) -> np.ndarray:
    """背景暗度图：越暗值越大。

    local_anomaly=False：255-灰度 + 3x3 平滑（与原实现一致）。
    local_anomaly=True：只取"比邻域更暗"的局部异常，对整体偏暗的照片更稳。
    """
    gray = cv2.cvtColor(bg[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
    dark = 255.0 - gray
    if local_anomaly:
        base = cv2.GaussianBlur(dark, (31, 31), 0)
        dark = np.clip(dark - base, 0, None)
    return cv2.GaussianBlur(dark, (3, 3), 0)


def _edge_response(bg: np.ndarray) -> np.ndarray:
    """把背景边缘转换成连续响应图，距离边缘越近分数越高。"""
    gray = cv2.cvtColor(bg[:, :, :3], cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gray, 30, 100)
    distance = cv2.distanceTransform(255 - edges, cv2.DIST_L2, 3)
    return np.exp(-distance / 2.0).astype(np.float32)


def _rank_curve(values: dict) -> dict:
    """把不同匹配图的分数转换到相同的 0..1 稳健排名区间。"""
    if not values:
        return {}
    keys = list(values)
    arr = np.asarray([values[k] for k in keys], dtype=np.float32)
    valid = arr[np.isfinite(arr) & (arr >= -0.5)]
    if len(valid) == 0:
        return {k: 0.0 for k in keys}
    low, high = np.percentile(valid, [10, 90])
    scale = max(float(high - low), 1e-6)
    return {k: float(np.clip((values[k] - low) / scale, 0.0, 1.0)) for k in keys}


def _find_target_region(bg: np.ndarray, piece: np.ndarray):
    """从背景边缘中找出最像目标凹槽的区域。

    返回 (score, bbox, target_contour, piece_contour, candidates)，供位置和角度先验共用。
    """
    gray = cv2.cvtColor(bg[:, :, :3], cv2.COLOR_BGR2GRAY)
    mask = _piece_mask(piece)
    piece_contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    if not piece_contours:
        return None
    piece_contour = max(piece_contours, key=cv2.contourArea)
    _, _, piece_w, piece_h = cv2.boundingRect(piece_contour)
    piece_area = max(piece_w * piece_h, 1)

    edges = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), 0), 25, 90)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
    )
    hierarchy = hierarchy[0] if hierarchy is not None else []
    candidates = []
    H, W = gray.shape
    for index, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        x, y, width, height = cv2.boundingRect(contour)
        ratio = (width * height) / float(piece_area)
        if (
            area < 100
            or width < 12
            or height < 10
            or x < 3
            or y < 3
            or x + width > W - 3
            or y + height > H - 3
            or ratio < 0.35
            or ratio > 4.5
        ):
            continue

        shape_error = float(
            cv2.matchShapes(piece_contour, contour, cv2.CONTOURS_MATCH_I1, 0)
        )
        shape_score = math.exp(-min(shape_error, 4.0) / 1.5)
        size_score = math.exp(-abs(math.log(max(ratio, 1e-6))) / 0.7)
        # 轮廓明显比拼图大、且形状又不像时，通常是整件物体的外轮廓。
        if ratio > 2.5 and shape_score < 0.5:
            size_score *= 0.45
        center_score = math.exp(
            -(
                ((x + width / 2 - W / 2) / (W / 2)) ** 2
                + ((y + height / 2 - H / 2) / (H / 2)) ** 2
            )
            / 2.0
        )
        child = int(hierarchy[index][2]) if len(hierarchy) else -1
        parent = int(hierarchy[index][3]) if len(hierarchy) else -1
        nested_score = (
            0.80 if child >= 0 and ratio <= 2.5
            else (0.05 if parent >= 0 else 0.0)
        )
        border_penalty = 0.6 if y < 18 else 1.0
        score = border_penalty * (
            0.30 * size_score
            + 0.25 * center_score
            + 0.15 * shape_score
            + 0.30 * nested_score
        )
        candidates.append((score, (x, y, width, height), contour))

    if not candidates:
        return None
    ordered = sorted(candidates, key=lambda item: item[0], reverse=True)
    best = ordered[0]
    return best[0], best[1], best[2], piece_contour, ordered[:8]


def _axis_angle(contour):
    """返回轮廓主轴角度（0..180），用于给旋转搜索提供稳定先验。"""
    if contour is None or len(contour) < 5:
        return None
    (_, _), (width, height), angle = cv2.minAreaRect(contour)
    if width < height:
        angle += 90.0
    return float(angle % 180.0)


def _find_salient_region(bg: np.ndarray, piece: np.ndarray):
    """闭合凹槽找不到时，用低阈值边缘提取一个显著目标作为回退。"""
    gray = cv2.cvtColor(bg[:, :, :3], cv2.COLOR_BGR2GRAY)
    mask = _piece_mask(piece)
    piece_contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    if not piece_contours:
        return None
    piece_contour = max(piece_contours, key=cv2.contourArea)
    _, _, piece_w, piece_h = cv2.boundingRect(piece_contour)
    piece_area = max(piece_w * piece_h, 1)

    edges = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), 0), 15, 70)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    # 深色场景里目标边缘可能与地面连成一片，补充高亮前景的独立轮廓。
    bright = (gray > np.percentile(gray, 75)).astype(np.uint8) * 255
    bright = cv2.dilate(bright, np.ones((3, 3), np.uint8))
    bright_contours, _ = cv2.findContours(
        bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    contours = list(contours) + list(bright_contours)
    H, W = gray.shape
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, width, height = cv2.boundingRect(contour)
        ratio = (width * height) / float(piece_area)
        if (
            area < 120
            or width < 10
            or height < 10
            or ratio < 0.45
            or ratio > 5.5
            or width > W * 0.70
            or height > H * 0.85
            or x < 3
            or y < 3
        ):
            continue
        shape_error = float(
            cv2.matchShapes(piece_contour, contour, cv2.CONTOURS_MATCH_I1, 0)
        )
        shape_score = math.exp(-min(shape_error, 5.0) / 2.0)
        size_score = math.exp(-abs(math.log(max(ratio, 1e-6))) / 0.9)
        compact_score = min(area / max(width * height, 1), 1.0)
        center_score = math.exp(
            -(
                ((x + width / 2 - W / 2) / (W / 2)) ** 2
                + ((y + height / 2 - H / 2) / (H / 2)) ** 2
            )
            / 2.0
        )
        score = (
            0.35 * size_score
            + 0.30 * shape_score
            + 0.20 * compact_score
            + 0.15 * center_score
        )
        candidates.append((score, (x, y, width, height), contour))
    if not candidates:
        return None
    best = max(candidates, key=lambda item: item[0])
    return best[0], best[1], best[2], piece_contour


def _region_edge_score(edge: np.ndarray, tmpl: np.ndarray, region):
    """在候选目标区域中心评估旋转模板轮廓的贴合程度。"""
    x, y, width, height = region
    boundary = cv2.morphologyEx(
        tmpl.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)
    )
    ys, xs = np.where(boundary > 0)
    if len(xs) < 20:
        return -1.0, (0, 0)
    bx = int(round(x + width / 2 - tmpl.shape[1] / 2))
    by = int(round(y + height / 2 - tmpl.shape[0] / 2))
    px = bx + xs
    py = by + ys
    valid = (px >= 0) & (px < edge.shape[1]) & (py >= 0) & (py < edge.shape[0])
    if valid.sum() < len(xs) * 0.8:
        return -1.0, (0, 0)
    return float(edge[py[valid], px[valid]].mean()), (bx, by)


def _rotated_template(mask: np.ndarray, theta: float):
    """旋转拼图遮罩，取有效区域外接框作模板；返回 (模板, 框左上角偏移)"""
    ph, pw = mask.shape
    m = cv2.getRotationMatrix2D((pw / 2, ph / 2), -theta, 1.0)
    ra = cv2.warpAffine(mask, m, (pw, ph), flags=cv2.INTER_NEAREST, borderValue=0)
    ys, xs = np.where(ra > 0)
    if len(xs) < 50:
        return None, None
    return (ra[ys.min():ys.max() + 1, xs.min():xs.max() + 1] > 0).astype(np.float32), \
        (ys.min(), xs.min())


def _refine_theta(curve: dict, peak_theta: int) -> float:
    """对峰值做抛物线插值，把 1° 分辨率细化到亚度"""
    prev = curve.get(peak_theta - 1)
    next_ = curve.get(peak_theta + 1)
    peak = curve.get(peak_theta)
    if prev is None or next_ is None or peak is None:
        return float(peak_theta)
    denom = prev - 2.0 * peak + next_
    if abs(denom) < 1e-9:
        return float(peak_theta)
    delta = 0.5 * (prev - next_) / denom
    return float(peak_theta + max(-0.5, min(0.5, delta)))


def _relative_darkness(bg: np.ndarray, piece: np.ndarray, theta: float,
                       maxloc: tuple) -> float:
    """匹配框内"拼图覆盖区域"平均暗度 / 全图平均暗度。

    真实缺口通常比照片暗（>1）；<1 说明匹配到的可能是亮区，可疑。
    """
    gray = cv2.cvtColor(bg[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
    dark = 255.0 - gray
    H, W = gray.shape
    mask = _piece_mask(piece)
    tmpl, (ty, tx) = _rotated_template(mask, theta)
    if tmpl is None:
        return 0.0
    th, tw = tmpl.shape
    bx, by = int(maxloc[0]) - tx, int(maxloc[1]) - ty
    if bx < 0 or by < 0 or bx + tw > W or by + th > H or tmpl.sum() < 1:
        return 0.0
    region = dark[by:by + th, bx:bx + tw]
    under = float((region * tmpl).sum() / tmpl.sum())
    return round(under / max(float(dark.mean()), 1e-6), 2)


def _cross_check(bg: np.ndarray, piece: np.ndarray, theta_primary: int,
                 tol: int = 15):
    """用两条独立线索交叉验证主结果，返回同意的条数（0..2）。"""
    agree = 0
    # 线索1：局部暗度异常图
    (t2, _, _), _ = detect_angle(bg, piece, local_anomaly=True, return_curve=True)
    if abs(t2 - theta_primary) <= tol:
        agree += 1
    # 线索2：边缘距离图（模板只用外缘而非整块填充）
    mask = _piece_mask(piece)
    gray = cv2.cvtColor(bg[:, :, :3], cv2.COLOR_BGR2GRAY)
    H, W = gray.shape
    mp = _edge_response(bg)
    best = (0, -1.0)
    for theta in range(0, MAX_THETA + 1):
        tmpl, (ty, tx) = _rotated_template(mask, theta)
        if tmpl is None:
            continue
        th, tw = tmpl.shape
        if th >= H or tw >= W:
            continue
        k = np.ones((3, 3), np.uint8)
        out = (cv2.dilate(tmpl, k) - tmpl > 0).astype(np.float32)
        res = cv2.matchTemplate(mp, out, cv2.TM_CCORR)
        res /= max(float(out.sum()), 1.0)
        res[~np.isfinite(res)] = -1.0
        _, mx, _, maxloc = cv2.minMaxLoc(res)
        bx, by = maxloc[0] - tx, maxloc[1] - ty
        if bx < 0 or by < 0 or bx + tw > W or by + th > H:
            continue
        if mx > best[1]:
            best = (theta, float(mx))
    if abs(best[0] - theta_primary) <= tol:
        agree += 1
    return agree, best[0]


def detect_angle(bg: np.ndarray, piece: np.ndarray, local_anomaly: bool = False,
                 return_curve: bool = False):
    """
    目标区域约束下的轮廓-暗度匹配，搜索最佳旋转角度。
    先从背景的嵌套边缘中定位凹槽，再在该区域内用拼图轮廓、主轴和暗度联合选角。
    返回 (theta, score[, maxloc, curve])，theta 单位为度（0..MAX_THETA）。
    会剔除"匹配框越出背景"的角度。
    """
    mask = _piece_mask(piece)
    dark = _darkness_map(bg, local_anomaly)
    local_dark = _darkness_map(bg, not local_anomaly)
    edge = _edge_response(bg)
    H, W = dark.shape

    edge_scores = {}
    fill_scores = {}
    local_scores = {}
    region_scores = {}
    region_locations = {}
    locations = {}
    target_info = _find_target_region(bg, piece)
    if target_info is None:
        fallback_info = _find_salient_region(bg, piece)
        if (
            fallback_info is not None
            and fallback_info[0] >= 0.33
            and cv2.contourArea(fallback_info[2]) >= 500
        ):
            target_info = fallback_info
    target_region = target_info[1] if target_info is not None else None
    region_candidates = []
    if target_info is not None:
        if len(target_info) >= 5:
            region_candidates = target_info[4]
        else:
            region_candidates = [
                (target_info[0], target_info[1], target_info[2])
            ]
    piece_axis = _axis_angle(target_info[3]) if target_info is not None else None
    orientation_target = None
    if target_info is not None and piece_axis is not None:
        target_axis = _axis_angle(target_info[2])
        if target_axis is not None:
            orientation_target = (target_axis - piece_axis) % 180.0
    orientation_dominant = False
    if target_info is not None:
        _, _, piece_box_w, piece_box_h = cv2.boundingRect(target_info[3])
        target_box_w, target_box_h = target_info[1][2:]
        orientation_dominant = (
            min(piece_box_w, piece_box_h) / max(piece_box_w, piece_box_h, 1)
            < 0.45
            and target_box_w * target_box_h
            / max(piece_box_w * piece_box_h, 1) > 3.0
        )
    if orientation_dominant and region_candidates:
        # 细长侧视拼图通常对应整件物体的主轴，旁边的局部边缘会产生错误周期。
        region_candidates = region_candidates[:1]
    orientation_scores = {}
    for theta in range(0, MAX_THETA + 1, 1):
        tmpl, (ty, tx) = _rotated_template(mask, theta)
        if tmpl is None:
            continue
        th, tw = tmpl.shape
        if th >= H or tw >= W:
            continue
        # 缺口的形状主要体现在轮廓，填充暗度只作为辅助线索。
        boundary = cv2.morphologyEx(
            tmpl.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)
        ).astype(np.float32)
        edge_res = cv2.matchTemplate(edge, boundary, cv2.TM_CCORR)
        edge_res /= max(float(boundary.sum()), 1.0)
        fill_res = cv2.matchTemplate(dark, tmpl, cv2.TM_CCOEFF_NORMED)
        local_res = cv2.matchTemplate(local_dark, tmpl, cv2.TM_CCOEFF_NORMED)
        edge_res[~np.isfinite(edge_res)] = -1.0
        fill_res[~np.isfinite(fill_res)] = -1.0
        local_res[~np.isfinite(local_res)] = -1.0
        _, edge_score, _, edge_loc = cv2.minMaxLoc(edge_res)
        _, fill_score, _, fill_loc = cv2.minMaxLoc(fill_res)
        _, local_score, _, _ = cv2.minMaxLoc(local_res)

        # 目标凹槽已经由背景轮廓锁定，角度评分优先在该区域内进行。
        region_score, region_top_left = (-1.0, (0, 0))
        region_orientation = 0.0
        if region_candidates:
            best_candidate_fit = -1.0
            best_candidate_location = (0, 0)
            best_candidate_orientation = 0.0
            best_candidate_score = max(float(region_candidates[0][0]), 1e-6)
            for candidate_score, candidate_bbox, candidate_contour in region_candidates:
                candidate_edge, candidate_location = _region_edge_score(
                    edge, tmpl, candidate_bbox
                )
                candidate_weight = float(
                    np.clip(candidate_score / best_candidate_score, 0.35, 1.0)
                )
                candidate_orientation = 0.0
                target_axis = _axis_angle(candidate_contour)
                if piece_axis is not None and target_axis is not None:
                    prior = (target_axis - piece_axis) % 180.0
                    distances = [
                        abs(float(theta) - prior),
                        abs(float(theta) - prior - 180.0),
                        abs(float(theta) - prior + 180.0),
                    ]
                    candidate_orientation = math.exp(-min(distances) / 22.0)
                _, _, piece_box_w, piece_box_h = cv2.boundingRect(target_info[3])
                oversized_thin = (
                    piece_box_w > 0
                    and piece_box_h > 0
                    and min(piece_box_w, piece_box_h)
                    / max(piece_box_w, piece_box_h) < 0.45
                    and candidate_bbox[2] * candidate_bbox[3]
                    / max(piece_box_w * piece_box_h, 1) > 3.0
                )
                if oversized_thin:
                    edge_weight, orientation_weight, candidate_weighting = (
                        0.20, 0.55, 0.25
                    )
                else:
                    edge_weight, orientation_weight, candidate_weighting = (
                        0.40, 0.20, 0.40
                    )
                candidate_fit = (
                    edge_weight * candidate_edge
                    + orientation_weight * candidate_orientation
                    + candidate_weighting * candidate_weight
                )
                if candidate_fit > best_candidate_fit:
                    best_candidate_fit = candidate_fit
                    best_candidate_location = candidate_location
                    best_candidate_orientation = candidate_orientation
            if best_candidate_fit >= 0.0:
                region_score = best_candidate_fit
                region_top_left = best_candidate_location
                region_orientation = best_candidate_orientation

        # 拒绝越界匹配框
        bx, by = edge_loc[0] - tx, edge_loc[1] - ty
        if bx < 0 or by < 0 or bx + tw > W or by + th > H:
            continue
        edge_scores[theta] = float(edge_score)
        fill_scores[theta] = float(fill_score)
        local_scores[theta] = float(local_score)
        if region_score >= 0.0:
            region_scores[theta] = float(region_score)
            # _relative_darkness 接收的是 matchTemplate 坐标，需要补回裁剪偏移。
            region_locations[theta] = (
                int(region_top_left[0] + tx),
                int(region_top_left[1] + ty),
            )
        if region_candidates:
            orientation_scores[theta] = region_orientation
        # 没有目标候选时保留全图匹配作为回退。
        locations[theta] = (int(fill_loc[0]), int(fill_loc[1]))

    region_rank = _rank_curve(region_scores)
    edge_rank = _rank_curve(edge_scores)
    fill_rank = _rank_curve(fill_scores)
    local_rank = _rank_curve(local_scores)
    orientation_rank = _rank_curve(orientation_scores)
    curve = {}
    raw_curve = {}
    for theta in edge_scores:
        if region_scores:
            # 位置候选存在时，角度必须与目标凹槽的边界一致。
            if orientation_dominant:
                curve[theta] = (
                    0.75 * orientation_rank.get(theta, 0.0)
                    + 0.15 * region_rank.get(theta, 0.0)
                    + 0.05 * edge_rank.get(theta, 0.0)
                    + 0.05 * fill_rank.get(theta, 0.0)
                )
                raw_curve[theta] = (
                    0.75 * orientation_scores.get(theta, 0.0)
                    + 0.15 * region_scores[theta]
                    + 0.05 * edge_scores[theta]
                    + 0.05 * fill_scores[theta]
                )
            else:
                curve[theta] = (
                    0.45 * orientation_rank.get(theta, 0.0)
                    + 0.30 * region_rank.get(theta, 0.0)
                    + 0.15 * edge_rank.get(theta, 0.0)
                    + 0.10 * fill_rank.get(theta, 0.0)
                )
                raw_curve[theta] = (
                    0.45 * orientation_scores.get(theta, 0.0)
                    + 0.30 * region_scores[theta]
                    + 0.15 * edge_scores[theta]
                    + 0.10 * fill_scores[theta]
                )
        else:
            # 轮廓占主权重；暗度和局部异常帮助照片纹理不明显时稳定选角。
            curve[theta] = (
                0.55 * edge_rank.get(theta, 0.0)
                + 0.30 * fill_rank.get(theta, 0.0)
                + 0.15 * local_rank.get(theta, 0.0)
            )
            raw_curve[theta] = (
                0.55 * edge_scores[theta]
                + 0.30 * fill_scores[theta]
                + 0.15 * local_scores[theta]
            )

    if not curve:
        best = (0, -1.0, (0, 0))
    else:
        if orientation_dominant and orientation_target is not None:
            theta = min(
                curve,
                key=lambda item: min(
                    abs(float(item) - orientation_target),
                    abs(float(item) - orientation_target - 180.0),
                    abs(float(item) - orientation_target + 180.0),
                ),
            )
        else:
            theta = max(curve, key=curve.get)
        best_location = region_locations.get(theta, locations[theta])
        best = (theta, float(raw_curve[theta]), best_location)
    if return_curve:
        return best, curve
    return best


def _get_drag_path_by_distance(distance: int):
    """按目标距离从资源库读取一条人类拖拽轨迹。"""
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="database.db")
    if distance <= 50:
        bucket = 50
    elif distance < 150:
        bucket = 100
    elif distance < 200:
        bucket = 150
    else:
        bucket = 200

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tracker WHERE distance = ?", (bucket,))
        rows = cursor.fetchall()

    if not rows:
        raise ValueError(f"database.db 中未找到距离 {bucket} 的轨迹数据")

    track = ast.literal_eval(random.choice(rows)[2])
    scale = float(distance) / float(bucket)
    result = []
    for offset_x, offset_y, duration in track:
        result.append([offset_x * scale, offset_y, duration])
    result[-1][0] = float(distance)
    return result


def ease_drag(web_page, drag_ele, target_dx):
    """使用资源库轨迹模拟人类拖拽。"""
    drag_element = web_page.find(drag_ele)
    x, y, width, height = drag_element.get_bounding(to96dpi=False)
    sx = int(x + width / 2)
    sy = int(y + height / 2)
    mouse_pos_path = _get_drag_path_by_distance(int(round(target_dx)))

    xbot.win32.manual_motion_on()
    _moveTo(sx, sy)
    sleep(0.1)
    win32.mouse_click(button="left", click_type="down", delay_after=0)

    try:
        for offset_x, offset_y, duration in mouse_pos_path:
            _moveTo(sx + int(offset_x), sy + int(offset_y))
            sleep(float(duration) / 2000)
        sleep(0.3)
    finally:
        win32.mouse_click(button="left", click_type="up")
        xbot.win32.manual_motion_off()


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    drag_ele: str,
    bg_ele: str,
    piece_ele: str,
    retry_count: int = 5,
    offset: int = 0,
    refresh_ele: str = "",
    wait_time: int = 2,
    min_score: float = 0.3,
    debug: bool = False
):
    """处理 Shopee 旋转拼图验证码"""
    for attempt_num in range(int(retry_count)):
        # 刷新验证码（首次也刷新以清除可能的错误状态）
        web_page.find(refresh_ele).click()
        sleep(wait_time)
        # 提取验证码图片
        bg, piece = get_captcha_images(web_page, bg_ele, piece_ele)
        if bg is None or piece is None:
            continue

        # 检测目标角度
        (theta, score, maxloc), curve = detect_angle(bg, piece, return_curve=True)
        if score < min_score:
            if debug:
                print(f"[captcha v2] 第{attempt_num + 1}次：分数过低({score:.2f} < {min_score})，跳过")
            continue

        # 角度细化 + 可信度诊断
        theta_ref = _refine_theta(curve, theta)
        target_dx = theta_ref / DEG_PER_PX + float(offset)
        rel_dark = _relative_darkness(bg, piece, theta_ref, maxloc)
        agree, other_theta = _cross_check(bg, piece, theta)

        if debug:
            verdict = "高" if (rel_dark >= 1.0 and agree >= 1) else ("中" if (rel_dark >= 1.0 or agree >= 1) else "低")
            print(f"[captcha v2] 第{attempt_num + 1}次：角度={theta_ref:.1f}° "
                  f"距离={target_dx:.1f}px 分数={score:.3f} "
                  f"暗度比={rel_dark:.2f} 交叉同意={agree}/2 判定={verdict}")
            if rel_dark < 1.0:
                print(f"[captcha v2] 警告：匹配区域比背景亮(暗度比<1)，可能不是真缺口，建议重试")

        # 缩放距离（CSS像素 → 物理像素）
        ppi = get_ppi()
        drag_distance = target_dx
        if os.name == "nt":
            drag_distance = int(drag_distance / ppi)
        else:
            drag_distance = int(drag_distance)

        # 执行拖拽
        ease_drag(web_page, drag_ele, drag_distance)
        sleep(2.5)

        # 检查验证码是否消失
        if web_page.is_element_displayed(drag_ele):
            _, _, w_val, h_val = web_page.find(drag_ele).get_bounding()
            if w_val == 0 and h_val == 0:
                return
        else:
            return


def test_func() -> None:
    if 'xbot_extensions' in __file__:
        return

    web_page = web.get_active('chrome')

    def select_ele(xpath):
        if "frame" in xpath:
            xpaths = xpath.split(">>")
            data = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple',
                    'xpath': {'enable': 'true', 'segments': xpaths}}
            return Selector(data)
        else:
            data = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple',
                    'xpath': {'enable': 'true', 'segments': [xpath]}}
            return Selector(data)

    # Shopee 三个元素 (drag_ele 同时用于拖拽和刷新按钮定位)
    drag_ele = select_ele(xpath='//*[@class="_61Ei-7"]')
    bg_ele = select_ele(xpath='//*[@class="BX1JD-"]')
    piece_ele = select_ele(xpath='//*[@class="MqzVM5"]')
    retry_count = 5
    offset = 0
    refresh_ele = select_ele(xpath='//*[@class="rf8fOu"]')
    handle_captcha(web_page, drag_ele, bg_ele, piece_ele, retry_count, offset, refresh_ele)
    exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    drag_ele = args.get("drag_ele")
    bg_ele = args.get("bg_ele")
    piece_ele = args.get("piece_ele")
    retry_count = args.get("retry_count", 5)
    offset = args.get("offset", 0)
    refresh_ele = args.get("refresh_ele", "")
    wait_time = args.get('wait_time', 2)
    handle_captcha(web_page, drag_ele, bg_ele, piece_ele, retry_count, offset, refresh_ele, wait_time)