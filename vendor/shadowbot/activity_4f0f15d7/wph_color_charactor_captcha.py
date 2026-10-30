# -*- coding: utf-8 -*-
"""xbot 验证码识别指令。

输入参数（args）：
    web_page: xbot 网页对象
    prompt_ele: 提示词图片元素，或可被 web_page.find() 查找的选择器
    captcha_ele: 验证码图片元素，或可被 web_page.find() 查找的选择器

输出参数：
    result: 目标颜色对应的验证码答案字符串
    result_detail: 完整识别结果字典

本文件包含完整图像识别逻辑。
"""

import hashlib
import base64
import os
import tempfile
import uuid
from urllib.request import Request, urlopen

import cv2
import numpy as np
import xbot
import xbot_visual
from xbot import print


MODEL_FILE = "captcha_cnn_r1.onnx"
CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
IMG = 40

HUE_RANGES = [
    ("红色", [(0, 7), (173, 179)]),
    ("橙色", [(8, 17)]),
    ("黄色", [(18, 40)]),
    ("绿色", [(41, 85)]),
    ("蓝色", [(86, 125)]),
    ("紫色", [(126, 172)]),
]

# 问题图中的颜色词使用固定红色字体，按字形掩码识别词形。
WORD_HASH = {
    "269e7565b7": "红色",
    "34a99d8828": "黄色",
    "ba011ccba4": "蓝色",
    "a24b0e7b89": "绿色",
    "2373af0f79": "紫色",
    # 浏览器截图/白底合成后的同一组提示词字形。
    "059a34df4a": "红色",
    "c5d137d387": "黄色",
    "c00511403f": "蓝色",
    "80ba6be92a": "绿色",
    "715f5668dc": "紫色",
}


def read_bgr(image, composite_alpha=True):
    if isinstance(image, np.ndarray):
        image = image.copy()
    else:
        image = cv2.imread(str(image), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError("无法读取图片")
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4 and composite_alpha:
        rgb = image[:, :, :3].astype(np.float32)
        alpha = image[:, :, 3:4].astype(np.float32) / 255
        image = (rgb * alpha + 255 * (1 - alpha)).astype(np.uint8)
    return image[:, :, :3]


def color_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return hsv, ((hsv[:, :, 1] > 80) & (hsv[:, :, 2] > 100)).astype(np.uint8)


def parse_question(image):
    """从问题图中识别目标颜色词。透明 PNG 保留原始 BGR 通道。"""
    bgr = read_bgr(image, composite_alpha=False)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    mask = (((h <= 7) | (h >= 173)) & (s > 150) & (v > 150)).astype(np.uint8)
    ys, xs = np.where(mask)
    if len(xs) < 20:
        return None
    word = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    small = cv2.resize(word, (16, 8), interpolation=cv2.INTER_AREA)
    key = hashlib.md5((small > 0.3).tobytes()).hexdigest()[:10]
    return WORD_HASH.get(key)


def color_components(image):
    """按颜色提取字符块，返回 {颜色: [(x, 字符彩图)]}。"""
    bgr = read_bgr(image)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    result = {}
    for name, ranges in HUE_RANGES:
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in ranges:
            mask[(hsv[:, :, 0] >= lo) & (hsv[:, :, 0] <= hi) &
                 (hsv[:, :, 1] > 80) & (hsv[:, :, 2] > 100)] = 1
        if mask.sum() < 12:
            continue

        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        raw = []
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            if area >= 8 and h >= 3 and w >= 3:
                raw.append([x, x + w, y, y + h, area])

        merged = True
        while merged:
            merged = False
            for a in range(len(raw)):
                for b in range(a + 1, len(raw)):
                    x0a, x1a, y0a, y1a, _ = raw[a]
                    x0b, x1b, y0b, y1b, _ = raw[b]
                    overlap = min(x1a, x1b) - max(x0a, x0b)
                    gap = max(y0a, y0b) - min(y1a, y1b)
                    if overlap >= 0.5 * min(x1a - x0a, x1b - x0b) and -2 <= gap <= 3:
                        raw[a] = [min(x0a, x0b), max(x1a, x1b),
                                  min(y0a, y0b), max(y1a, y1b),
                                  raw[a][4] + raw[b][4]]
                        del raw[b]
                        merged = True
                        break
                if merged:
                    break

        boxes = []
        for x, x1, y, y1, area in raw:
            w, h = x1 - x, y1 - y
            if area < 20 or h < 8 or w < 4 or area < 0.22 * w * h:
                continue
            component = mask[y:y1, x:x1]
            if w >= 15:
                affine = np.float32([[1, -0.25, 0], [0, 1, 0]])
                sheared = cv2.warpAffine(component * 255, affine,
                                          (component.shape[1] + 8, component.shape[0]),
                                          flags=cv2.INTER_NEAREST)
                projection = (sheared > 0).sum(axis=0)
                cut = 3 + int(np.argmin(projection[3:component.shape[1] - 3]))
                if projection[cut] <= projection.mean() * 0.6 or projection[cut] == 0:
                    for part in (component[:, :cut], component[:, cut:]):
                        if part.sum() < 12 or part.shape[1] < 4:
                            continue
                        py, px = np.where(part)
                        boxes.append((x + px.min(), x + px.max() + 1,
                                      y + py.min(), y + py.max() + 1))
                    continue
            py, px = np.where(component)
            boxes.append((x + px.min(), x + px.max() + 1,
                          y + py.min(), y + py.max() + 1))

        crops = []
        for x0, x1, y0, y1 in sorted(boxes):
            crop = bgr[max(y0 - 1, 0):y1 + 1, max(x0 - 1, 0):x1 + 1]
            _, crop_mask_value = color_mask(crop)
            py, px = np.where(crop_mask_value > 0)
            if len(px) >= 4:
                crops.append((x0, crop[py.min():py.max() + 1, px.min():px.max() + 1]))
        if crops:
            result[name] = crops
    return result


def normalize(bgr):
    _, mask = color_mask(bgr)
    ys, xs = np.where(mask > 0)
    if len(xs) < 4:
        return np.zeros((IMG, IMG), np.float32)
    mask = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255
    h, w = mask.shape
    scale = (IMG - 6) / max(h, w)
    resized = cv2.resize(mask, (max(int(round(w * scale)), 1),
                                max(int(round(h * scale)), 1)),
                         interpolation=cv2.INTER_AREA)
    canvas = np.zeros((IMG, IMG), np.float32)
    ys2, xs2 = np.where(resized > 40)
    center_x = xs2.mean() if len(xs2) else resized.shape[1] / 2
    x0 = int(round(IMG / 2 - center_x))
    x0 = max(min(x0, IMG - resized.shape[1]), 0)
    if resized.shape[1] > IMG:
        resized = resized[:, :IMG]
    canvas[3:3 + resized.shape[0], x0:x0 + resized.shape[1]] = resized
    return canvas / 255.0


def load_model():
    model_path = xbot_visual.resourcesfile.get_resourcesfile_path(
        file_name=MODEL_FILE
    )
    if not model_path:
        raise FileNotFoundError(f"资源文件中找不到 {MODEL_FILE}")
    return cv2.dnn.readNetFromONNX(str(model_path))


def softmax(logits):
    logits = logits - logits.max(axis=1, keepdims=True)
    values = np.exp(logits)
    return values / values.sum(axis=1, keepdims=True)


def solve_images(question_image, captcha_image):
    target = parse_question(question_image)
    if target is None:
        return {"ok": False, "error": "无法识别问题图中的目标颜色词",
                "target_color": None, "answer": "", "confidence": 0.0, "n_chars": 0}

    crops = color_components(captcha_image).get(target, [])
    if not crops:
        return {"ok": False, "error": f"验证码图中未找到目标颜色: {target}",
                "target_color": target, "answer": "", "confidence": 0.0, "n_chars": 0}

    model = load_model()
    probabilities = []
    for _, crop in crops:
        batch = normalize(crop)[None, None].astype(np.float32)
        model.setInput(batch)
        logits = np.asarray(model.forward())
        if logits.ndim == 3:
            logits = logits[0]
        if logits.ndim != 2:
            raise RuntimeError(f"ONNX 模型输出维度异常: {logits.shape}")
        probabilities.append(softmax(logits)[0])
    probabilities = np.stack(probabilities)
    predictions = probabilities.argmax(1)
    answer = "".join(CHARS[i] for i in predictions)
    return {"ok": True, "target_color": target, "answer": answer,
            "confidence": round(float(probabilities.max(1).mean()), 4),
            "n_chars": len(answer)}


def _resolve_element(web_page, element):
    if element is None:
        return None
    if hasattr(element, "get_bounding"):
        return element
    if web_page is None or not element:
        return None
    return web_page.find(element)


def gen_selector(xpath):
    """按 gif_math_captcha.py 的方式生成 xbot XPath 选择器。"""
    from xbot.web import Selector

    if isinstance(xpath, str):
        xpath = [xpath]
    uid = str(uuid.uuid4())
    return Selector({
        "id": uid,
        "name": uid,
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpath},
    })


def _image_from_src(target):
    """读取 data URL 或远程 src；失败时由调用方截图兜底。"""
    try:
        src = target.get_attribute("src")
        if not src:
            return None
        if src.startswith("data:image/") and "," in src:
            raw = base64.b64decode(src.split(",", 1)[1])
        elif src.startswith(("http://", "https://")):
            request = Request(src, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=10) as response:
                raw = response.read()
        else:
            return None
        return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
    except Exception:
        return None


def _capture_element(web_page, element):
    target = _resolve_element(web_page, element)
    if target is None:
        return None

    # 与 gif_math_captcha.py 一致：如果图片是 data URL，直接取原图。
    image = _image_from_src(target)
    if image is not None:
        return image

    # URL 受限或读取失败时，使用元素区域截图兜底。
    x, y, w, h = target.get_bounding(to96dpi=False)
    if w <= 0 or h <= 0:
        return None
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, "element.png")
        xbot.win32.screenshot.save_screen_to_file(path, "png", x, y, x + w, y + h)
        return cv2.imread(path, cv2.IMREAD_UNCHANGED)


def handle_captcha(web_page, prompt_ele, captcha_ele):
    """截取提示词和验证码元素并完成识别。"""
    result = {"ok": False, "error": "", "target_color": None,
              "answer": "", "confidence": 0.0, "n_chars": 0}
    try:
        prompt_image = _capture_element(web_page, prompt_ele)
        captcha_image = _capture_element(web_page, captcha_ele)
        if prompt_image is None or captcha_image is None:
            result["error"] = "无法截取提示词元素或验证码元素"
        else:
            result = solve_images(prompt_image, captcha_image)
    except Exception as exc:
        result["error"] = f"验证码识别失败: {type(exc).__name__}: {exc}"
    return result


def test_func():
    """用 XPath 测试当前 Chrome 页面。"""
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active("chrome")
    prompt_ele = gen_selector('//img[@class="vipsc_code_qimg"]')
    captcha_ele = gen_selector('//img[@class="vipsc_code_img"]')
    result = handle_captcha(web_page, prompt_ele, captcha_ele)
    print(result["answer"] if result["ok"] else result["error"])
    exit()


def main(args):
    """xbot 指令入口。"""
    test_func()

    web_page = args.get("web_page")
    prompt_ele = args.get("prompt_ele")
    captcha_ele = args.get("captcha_ele")
    result = handle_captcha(web_page, prompt_ele, captcha_ele)

    args["result"] = result["answer"] if result["ok"] else ""
    args["result_detail"] = result
    return args["result"]
