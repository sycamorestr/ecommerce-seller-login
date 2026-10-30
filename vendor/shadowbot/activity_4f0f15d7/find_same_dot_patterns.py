"""找出截图中点数相同的图案。

依赖：opencv-python、numpy
安装：pip install opencv-python numpy
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np


# 识别阈值按题图原始内容尺寸设计；实际截图可以是任意倍率。
# x/y 分开计算，连非等比例 CSS 缩放也可以处理。
DETECTION_SIZE = (445, 430)


def read_image(path: str) -> np.ndarray:
    """支持 Windows 中文路径。"""
    data = np.fromfile(path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"无法读取图片：{path}")
    return image


def write_image(path: str, image: np.ndarray) -> None:
    """支持 Windows 中文路径。"""
    suffix = Path(path).suffix or ".png"
    ok, data = cv2.imencode(suffix, image)
    if not ok:
        raise OSError(f"无法编码图片：{path}")
    data.tofile(path)


def remove_white_frame(image: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
    """去掉截图四周的纯白边框，并返回裁剪偏移量。"""
    non_white = np.min(image, axis=2) < 230
    row_score = non_white.sum(axis=1)
    col_score = non_white.sum(axis=0)
    rows = np.flatnonzero(row_score > image.shape[1] * 0.5)
    cols = np.flatnonzero(col_score > image.shape[0] * 0.5)
    if len(rows) == 0 or len(cols) == 0:
        return image, (0, 0)
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    return image[y0:y1, x0:x1], (x0, y0)


def find_shape_contours(image: np.ndarray) -> list[np.ndarray]:
    """检测浅色的图案主体。高斯模糊可以消除背景中的细纹理。"""
    blurred = cv2.GaussianBlur(image, (9, 9), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 图案主体亮度明显高于背景；截图若缩放过，可调整 150。
    mask = np.where(hsv[:, :, 2] > 150, 255, 0).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        # 过滤背景碎片；这些范围适合题图，可根据图片分辨率按比例调整。
        if 1800 <= area <= 12000 and 40 <= w <= 140 and 40 <= h <= 140:
            result.append(contour)
    return sorted(result, key=lambda c: cv2.boundingRect(c)[1])


def component_candidates(mask: np.ndarray, offset: tuple[int, int]):
    """从二值点图中找圆形小连通区域。"""
    x0, y0 = offset
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        # 高 DPI 缩放后再归一化可能使小点面积略有损失。
        if not (25 <= area <= 350 and 6 <= w <= 25 and 6 <= h <= 25):
            continue

        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter else 0
        if circularity < 0.55:
            continue

        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue
        cx = moments["m10"] / moments["m00"] + x0
        cy = moments["m01"] / moments["m00"] + y0
        candidates.append((cx, cy))

    return candidates


def count_dots(image: np.ndarray, shape: np.ndarray) -> tuple[int, list[tuple[int, int]]]:
    """统计一个图案内的点数，并返回点中心。"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    x, y, w, h = cv2.boundingRect(shape)
    roi = hsv[y : y + h, x : x + w]

    # 彩色点：解决绿色点等亮度不够、但颜色明显的情况。
    color_mask = ((roi[:, :, 1] > 45) & (roi[:, :, 2] < 180)).astype(np.uint8) * 255
    # 深色点：解决灰色/低饱和度的点。
    dark_mask = (roi[:, :, 2] < 150).astype(np.uint8) * 255

    kernel = np.ones((3, 3), np.uint8)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)

    # 用凸包判断点是否大致位于图案内部。对星形尤其重要，因为星形有凹口。
    hull = cv2.convexHull(shape)
    color_candidates = component_candidates(color_mask, (x, y))
    dark_candidates = component_candidates(dark_mask, (x, y))
    candidates = []
    for point in dark_candidates:
        px, py = point
        # 去掉贴近外接矩形边缘的背景纹理。
        if min(px - x, x + w - px, py - y, y + h - py) < 5:
            continue
        if cv2.pointPolygonTest(hull, (float(px), float(py)), False) < 0:
            continue
        candidates.append(point)

    # 颜色检测只补充深色检测漏掉的彩色点；低饱和度区域通常是背景纹理。
    for point in color_candidates:
        px, py = point
        if min(px - x, x + w - px, py - y, y + h - py) < 5:
            continue
        if cv2.pointPolygonTest(hull, (float(px), float(py)), False) < 0:
            continue
        saturation = int(hsv[min(hsv.shape[0] - 1, round(py)), min(hsv.shape[1] - 1, round(px)), 1])
        if saturation < 70:
            continue
        if any(np.hypot(px - qx, py - qy) <= 16 for qx, qy in candidates):
            continue
        candidates.append(point)

    # 两种掩膜可能同时检测到同一个点，按距离合并。
    unique: list[tuple[float, float]] = []
    for point in sorted(candidates, key=lambda p: (p[1], p[0])):
        # 彩色掩膜和深色掩膜对同一个点的中心可能相差几像素。
        if all(np.hypot(point[0] - q[0], point[1] - q[1]) > 14 for q in unique):
            unique.append(point)

    centers = [(round(px), round(py)) for px, py in unique]
    return len(centers), centers


def analyze(image: np.ndarray):
    # 先统一到基准分辨率，避免高 DPI 或网页缩放导致固定像素阈值失效。
    target_width, target_height = DETECTION_SIZE
    x_scale = image.shape[1] / float(target_width)
    y_scale = image.shape[0] / float(target_height)
    if abs(x_scale - 1.0) > 0.03 or abs(y_scale - 1.0) > 0.03:
        detection_image = cv2.resize(
            image,
            (target_width, target_height),
            interpolation=cv2.INTER_AREA
            if max(x_scale, y_scale) > 1
            else cv2.INTER_LINEAR,
        )
    else:
        detection_image = image
        x_scale = 1.0
        y_scale = 1.0

    shapes = find_shape_contours(detection_image)
    result = []
    for contour in shapes:
        count, dots = count_dots(detection_image, contour)
        moments = cv2.moments(contour)
        if moments["m00"]:
            center = (
                round(moments["m10"] / moments["m00"]),
                round(moments["m01"] / moments["m00"]),
            )
        else:
            x, y, w, h = cv2.boundingRect(contour)
            center = (x + w // 2, y + h // 2)

        if x_scale != 1.0 or y_scale != 1.0:
            contour = contour.astype(np.float32)
            contour[:, :, 0] *= x_scale
            contour[:, :, 1] *= y_scale
            contour = np.round(contour).astype(np.int32)
            center = (
                round(center[0] * x_scale),
                round(center[1] * y_scale),
            )
            dots = [
                (round(x * x_scale), round(y * y_scale))
                for x, y in dots
            ]
        result.append({"contour": contour, "center": center, "count": count, "dots": dots})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="输入截图路径")
    parser.add_argument("-o", "--output", default="same_dot_result.png", help="标注结果路径")
    args = parser.parse_args()

    original = read_image(args.image)
    image, (x_offset, y_offset) = remove_white_frame(original)
    results = analyze(image)

    # 把裁剪后的坐标还原为原始截图坐标。
    for item in results:
        item["center"] = (item["center"][0] + x_offset, item["center"][1] + y_offset)
        item["dots"] = [(x + x_offset, y + y_offset) for x, y in item["dots"]]
        item["contour"] = item["contour"] + np.array([[[x_offset, y_offset]]], dtype=np.int32)

    groups = defaultdict(list)
    for item in results:
        groups[item["count"]].append(item["center"])

    print("各点数对应的图案中心坐标（坐标原点为图片左上角）：")
    for count in sorted(groups):
        print(f"  {count} 个点: {groups[count]}")

    print("\n相同点数的图案：")
    for count in sorted(groups):
        if len(groups[count]) >= 2:
            print(f"  {count} 个点 -> {groups[count]}")

    canvas = original.copy()
    for item in results:
        contour = item["contour"]
        center = item["center"]
        count = item["count"]
        cv2.drawContours(canvas, [contour], -1, (0, 0, 255), 2)
        cv2.circle(canvas, center, 4, (255, 0, 0), -1)
        cv2.putText(canvas, str(count), (center[0] - 8, center[1] + 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        for dot in item["dots"]:
            cv2.circle(canvas, dot, 3, (0, 255, 255), 1)

    write_image(args.output, canvas)
    print(f"\n标注结果已保存到：{args.output}")


if __name__ == "__main__":
    main()
