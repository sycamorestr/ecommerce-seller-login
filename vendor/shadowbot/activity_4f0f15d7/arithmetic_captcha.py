# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
import base64
import os
import tempfile
import numpy as np
import cv2

GLYPH = 32
OP_HEIGHT_SPLIT = 8  # 运算符字符高度 < 该值判为 '-'（细横线），否则 '+'
BG_DIFF = 45  # 与背景中位色的差异阈值（前景分割）

LABELS = "=?C+-17598036424-C"
_TPL_B64 = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AP//////////////////////////P////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB//4AAf//AAP//wAH//+AD///4A/w"
    "P+AP8B/gD/Af4A/wH+AP8B/gD/Af4AAAH+AAAP/gAAD/wAAA/wAAB/8AAA/+AAAP8AAAD/AAAH/wAAB/gAAAf4AAAD+AAAAAAAAA"
    "H4AAAD+AAAB/gAAAf4AAAH+AAAB/gAAAP4AAAB+AAD//AAA//wAAP+AAAD/AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAA"
    "P4AAAD+AAAA/gAAAP4AAAD+AAAA/4AAAP+AAAA/wAAAP+AAAD/wAAAf/AAAH/wAAB//4fAf/+HwB///8Af///AB///wAD//8AA//"
    "/AAA//wAAP/8AAAAAAAAAAAAD+AAAD/wAAA/8AAAP/AAAD/wAAA/8AAAP/AAAD/wAAA/8AAAP/AAAD/wAP////z////8////////"
    "///////8/////AA/8AAAP/AAAD/wAAA/8AAAP/AAAD/wAAA/8AAAP/AAAA/wAAAP8AAAD+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/////P////z///////////////z////8AAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP4AAAD+AAAA/gAAB/4AAA/+AAAP/gAAD/4AAH/+AAB//g"
    "AAf/4AAD/+AAAB/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAA/gAAAP4AAAD+AAAB/gAAH/"
    "/wAH//+AB///gAP//4AB//8AD///8B////gf///4H///+A////gAAA/4AAAP+AAAD/gAAA/4AAAf8AAAP/AAAH/gAAD/gAAB/wAA"
    "A/8AAAf+AAAP/gAAH/AAAD/wAAB/8AAA/4AAAf8AAAP/AAAH/gAAD/gAAB/wAAAf8AAAH/AAAB/wAAAf4AAAH+AAAA/gAAAP//+A"
    "H///gB///4Af//+AH///gB/gAAAf4AAAH+AAAB/gAAAf7/wAH+/+AB/v/gAf//+AH///gB///8Af+H/wD/gf+AAAD/gAAA/4AAAP"
    "+AAAD/gfwA/4H+AP+B/gD/gf+B/wB/g/4Af8f8AH//+AAf//gAB//gAAf/4AAH/+AAB//gAAf/4AAH/+AAH//4AB///gA/4/4Af8"
    "H+AP+B/4H/AH+B/wB/gf8Af4H/AH+B/4H/gP/B/4A/4/+AH///gB///4AH/3+AB/9/gAf/f4AAAH+AHAB/gB4Af4AfAH+AH4H/gB"
    "/B/gAf4/4AH//+AA//+AAH/+AAB//gAAf/4AAH/+AAB//gAAf/4AAf//gAH//+AH/j/gB/wf4B/4H/gf8A/4D/gf+A/8H/gH/h/g"
    "Af//gAD//wAA//8AAf//gAH//+AH/j/gB/wf8B/4H/gf8Af4H/AH+B/wB/gf8Af4D/gf+Af8H+AD/j/gAf//4AD//4AAf/4AAH/+"
    "AAB//gAAD+AAAB/gAAA/4AAAf/gAAP/8AAD//gAB//8AB///gAf4f4Af+H/wH/g/8B/gD/Af4A/wH+AP8B/gD/Af4A/wH+AP8B/g"
    "D/Af4A/wH+AP8B/gH/Af+D/wH/h/8Af4f4AH//+AAf//AAD//gAA//wAAH/wAAA/4AAAH+AAAA/gAAH/+AAD//wAB//+AA///wAf"
    "//+AH+B/wB/gf+Af4H/wAAAP+AAAH/AAAD/wAAB/4AAP/4AAD/8AAA//AAAP/wAAD/+AAAB/wAAAP+AAAB/wAAAP+AAAD/gAAA/4"
    "AAAP+A/gH/Af4D/gH+B/wB///4AP//+AB//+AAP//gAB//4AAH/+AAB//gAAf/4AAP//AAH//4AH/D+AB/gfgB/4H4Af4AeAH+AH"
    "gB/gA4Af4AAAH+/+AB/v/gAf7/4AH///gB///4Af/D/gH/gf4B/4H/Af4Af4H+AH+B/gB/gf4A/4H/gf8Af4P+AH/H/gAf//gAH/"
    "/4AAf/4AAH/+AAB//gAAAB8AAAA/gAAAf4AAAH+AAAH/gAAD/4AAB/+AAA//gAAP/4AAP/+AAH//gAD//4AB/3+AA/5/gAf8f4Af"
    "+H+AH/h/gB/gf4Af///gH///8B////gf///wH///8AAAf4AAAH+AAAB/gAAAf4AAAH+AAAB/gAAAf4AAAD+AAAAfAAB//gAAf/4A"
    "AH/+AAH//4AH//+AD/x/wA/4P+Af+B/wH+AP+B/gD/gfwA/4AAAP+AAAH/AAAD/gAAB/wAAA/4AAAf+AAAP+AAAH/gAAD/4AAA/w"
    "AAA/8AAAf/AAAP+AAAH/AAAD/gAAB/4AAA////Af///wH///8B////AP///wAAAfgAAAH8AAAD/gAAD/4AAB/+AAAf/gAAP/4AAP"
    "/+AAD//gAD//4AB//+AAf5/gAf+f4AH+H+AD/h/gD/4f4B/wH+Af///wH///8B////gf///4D///8A////AAAB/gAAAf4AAAH+AA"
    "AB/gAAAf4AAAH+AAAB/gAAAfwAAAH4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAP//////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AA+MAAAPhAAAD4AAAB8AAAA+AAAAPgAAAD4AAAA+AAAAPgAAAD4AAAA+AAAAPgAAAD4AAAA+AAAAH4AAAA+AAAAPgAAAD4AAAA/g"
    "AAAP4AAAB/AAAAH8AAAB/AAAAf8AAAH/AAAAf//8AH///AAP//wAA//8AAP//AAAB4AAAAeA"
)


def _load_templates():
    raw = np.frombuffer(base64.b64decode(_TPL_B64), dtype=np.uint8)
    bits = np.unpackbits(raw).reshape(-1, GLYPH, GLYPH).astype(np.uint8)
    return bits[: len(LABELS)]


_CENTROIDS = _load_templates()


def _mask(img):
    """前景 = 与背景中位色差异大的像素。兼容白底/浅色底，并保留灰色 +/- 运算符。"""
    bg = np.median(img.reshape(-1, 3), axis=0)
    diff = np.linalg.norm(img.astype(np.float32) - bg, axis=2)
    return (diff > BG_DIFF).astype(np.uint8) * 255


def _char_boxes(mask, min_area=10):
    """连通域按 x 轴重叠合并为字符，返回从左到右的 (x, y, w, h)。"""
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    comps = [list(stats[i, :4]) for i in range(1, n) if stats[i, 4] >= min_area]
    comps.sort(key=lambda c: c[0])
    groups = []
    for x, y, w, h in comps:
        x2, y2 = x + w, y + h
        for g in groups:
            if not (x2 < g[0] or x > g[2]):
                g[0], g[1] = min(g[0], x), min(g[1], y)
                g[2], g[3] = max(g[2], x2), max(g[3], y2)
                break
        else:
            groups.append([x, y, x2, y2])
    groups.sort(key=lambda g: g[0])
    return [(g[0], g[1], g[2] - g[0], g[3] - g[1]) for g in groups]


def _norm(mask, box, size=GLYPH):
    x, y, w, h = box
    crop = mask[y : y + h, x : x + w]
    s = max(w, h)
    sq = np.zeros((s, s), np.uint8)
    oy, ox = (s - h) // 2, (s - w) // 2
    sq[oy : oy + h, ox : ox + w] = crop
    return (cv2.resize(sq, (size, size), interpolation=cv2.INTER_AREA) > 127).astype(
        np.uint8
    )


def _classify(glyph):
    best, bd = "?", 1.0
    for c, lab in zip(_CENTROIDS, LABELS):
        d = float(np.mean(glyph != c))
        if d < bd:
            bd, best = d, lab
    return best, bd


def solve(image):
    """识别并计算。image 可为图片路径(str)或 BGR 数组(numpy)。返回结果字典。"""
    img = cv2.imread(image) if isinstance(image, str) else image
    if img is None:
        return {"ok": False, "error": "无法读取图片", "expr": None, "answer": None}

    mask = _mask(img)
    boxes = _char_boxes(mask)
    glyphs = [(_classify(_norm(mask, b)), b) for b in boxes]
    tokens = [g[0][0] for g in glyphs]
    confs = [g[0][1] for g in glyphs]
    res = {
        "ok": False,
        "tokens": "".join(tokens),
        "expr": None,
        "answer": None,
        "max_dist": round(max(confs), 3) if confs else None,
    }

    # 操作数 A = 开头连续的数字
    i, a = 0, ""
    while i < len(glyphs) and tokens[i].isdigit():
        a += tokens[i]
        i += 1
    if not a or i >= len(glyphs):
        return res
    # 运算符 = A 之后第一个非数字字符；正负号由其字符高度判定
    op = "-" if glyphs[i][1][3] < OP_HEIGHT_SPLIT else "+"
    i += 1
    # 操作数 B = 之后连续的数字
    b = ""
    while i < len(glyphs) and tokens[i].isdigit():
        b += tokens[i]
        i += 1
    if not b:
        return res

    a, b = int(a), int(b)
    ans = a + b if op == "+" else a - b
    res.update(
        {
            "ok": True,
            "expr": "%d %s %d" % (a, op, b),
            "a": a,
            "op": op,
            "b": b,
            "answer": ans,
        }
    )
    return res


def _resolve_element(web_page, element):
    if hasattr(element, "find"):
        return element
    if web_page is None or not element:
        return None
    return web_page.find(element)


def _capture_element_image(web_page, element):
    target = _resolve_element(web_page, element)
    if target is None:
        return None

    # 仅在真正需要截图时引入 xbot，避免本地纯算法调用时强依赖运行环境。
    import xbot

    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "captcha.png")
        x, y, w, h = target.get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(
            image_path, "png", x, y, x + w, y + h
        )
        return cv2.imread(image_path)


def test():
    if "xbot_extension" not in __file__:

        web_page = xbot.web.get_active(mode="chrome")
        picture_ele = web_page.find("图片")
        image = _capture_element_image(web_page, picture_ele)
        if image is None:
            return ""
        r = solve(image)
        result = str(r["answer"]) if r["ok"] else ""
        print(result)
        exit()



def main(args):
    
    test()
    web_page = args.get("web_page")
    picture_ele = args.get("picture_ele")
    image = _capture_element_image(web_page, picture_ele)
    if image is None:
        return ""
    r = solve(image)
    result = str(r["answer"]) if r["ok"] else ""
    args["result"] = result

