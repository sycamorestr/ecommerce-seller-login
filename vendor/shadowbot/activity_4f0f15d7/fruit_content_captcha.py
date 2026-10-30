import os
import time
from collections import defaultdict
from itertools import permutations
from pathlib import Path

import cv2
import numpy as np

import xbot
import xbot_visual
from xbot import print, sleep, win32
from . import package
from .utils import get_ppi, get_xbot_activity_cache_folder


SUPPORTED_FRUITS = (
    "草莓", "苹果", "石榴", "芒果", "香蕉", "柿子", "梨", "椰子",
    "橘子", "猕猴桃", "樱桃", "葡萄", "菠萝", "榴莲", "西瓜",
)
PROMPT_CLASSES = ("1", "2", "3", "4", "5", "从多到少") + SUPPORTED_FRUITS
PROMPT_CONFIDENCE = 0.50
FRUIT_GRID_CONFIDENCE = 0.40


def _read_image(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def _normalize_target(value):
    aliases = {name: name for name in SUPPORTED_FRUITS}
    aliases.update({"奇异果": "猕猴桃", "凤梨": "菠萝"})
    key = str(value).strip().lower()
    if key not in aliases:
        raise ValueError("不支持的水果：" + str(value))
    return aliases[key]


class PromptDnnDetector:
    INPUT_SIZE = 640

    def __init__(self, model_path, digit_conf=0.50, fruit_conf=0.50, iou=0.45):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError("提示词模型不存在：" + str(self.model_path))
        self.net = cv2.dnn.readNetFromONNX(str(self.model_path))
        self.digit_conf = float(digit_conf)
        self.fruit_conf = float(fruit_conf)
        self.iou = float(iou)

    @classmethod
    def _letterbox(cls, image):
        height, width = image.shape[:2]
        scale = min(cls.INPUT_SIZE / max(width, 1), cls.INPUT_SIZE / max(height, 1))
        rw = max(1, int(round(width * scale)))
        rh = max(1, int(round(height * scale)))
        resized = cv2.resize(image, (rw, rh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((cls.INPUT_SIZE, cls.INPUT_SIZE, 3), 114, dtype=np.uint8)
        px = (cls.INPUT_SIZE - rw) // 2
        py = (cls.INPUT_SIZE - rh) // 2
        canvas[py:py + rh, px:px + rw] = resized
        return canvas, scale, px, py

    def detect(self, image):
        if image is None or image.size == 0:
            return []
        canvas, scale, px, py = self._letterbox(image)
        blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0,
                                     (self.INPUT_SIZE, self.INPUT_SIZE),
                                     swapRB=True, crop=False)
        self.net.setInput(blob)
        prediction = np.asarray(self.net.forward())
        if prediction.ndim == 3:
            prediction = prediction[0]
        if prediction.ndim != 2:
            raise RuntimeError("提示词模型输出维度异常：" + str(prediction.shape))
        if prediction.shape[0] < prediction.shape[1]:
            prediction = prediction.T
        if prediction.shape[1] < 4 + len(PROMPT_CLASSES):
            raise RuntimeError("提示词模型类别数异常：" + str(prediction.shape))

        detections = []
        scores_by_class = prediction[:, 4:4 + len(PROMPT_CLASSES)]
        for class_id, class_name in enumerate(PROMPT_CLASSES):
            threshold = self.fruit_conf if class_name in SUPPORTED_FRUITS else self.digit_conf
            scores = scores_by_class[:, class_id]
            keep = scores >= threshold
            if not np.any(keep):
                continue
            candidates = prediction[keep]
            candidate_scores = scores[keep]
            boxes = []
            for cx, cy, bw, bh in candidates[:, :4]:
                x0 = int(round((cx - bw / 2 - px) / scale))
                y0 = int(round((cy - bh / 2 - py) / scale))
                x1 = int(round((cx + bw / 2 - px) / scale))
                y1 = int(round((cy + bh / 2 - py) / scale))
                x0 = max(0, min(image.shape[1] - 1, x0))
                y0 = max(0, min(image.shape[0] - 1, y0))
                x1 = max(x0 + 1, min(image.shape[1], x1))
                y1 = max(y0 + 1, min(image.shape[0], y1))
                boxes.append([x0, y0, x1 - x0, y1 - y0])
            indices = cv2.dnn.NMSBoxes(
                boxes, candidate_scores.astype(float).tolist(), threshold, self.iou
            )
            for index in np.asarray(indices).reshape(-1) if len(indices) else []:
                x0, y0, bw, bh = boxes[int(index)]
                detections.append({
                    "class": class_name,
                    "x0": x0, "y0": y0, "x1": x0 + bw, "y1": y0 + bh,
                    "score": float(candidate_scores[int(index)]),
                })
        return detections

    @staticmethod
    def _deduplicate_digits(digits):
        result = []
        for item in sorted(digits, key=lambda value: value["score"], reverse=True):
            duplicate = False
            for old in result:
                ix0 = max(item["x0"], old["x0"])
                iy0 = max(item["y0"], old["y0"])
                ix1 = min(item["x1"], old["x1"])
                iy1 = min(item["y1"], old["y1"])
                inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
                area = max(1, (item["x1"] - item["x0"]) * (item["y1"] - item["y0"]))
                old_area = max(1, (old["x1"] - old["x0"]) * (old["y1"] - old["y0"]))
                if inter / max(area + old_area - inter, 1) > 0.50:
                    duplicate = True
                    break
            if not duplicate:
                result.append(item)
        return result

    def recognize(self, image):
        detections = self.detect(image)
        digits = self._deduplicate_digits([
            item for item in detections if item["class"] in {"1", "2", "3", "4", "5"}
        ])
        if len(digits) > 4:
            digits = sorted(digits, key=lambda item: item["score"], reverse=True)[:4]
        digits.sort(key=lambda item: (item["x0"] + item["x1"]) / 2)
        order = [int(item["class"]) for item in digits] if len(digits) == 4 else []

        fruit_candidates = [item for item in detections if item["class"] in SUPPORTED_FRUITS]
        target = max(fruit_candidates, key=lambda item: item["score"])["class"] \
            if fruit_candidates else None
        descending = any(item["class"] == "从多到少" for item in detections)
        return target, order, descending, detections


class GridExtractor:
    def split(self, image):
        height, width = image.shape[:2]
        x0, x1 = int(width * 0.028), int(width * 0.972)
        y0, y1 = int(height * 0.168), int(height * 0.945)
        tiles = []
        for row in range(3):
            for col in range(3):
                xa = x0 + (x1 - x0) * col // 3
                xb = x0 + (x1 - x0) * (col + 1) // 3
                ya = y0 + (y1 - y0) * row // 3
                yb = y0 + (y1 - y0) * (row + 1) // 3
                padx = max(1, (xb - xa) // 35)
                pady = max(1, (yb - ya) // 35)
                tiles.append((row + 1, col + 1, image[ya + pady:yb - pady, xa + padx:xb - padx]))
        return tiles


class FruitDnnDetector:
    INPUT_SIZE = 320

    def __init__(self, model_path, conf=0.40, iou=0.45):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError("fruit_v5 模型不存在：" + str(self.model_path))
        self.net = cv2.dnn.readNetFromONNX(str(self.model_path))
        self.conf = float(conf)
        self.iou = float(iou)

    def detect(self, tile, fruit_name):
        if tile is None or tile.size == 0:
            return 0, []
        height, width = tile.shape[:2]
        scale = min(self.INPUT_SIZE / max(width, 1), self.INPUT_SIZE / max(height, 1))
        rw, rh = max(1, int(round(width * scale))), max(1, int(round(height * scale)))
        resized = cv2.resize(tile, (rw, rh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((self.INPUT_SIZE, self.INPUT_SIZE, 3), 114, dtype=np.uint8)
        px, py = (self.INPUT_SIZE - rw) // 2, (self.INPUT_SIZE - rh) // 2
        canvas[py:py + rh, px:px + rw] = resized
        blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0,
                                     (self.INPUT_SIZE, self.INPUT_SIZE),
                                     swapRB=True, crop=False)
        self.net.setInput(blob)
        prediction = np.asarray(self.net.forward())
        if prediction.ndim == 3:
            prediction = prediction[0]
        if prediction.shape[0] < prediction.shape[1]:
            prediction = prediction.T
        fruit_id = SUPPORTED_FRUITS.index(fruit_name)
        scores = prediction[:, 4:4 + len(SUPPORTED_FRUITS)][:, fruit_id]
        keep = scores >= self.conf
        if not np.any(keep):
            return 0, []
        candidates, candidate_scores = prediction[keep], scores[keep]
        boxes = []
        for cx, cy, bw, bh in candidates[:, :4]:
            x0 = int(round((cx - bw / 2 - px) / scale))
            y0 = int(round((cy - bh / 2 - py) / scale))
            x1 = int(round((cx + bw / 2 - px) / scale))
            y1 = int(round((cy + bh / 2 - py) / scale))
            x0, y0 = max(0, min(width - 1, x0)), max(0, min(height - 1, y0))
            x1, y1 = max(x0 + 1, min(width, x1)), max(y0 + 1, min(height, y1))
            boxes.append([x0, y0, x1 - x0, y1 - y0])
        indices = cv2.dnn.NMSBoxes(boxes, candidate_scores.astype(float).tolist(), self.conf, self.iou)
        selected = np.asarray(indices).reshape(-1) if len(indices) else []
        result = [(boxes[int(i)][0], boxes[int(i)][1],
                   boxes[int(i)][0] + boxes[int(i)][2],
                   boxes[int(i)][1] + boxes[int(i)][3],
                   float(candidate_scores[int(i)])) for i in selected]
        return len(result), result


def _count_score(counts, order):
    if order:
        required = list(dict.fromkeys(order))
        coverage = sum(number in counts for number in required)
        unique = sum(counts.count(number) == 1 for number in required)
        exact = sum(number in counts for number in order)
        noise = sum(max(0, count - 5) for count in counts)
        return coverage * 20.0 + unique * 5.0 + exact - noise * 2.0
    non_zero = sum(count > 0 for count in counts)
    spread = max(counts) - min(counts)
    noise = sum(max(0, count - 6) for count in counts)
    return min(spread, 6) * 3.0 + min(non_zero, 6) - noise * 2.0


class FruitConnector:
    def __init__(self, target="auto", grid_model=None, prompt_model=None,
                 grid_conf=0.40, iou=0.45):
        self.target = "auto" if not target or str(target).lower() == "auto" else _normalize_target(target)
        self.grid = GridExtractor()
        self.grid_detector = FruitDnnDetector(grid_model, grid_conf, iou)
        self.prompt_detector = PromptDnnDetector(
            prompt_model, digit_conf=PROMPT_CONFIDENCE,
            fruit_conf=PROMPT_CONFIDENCE, iou=iou
        )

    def _infer_with_dnn(self, tiles, order):
        all_counts, ranked = {}, []
        for fruit in SUPPORTED_FRUITS:
            counts = [self.grid_detector.detect(tile, fruit)[0] for _, _, tile in tiles]
            all_counts[fruit] = counts
            ranked.append((_count_score(counts, order), fruit))
        ranked.sort(reverse=True)
        return ranked[0][1], all_counts, ranked

    @staticmethod
    def _assign(counts, order):
        positions = list(counts)
        best, best_cost = None, float("inf")
        for assignment in permutations(positions, len(order)):
            cost = sum(abs(counts[pos] - number) for pos, number in zip(assignment, order))
            if cost < best_cost:
                best, best_cost = assignment, cost
        return [[position] for position in best] if best else [[] for _ in order]

    def process(self, image_path):
        image = _read_image(image_path)
        if image is None:
            raise RuntimeError("无法读取图片：" + str(image_path))
        target_from_prompt, order, descending, prompt_detections = self.prompt_detector.recognize(image)
        tiles = self.grid.split(image)

        if self.target != "auto":
            target = self.target
            counts_list = [self.grid_detector.detect(tile, target)[0] for _, _, tile in tiles]
        elif target_from_prompt:
            target = target_from_prompt
            counts_list = [self.grid_detector.detect(tile, target)[0] for _, _, tile in tiles]
        else:
            target, all_counts, ranked = self._infer_with_dnn(tiles, order)
            counts_list = all_counts[target]
            print("提示词水果未达到 0.50，使用旧逻辑反推：" + target)

        counts = {(row, col): count for (row, col, _), count in zip(tiles, counts_list)}
        by_count = defaultdict(list)
        for position, count in counts.items():
            by_count[count].append(position)
        if order:
            result = self._assign(counts, order)
        elif descending:
            result = [positions for _, positions in sorted(by_count.items(), reverse=True)]
        else:
            raise RuntimeError("数字识别未达到 0.50，无法确认题目顺序")
        return {
            "image": str(image_path), "target": target, "order": order,
            "counts": counts, "result": result, "prompt_detections": prompt_detections,
        }


def _capture(web_page, img_ele, cache_dir):
    element = web_page.find(img_ele, timeout=5)
    ex, ey, ew, eh = element.get_bounding(to96dpi=False)
    ax, ay, _, _ = element.get_bounding(to96dpi=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "fruit_connect_temp.png"
    win32.screenshot.save_screen_to_file(str(path), "png", int(ex), int(ey), int(ex + ew), int(ey + eh))
    return path, (ex, ey, ew, eh), (ax, ay)


def _routing_waypoints(positions, image_width, image_height):
    x0 = int(image_width * 0.028)
    x1 = int(image_width * 0.972)
    y0 = int(image_height * 0.168)
    y1 = int(image_height * 0.945)
    dx = (x1 - x0) / 3.0
    dy = (y1 - y0) / 3.0

    def center(r, c):
        return (x0 + dx * (c - 0.5), y0 + dy * (r - 0.5))

    def corner(r, c):
        return (x0 + dx * c, y0 + dy * r)

    waypoints = []
    for i, (r1, c1) in enumerate(positions):
        waypoints.append(center(r1, c1))
        if i >= len(positions) - 1:
            continue
        r2, c2 = positions[i + 1]
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            continue
        if r1 == r2:
            mid_col = (c1 + c2) // 2
            if r1 == 1:
                waypoints.append(corner(0, mid_col))
            else:
                waypoints.append(corner(3, mid_col))
        elif c1 == c2:
            mid_row = (r1 + r2) // 2
            if c1 == 1:
                waypoints.append(corner(mid_row, 0))
            else:
                waypoints.append(corner(mid_row, 3))
        else:
            waypoints.append(corner(min(r1, r2), min(c1, c2)))
    return waypoints


def _drag(points, base_x, base_y, width, height, ppi):
    if len(points) < 2:
        raise RuntimeError("连线坐标不足")
    import ctypes
    screen = [(int((float(base_x) + x * ppi) / ppi), int((float(base_y) + y * ppi) / ppi)) for x, y in points]
    win32.manual_motion_on()
    pressed = False
    try:
        ctypes.windll.user32.SetCursorPos(*screen[0])
        sleep(0.15)
        win32.mouse_click(button="left", click_type="down", delay_after=0)
        pressed = True
        for start, end in zip(screen, screen[1:]):
            steps = max(8, int(np.hypot(end[0] - start[0], end[1] - start[1]) / 4))
            for step in range(1, steps + 1):
                ratio = step / steps
                ctypes.windll.user32.SetCursorPos(
                    int(start[0] + (end[0] - start[0]) * ratio),
                    int(start[1] + (end[1] - start[1]) * ratio),
                )
                sleep(0.008)
        win32.mouse_click(button="left", click_type="up", delay_after=0)
        pressed = False
    finally:
        if pressed:
            win32.mouse_click(button="left", click_type="up", delay_after=0)
        win32.manual_motion_off()


def _handle_captcha(web_page, img_ele, confirm_ele, retry=3):
    grid_model_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="fruit_v5.onnx")
    prompt_model_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="prompt_v3.onnx")
    if not grid_model_path:
        raise FileNotFoundError("资源文件中找不到 fruit_v5.onnx")
    if not prompt_model_path:
        raise FileNotFoundError("资源文件中找不到 prompt_v3.onnx")

    connector = FruitConnector(grid_model=grid_model_path, prompt_model=prompt_model_path)
    cache_dir = Path(get_xbot_activity_cache_folder("fruit_connect"))

    for attempt in range(retry):
        image_path = None
        try:
            image_path, (_, _, width, height), (base_x, base_y) = _capture(web_page, img_ele, cache_dir)
            image = _read_image(image_path)
            result = connector.process(image_path)
            positions = [position for group in result["result"] for position in group]
            _drag(
                _routing_waypoints(positions, image.shape[1], image.shape[0]),
                base_x, base_y, width, height, float(get_ppi() or 1),
            )
            web_page.find(confirm_ele, timeout=5).click()
            sleep(1.5)
            return
        except Exception:
            if attempt >= retry - 1:
                raise
            sleep(0.8)
        finally:
            if image_path is not None:
                try:
                    os.remove(image_path)
                except OSError:
                    pass


def test():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active("chrome")
        image_ele = package.selector("test_1")
        commit_ele = package.selector("test_2")
        _handle_captcha(web_page=web_page, img_ele=image_ele, confirm_ele=commit_ele, retry=3)
        exit()


def main(args):
    test()
    args = args or {}
    web_page = args.get("web_page")
    img_ele = args.get("img_ele")
    confirm_ele = args.get("confirm_ele")
    if not web_page or not img_ele or not confirm_ele:
        raise ValueError("web_page、img_ele、confirm_ele 参数不能为空")
    _handle_captcha(
        web_page=web_page,
        img_ele=img_ele,
        confirm_ele=confirm_ele,
        retry=int(args.get("retry", 3)),
    )