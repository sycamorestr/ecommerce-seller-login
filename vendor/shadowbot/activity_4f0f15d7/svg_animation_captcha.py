# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用流程"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .package import variables as glv
from xbot.selector import Selector
import xml.etree.ElementTree as ET
import re
import copy
import base64
import uuid
import json
import os
import time
from .utils import get_ppi
from io import BytesIO
from PIL import Image, ImageOps

SVG_NS = "http://www.w3.org/2000/svg"


def css_block(text, pattern):
    match = re.search(pattern, text)
    if not match:
        raise ValueError("未找到 CSS：%s" % pattern)
    start = text.index("{", match.start())
    depth = 0
    for index in range(start, len(text)):
        depth += (text[index] == "{") - (text[index] == "}")
        if depth == 0:
            return text[start + 1:index]
    raise ValueError("CSS 花括号不完整")


def frame_number(node):
    match = re.search(r"geetest_frame_(\d+)_", node.get("class", ""))
    return int(match.group(1)) if match else None


def render_svgs_batch(web_page, svg_info_list):
    """批量渲染 SVG 列表，减少浏览器通讯开销"""
    render_id = uuid.uuid4().hex[:8]
    # 1. 批量注入
    web_page.execute_javascript(
        """function(element, args) {
            var data = JSON.parse(args);
            data.forEach(function(item) {
                var el = document.createElement('img');
                el.id = item.id;
                el.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;height:1px';
                el.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(item.svg);
                document.body.appendChild(el);
            });
        }""",
        json.dumps([{"id": "svg_%s_%d" % (render_id, i), "svg": info[0]} for i, info in enumerate(svg_info_list)]),
    )
    
    # 2. 等待渲染队列完成
    sleep(0.5)
    
    # 3. 批量读取
    results = web_page.execute_javascript(
        """function(element, args) {
            var data = JSON.parse(args);
            return data.map(function(item) {
                var el = document.getElementById(item.id);
                if (!el || !el.complete) return '';
                var c = document.createElement('canvas');
                c.width = item.w; c.height = item.h;
                c.getContext('2d').drawImage(el, 0, 0, item.w, item.h);
                el.remove();
                return c.toDataURL('image/png');
            });
        }""",
        json.dumps([{"id": "svg_%s_%d" % (render_id, i), "w": info[1], "h": info[2]} for i, info in enumerate(svg_info_list)]),
    )
    
    bytes_list = []
    for res in results:
        if not res:
            bytes_list.append(None)
            continue
        _, encoded = res.split(",", 1)
        bytes_list.append(base64.b64decode(encoded))
    return bytes_list


def make_icon(group):
    translates = re.findall(
        r"translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)",
        group.get("transform", ""),
    )
    center = tuple(map(float, translates[-1])) if translates else ()
    size = max(map(abs, center)) * 2 if center and all(v < 0 for v in center) else 24
    
    svg = ET.Element(
        "{%s}svg" % SVG_NS,
        {
            "xmlns": SVG_NS,
            "viewBox": "0 0 %g %g" % (size, size),
            "width": "48",
            "height": "48",
        },
    )
    icon = copy.deepcopy(group)
    icon.attrib.pop("transform", None)
    icon.set("fill", "none")
    icon.set("stroke", "#000")
    icon.set("stroke-width", "2")
    icon.set("stroke-linecap", "round")
    icon.set("stroke-linejoin", "round")
    svg.append(icon)
    return ET.tostring(svg, encoding="unicode")


def image_mask(image):
    image = image.convert("RGBA")
    alpha = image.getchannel("A")
    if alpha.getextrema()[0] < 250:
        channel = alpha
    else:
        channel = ImageOps.invert(ImageOps.grayscale(image))
    width, _ = channel.size
    return set(
        (index % width, index // width)
        for index, value in enumerate(channel.getdata())
        if value > 40
    )


def similarity(target, candidate):
    if not target or not candidate:
        return 0.0
    best = 0.0
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            shifted = set((x + dx, y + dy) for x, y in candidate)
            intersection = len(target & shifted)
            score = 2 * intersection / (len(target) + len(candidate))
            if score > best:
                best = score
    return best


def visible_interval(svg_text, number, duration):
    block = css_block(
        svg_text, r"@keyframes\s+geetest_frame%d_animation_\w+" % number
    )
    visible = [
        float(percent)
        for percent, opacity in re.findall(
            r"([\d.]+)%\s*\{\s*opacity:\s*([01])", block
        )
        if opacity == "1"
    ]
    if not visible:
        raise ValueError("第 %d 帧没有可见时间" % number)
    return min(visible) / 100 * duration, max(visible) / 100 * duration


def get_svg_markup(web_page):
    svg_el = web_page.find_by_xpath(
        '//*[local-name()="svg" and contains(@class,"geetest_svg_container")]',
        timeout=5,
    )
    markup = svg_el.execute_javascript(
        "function(element, args) { return new XMLSerializer().serializeToString(element); }"
    )
    for _ in range(10):
        bounding = svg_el.get_bounding(to96dpi=False)
        if bounding[2] > 0 and bounding[3] > 0:
            break
        sleep(0.5)
    return markup, bounding


def get_target_image_bytes(web_page, target_ele):
    el = web_page.find(target_ele)
    src = el.get_attribute("src")
    if not src:
        return None
    if src.startswith("data:image/"):
        _, encoded = src.split(",", 1)
        return base64.b64decode(encoded)
    if src.startswith("http"):
        data_uri = el.execute_javascript(
            """function(element, args) {
                var c = document.createElement('canvas');
                c.width = element.naturalWidth || element.width;
                c.height = element.naturalHeight || element.height;
                c.getContext('2d').drawImage(element, 0, 0);
                try { return c.toDataURL('image/png'); } catch(e) { return ''; }
            }"""
        )
        if data_uri:
            _, encoded = data_uri.split(",", 1)
            return base64.b64decode(encoded)
        import tempfile
        tmp_dir = tempfile.mkdtemp()
        save_path = os.path.join(tmp_dir, "target.png")
        web_page.http_request(
            src, method="GET", connect_timeout=10,
            save_filename=save_path,
        )
        data = open(save_path, "rb").read()
        try:
            os.remove(save_path)
            os.rmdir(tmp_dir)
        except Exception:
            pass
        return data
    return None


def get_click_coords(bounding, x, y, canvas_width, canvas_height):
    scale = get_ppi() if os.name == "nt" else 1.0
    if scale <= 0:
        scale = 1.0
    screen_x = (bounding[0] + (x / canvas_width) * bounding[2]) * scale
    screen_y = (bounding[1] + (y / canvas_height) * bounding[3]) * scale
    return screen_x, screen_y


def check_captcha_passed(web_page):
    sleep(1)
    try:
        tips_el = web_page.find_by_xpath(
            '//div[contains(@class,"geetest_result_tips")]', timeout=2
        )
        tips_text = tips_el.get_text()
        return tips_text and "秒的速度" in tips_text
    except Exception:
        return False


def handle_captcha(web_page, target_ele, refresh_ele, retry_count=5, wait_time=2):
    for attempt in range(int(retry_count)):
        print("第 %d/%d 次验证尝试" % (attempt + 1, retry_count))
        if refresh_ele:
            web_page.find(refresh_ele).click()
            for _ in range(20):
                try:
                    web_page.find_by_xpath(
                        '//*[local-name()="svg" and contains(@class,"geetest_svg_container")]',
                        timeout=1,
                    )
                    break
                except Exception:
                    sleep(0.1)
            attempt_start = time.time()
        else:
            attempt_start = time.time()

        svg_text, svg_bounding = get_svg_markup(web_page)
        target_bytes = get_target_image_bytes(web_page, target_ele)
        if not svg_text or not target_bytes:
            continue

        target_image = Image.open(BytesIO(target_bytes)).convert("RGBA").resize((48, 48))
        target_mask = image_mask(target_image)

        root = ET.fromstring(svg_text)
        view_box = root.get("viewBox", "")
        parts = view_box.split()
        if len(parts) != 4:
            continue
        _, _, canvas_width, canvas_height = map(float, parts)

        duration_match = re.search(r"animation:\s*\S+\s+([\d.]+)s", svg_text)
        if not duration_match:
            duration_match = re.search(r"animation:\s*([\d.]+)s", svg_text) # 兼容极简格式
            if not duration_match: continue
        duration = float(duration_match.group(1))

        frames = []
        for node in root:
            fn = frame_number(node)
            if fn is not None:
                frames.append((fn, node))

        if not frames:
            continue

        # 1. 收集所有需要渲染的图标 SVG
        icon_tasks = [] # (number, cell_index, cell, svg_str)
        for number, frame in frames:
            cell = None
            cell_index = -1
            for node in frame:
                if "geetest_grid_" in node.get("class", ""):
                    cell = node
                    cell_index += 1
                elif node.tag.endswith("g") and cell is not None:
                    icon_svg_str = make_icon(node)
                    icon_tasks.append((number, cell_index, cell, icon_svg_str))
                    cell = None

        # 2. 批量渲染图标
        # print("正在批量识别 %d 个图标..." % len(icon_tasks))
        png_list = render_svgs_batch(web_page, [(t[3], 48, 48) for t in icon_tasks])

        # 3. 匹配图标
        candidates = []
        for i, png_bytes in enumerate(png_list):
            if not png_bytes: continue
            icon_image = Image.open(BytesIO(png_bytes))
            score = similarity(target_mask, image_mask(icon_image))
            candidates.append((score, icon_tasks[i][0], icon_tasks[i][1], icon_tasks[i][2]))

        if not candidates:
            continue

        score, number, cell_index, cell = max(candidates)
        print("匹配成功: 帧%d 格%d (相似度 %.1f%%)" % (number, cell_index + 1, score * 100))
        if score < 0.65:
            continue

        start, end = visible_interval(svg_text, number, duration)
        x = float(cell.get("x")) + float(cell.get("width")) / 2
        y = float(cell.get("y")) + float(cell.get("height")) / 2

        screen_x, screen_y = get_click_coords(svg_bounding, x, y, canvas_width, canvas_height)

        # 预位移
        win32.mouse_move(int(screen_x), int(screen_y), move_speed="instant")
        
        # 计算等待时间
        elapsed = (time.time() - attempt_start) % duration
        if elapsed <= start:
            wait = start - elapsed
        elif elapsed <= end:
            wait = 0
        else:
            wait = duration - elapsed + start

        if wait > 0:
            sleep(wait)
            
        # 点击前再次微调校验
        elapsed = (time.time() - attempt_start) % duration
        if elapsed > end - 0.4: # 留 0.4s 容差给点击动作
            sleep(duration - elapsed + start)
            
        win32.mouse_click(button="left", click_type="click")

        if check_captcha_passed(web_page):
            print("验证通过")
            return

        print("验证未通过，继续重试")

    raise Exception("验证码处理失败，已达到最大重试次数(%d)" % retry_count)


def gen_selector(xpath):
    if isinstance(xpath, str):
        xpath = [xpath]
    uid = str(uuid.uuid4())
    data = {
        "id": uid,
        "name": uid,
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpath},
    }
    return Selector(data)


def test_func():
    if "xbot_extensions" in __file__:
        return

    web_page = web.get_active("chrome")
    target_ele = gen_selector(
        '//div[contains(@class,"geetest_ques_tips")]/img'
    )
    refresh_ele = gen_selector(
        '//button[contains(concat(" ", @class, " "), " geetest_refresh ")]'
    )

    handle_captcha(
        web_page=web_page,
        target_ele=target_ele,
        refresh_ele=refresh_ele,
        retry_count=5,
        wait_time=2,
    )
    exit()


def main(args):
    test_func()
    if args is None:
        args = {}

    web_page = args.get("web_page") or web.get_active("chrome")
    target_ele = args.get("target_ele") or gen_selector(
        '//div[contains(@class,"geetest_ques_tips")]/img'
    )
    refresh_ele = args.get("refresh_ele") or gen_selector(
        '//button[contains(concat(" ", @class, " "), " geetest_refresh ")]'
    )
    retry_count = args.get("retry_count", 5)
    wait_time = args.get("wait_time", 2)

    handle_captcha(web_page, target_ele, refresh_ele, retry_count, wait_time)