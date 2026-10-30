# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用流程"的指令使用此模块

import xbot
from xbot import print, sleep
import xbot.web
import xbot_visual
from . import package
from .package import variables as glv

import os
import base64
import numpy as np
import cv2
from PIL import Image
import io
import uuid

# --- 验证码识别核心算法 ---

GLYPH = 32
BG_DIFF = 45
ROI_A = (0, 50)
ROI_OP = (50, 100)
ROI_B = (100, 150)

def merge_gif_frames_from_bytes(gif_data):
    im = Image.open(io.BytesIO(gif_data))
    frames = []
    for i in range(getattr(im, 'n_frames', 1)):
        im.seek(i)
        frames.append(np.array(im.convert("RGB")))
    return np.stack(frames).min(axis=0).astype(np.uint8)

def make_mask(img_bgr):
    bg = np.median(img_bgr.reshape(-1, 3), axis=0)
    diff = np.linalg.norm(img_bgr.astype(np.float32) - bg, axis=2)
    m = (diff > BG_DIFF).astype(np.uint8) * 255
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

def make_core(mask, th=1.5):
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
    return (dist >= th).astype(np.uint8) * 255

def _core_box(core, x0, x1, min_area=8):
    sub = core[:, x0:x1]
    n, _, stats, _ = cv2.connectedComponentsWithStats(sub, connectivity=8)
    x0c = y0c = x1c = y1c = None
    for i in range(1, n):
        if stats[i, 4] < min_area:
            continue
        x, y, w, h = (int(v) for v in stats[i, :4])
        x0c = x if x0c is None else min(x0c, x)
        y0c = y if y0c is None else min(y0c, y)
        x1c = x + w if x1c is None else max(x1c, x + w)
        y1c = y + h if y1c is None else max(y1c, y + h)
    if x0c is None:
        return None
    return x0c + x0, y0c, x1c + x0, y1c

def _norm_crop(bin_img, box):
    x, y, w, h = box
    crop = bin_img[y:y + h, x:x + w]
    s = max(w, h)
    sq = np.zeros((s, s), np.uint8)
    oy, ox = (s - h) // 2, (s - w) // 2
    sq[oy:oy + h, ox:ox + w] = crop
    return (cv2.resize(sq, (GLYPH, GLYPH), interpolation=cv2.INTER_AREA) > 127).astype(np.uint8)

def roi_glyph(mask, core, rgb, x0, x1, pad=3, color_tol=None):
    b = _core_box(core, x0, x1)
    if b is None: return None, None
    bx0, by0, bx1, by1 = max(0, b[0]-pad), max(0, b[1]-pad), min(mask.shape[1], b[2]+pad), min(mask.shape[0], b[3]+pad)
    sub = mask[by0:by1, bx0:bx1]
    if color_tol is not None:
        coresub = core[by0:by1, bx0:bx1] > 0
        sub_rgb = rgb[by0:by1, bx0:bx1].astype(np.float32)
        if coresub.sum() >= 5:
            c0 = np.median(sub_rgb[coresub], axis=0)
            cdist = np.linalg.norm(sub_rgb - c0, axis=2)
            sub = np.where((cdist < color_tol) & (sub > 0), 255, 0).astype(np.uint8)
    e = cv2.erode(sub, np.ones((2, 2), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(e, connectivity=8)
    if n > 1:
        biggest = 1 + int(np.argmax([stats[i, 4] for i in range(1, n)]))
        seed = (lab == biggest).astype(np.uint8) * 255
        rec = cv2.dilate(seed, np.ones((3, 3), np.uint8))
        keep = np.where(rec > 0, sub, 0)
    else: keep = sub
    ys, xs = np.nonzero(keep)
    if len(xs) == 0: return None, None
    x0c, x1c, y0c, y1c = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    return _norm_crop(keep, (x0c, y0c, x1c - x0c, y1c - y0c)), (x0c + bx0, y0c + by0, x1c - x0c, y1c - y0c)

def roi_op(mask, core, x0=ROI_OP[0], x1=ROI_OP[1]):
    sub = core[:, x0:x1]
    n, _, stats, _ = cv2.connectedComponentsWithStats(sub, connectivity=8)
    best, ba = -1, 7
    for i in range(1, n):
        if stats[i, 4] > ba: best, ba = i, int(stats[i, 4])
    if best < 0: return None
    h = int(stats[best, 3])
    return "-" if h <= 10 else "+"

def classify_digit(norm, templates, k=3):
    glyphs, labels = templates
    dists = np.mean(norm[None, :, :] != glyphs, axis=(1, 2))
    order = np.argsort(dists, kind="stable")
    votes = {}
    for rank, i in enumerate(order[:k]):
        lab = str(labels[i])
        votes.setdefault(lab, []).append((rank, float(dists[i])))
    def key(item):
        ranks = [r for r, _ in item[1]]; ds = [d for _, d in item[1]]
        return (-len(ranks), min(ranks), sum(ds) / len(ds))
    return sorted(votes.items(), key=key)[0][0], float(dists[order[0]])

def solve_captcha_core(gif_data, tpl_path):
    z = np.load(tpl_path)
    templates = (z["glyphs"], z["labels"])
    rgb = merge_gif_frames_from_bytes(gif_data)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    mask = make_mask(bgr); core = make_core(mask)
    ga, _ = roi_glyph(mask, core, rgb, *ROI_A)
    gb, _ = roi_glyph(mask, core, rgb, *ROI_B)
    op = roi_op(mask, core)
    if ga is None or gb is None or op is None: return {"ok": False}
    a, _ = classify_digit(ga, templates); b, _ = classify_digit(gb, templates)
    ans = int(a) + int(b) if op == "+" else int(a) - int(b)
    return {"ok": True, "expr": f"{a}{op}{b}", "answer": str(ans)}

# --- 主逻辑与测试用例 ---

def gen_selector(xpath):
    from xbot.web import Selector
    if isinstance(xpath, str): xpath = [xpath]
    uid = str(uuid.uuid4())
    return Selector({"id": uid, "name": uid, "type": "simple", "xpath": {"enable": "true", "segments": xpath}})

def handle_captcha(web_page, target_ele):
    """验证码识别"""
    tpl_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="digit_templates.npz")
    try:
        target_ele = web_page.find(target_ele)

        src = target_ele.get_attribute("src")
        if not src or "data:image/gif;base64," not in src:
            sleep(2)
            src = target_ele.get_attribute("src")
        
        gif_data = base64.b64decode(src.split(",", 1)[1])
        res = solve_captcha_core(gif_data, tpl_path)
        if res["ok"]:
            # xbot.print(f"识别结果: {res['expr']} = {res['answer']}")
            return res["answer"]
        else:
            xbot.print("识别失败")
    except Exception as e:
        xbot.print(f"异常: {e}")
    return None

def test_func():
    if "xbot_extensions" in __file__:
        return
    web_page = xbot.web.get_active("chrome")
    target_ele = gen_selector('//img[contains(@class, "login-content-code-img")]')
    ans = handle_captcha(web_page, target_ele)
    print(ans)
    exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    target_ele = args.get("target_ele")
    
    ans = handle_captcha(web_page, target_ele)
    
    args["result"] = ans
