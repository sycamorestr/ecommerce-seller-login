#!/usr/bin/env python3
"""Traditional (non-deep-learning) animal matching for ``类型二``.

It compares the reference cards in img_1.png with img_2.png and later using:
  1. the largest foreground component (the animal, not the ``2 x`` text),
  2. a foreground HSV colour histogram,
  3. Hu moments, and
  4. a normalized silhouette, and
  5. a small local-feature cue after the foreground crop.

Install:
    pip install opencv-python numpy

Usage:
    python solve_type2_opencv.py
    python solve_type2_opencv.py --root "C:\\data\\类型二"

Results are stored in ``type2_opencv_matches.json``.  A low score margin is
marked for manual review; this matters when the same animal is drawn in very
different poses.
"""

import argparse
import itertools
import json
import re
from pathlib import Path

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def image_number(path):
    match = re.fullmatch(r"img_(\d+)", path.stem)
    return int(match.group(1)) if match else -1


def group_number(path):
    match = re.fullmatch(r"group_(\d+)", path.name)
    return int(match.group(1)) if match else 10**9


def imread(path):
    """Read paths containing Chinese characters on all Windows OpenCV builds."""
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Cannot read {path}")
    return image


def frame_boxes(image, min_side=35):
    """Return black rectangular card borders as (left, top, right, bottom)."""
    dark = np.max(image, axis=2) < 80
    count, _, stats, _ = cv2.connectedComponentsWithStats(dark.astype(np.uint8), connectivity=4)
    result = []
    for left, top, width, height, pixels in stats[1:count]:
        if pixels < 150 or width < min_side or height < min_side:
            continue
        aspect = width / height
        if 0.55 <= aspect <= 1.8:
            result.append((int(left), int(top), int(left + width), int(top + height)))
    return sorted(result, key=lambda b: (b[1], b[0]))


def crop_card(image, box):
    left, top, right, bottom = box
    inset = max(2, round(min(right - left, bottom - top) * 0.025))
    return image[top + inset : bottom - inset, left + inset : right - inset]


def subject_mask(image):
    """Return the largest coloured/dark foreground component.

    The old implementation returned every coloured component. On a prompt
    card that includes the number and multiplication sign, so the text often
    dominated the colour histogram. In this data the animal is consistently
    the largest connected foreground component after a small close operation.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    foreground = ((hsv[:, :, 1] > 28) | (hsv[:, :, 2] < 145)).astype(np.uint8) * 255
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

    count, labels, stats, _ = cv2.connectedComponentsWithStats(foreground, connectivity=8)
    if count <= 1:
        return foreground
    largest = max(range(1, count), key=lambda index: stats[index, cv2.CC_STAT_AREA])
    return (labels == largest).astype(np.uint8) * 255


def descriptor(image):
    mask = subject_mask(image)
    shape_mask = mask.copy()
    ys, xs = np.where(mask > 0)
    if len(xs):
        padding = 2
        left = max(0, int(xs.min()) - padding)
        right = min(image.shape[1], int(xs.max()) + padding + 1)
        top = max(0, int(ys.min()) - padding)
        bottom = min(image.shape[0], int(ys.max()) + padding + 1)
        image = image[top:bottom, left:right]
        mask = mask[top:bottom, left:right]

    resized = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA)
    resized_mask = cv2.resize(mask, (64, 64), interpolation=cv2.INTER_NEAREST)

    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    histogram = cv2.calcHist([hsv], [0, 1, 2], resized_mask, [12, 6, 6], [0, 180, 0, 256, 0, 256])
    histogram = cv2.normalize(histogram, histogram).flatten()

    # Preserve coarse colour layout as well as the global histogram. This
    # helps distinguish grey marine animals from brown land animals while
    # remaining tolerant to small translations.
    colour_grid = []
    for row in range(2):
        for column in range(2):
            tile = hsv[row * 32 : (row + 1) * 32, column * 32 : (column + 1) * 32]
            tile_mask = resized_mask[row * 32 : (row + 1) * 32, column * 32 : (column + 1) * 32] > 0
            pixels = tile[tile_mask]
            colour_grid.extend(np.r_[pixels.mean(axis=0), pixels.std(axis=0)] if len(pixels) else np.zeros(6))

    silhouette = cv2.resize(mask, (32, 32), interpolation=cv2.INTER_NEAREST).astype(np.float32) / 255.0
    # Calculate moments on the original foreground mask. Resizing the
    # contour to 64x64 introduces quantization noise, especially for the
    # 65x65 candidate thumbnails.
    contours, _ = cv2.findContours(shape_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        contour = max(contours, key=cv2.contourArea)
        hu = cv2.HuMoments(cv2.moments(contour)).flatten()
        hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-30)
    else:
        hu = np.zeros(7, dtype=np.float64)

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=250, fastThreshold=8)
    keypoints, features = orb.detectAndCompute(gray, resized_mask)
    return {
        "histogram": histogram,
        "colour_grid": np.asarray(colour_grid, dtype=np.float32),
        "hu": hu,
        "silhouette": silhouette,
        "features": features,
        "keypoints": len(keypoints),
    }


def reference_descriptors(card):
    """Describe the animal in a prompt card.

    A prompt card also contains a coloured quantity and multiplication sign.
    ``descriptor`` first isolates the largest foreground component, which is
    more reliable here than choosing a fixed left/right crop.
    """
    # The descriptor removes the text by retaining the largest foreground
    # component, so a full-card descriptor is more stable than overlapping
    # left/right crops that may retain part of the number or ``x``.
    return [descriptor(card)]


def orb_similarity(first, second):
    """Return a small exact/local-texture cue after foreground cropping."""
    first_features = first["features"]
    second_features = second["features"]
    if first_features is None or second_features is None:
        return 0.0
    if len(first_features) < 4 or len(second_features) < 4:
        return 0.0
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(first_features, second_features)
    if not matches:
        return 0.0
    good = sum(match.distance < 56 for match in matches)
    return good / max(8, min(len(first_features), len(second_features)))


def similarity(first, second):
    """Combine complementary foreground-only classical features."""
    histogram = max(0.0, cv2.compareHist(first["histogram"], second["histogram"], cv2.HISTCMP_CORREL))
    silhouette = float(1.0 - np.mean(np.abs(first["silhouette"] - second["silhouette"])))
    shape_distance = float(np.linalg.norm(first["hu"] - second["hu"]))
    shape = float(np.exp(-shape_distance / 4.0))
    # H, S, V means/stds for four coarse tiles. The scale converts the
    # channels to comparable units before measuring the feature distance.
    colour_scale = np.tile(np.array([60, 90, 128, 60, 90, 128], dtype=np.float32), 4)
    colour_grid = float(
        np.exp(-np.linalg.norm((first["colour_grid"] - second["colour_grid"]) / colour_scale) / 2.0)
    )
    local = orb_similarity(first, second)
    return 0.10 * histogram + 0.43 * silhouette + 0.05 * shape + 0.23 * colour_grid + 0.19 * local


def assign_references(scores):
    """Assign candidates to reference cards while covering every card.

    Independent nearest-neighbour decisions can assign all four candidates to
    one visually dominant card. A prompt with at least as many candidates as
    cards should contain every referenced species, so choose the highest total
    score among the small (normally 3^4 or 4^4) set of assignments that covers
    all reference cards. If there are fewer candidates, fall back to the
    independent best match.
    """
    candidate_count, reference_count = scores.shape
    if candidate_count < reference_count:
        return tuple(int(index) for index in np.argmax(scores, axis=1))

    best_assignment = None
    best_score = -float("inf")
    for assignment in itertools.product(range(reference_count), repeat=candidate_count):
        if set(assignment) != set(range(reference_count)):
            continue
        total = sum(float(scores[row, column]) for row, column in enumerate(assignment))
        if total > best_score:
            best_score = total
            best_assignment = assignment
    return tuple(best_assignment or np.argmax(scores, axis=1))


def solve_group(group):
    prompt_path = group / "img_1.png"
    candidate_paths = sorted(
        (path for path in group.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS and image_number(path) >= 2),
        key=image_number,
    )
    if not prompt_path.exists() or not candidate_paths:
        return None

    prompt = imread(prompt_path)
    # Prompt cards are much larger than candidate-image borders.  The higher
    # size floor excludes black digits or multiplication signs that otherwise
    # look like tiny rectangles to connected-component detection.
    boxes = frame_boxes(prompt, min_side=90)
    if not boxes:
        raise RuntimeError(f"No reference cards found: {prompt_path}")
    references = [reference_descriptors(crop_card(prompt, box)) for box in boxes]
    candidates = []
    for path in candidate_paths:
        image = imread(path)
        boxes = frame_boxes(image)
        crop = crop_card(image, max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))) if boxes else image
        candidates.append(descriptor(crop))

    score_matrix = np.asarray(
        [[max(similarity(candidate, side) for side in reference) for reference in references] for candidate in candidates],
        dtype=np.float32,
    )
    assignments = assign_references(score_matrix)

    matches = []
    for row, path in enumerate(candidate_paths):
        scores = score_matrix[row]
        order = np.argsort(scores)[::-1]
        best = assignments[row]
        rank = int(np.where(order == best)[0][0])
        second = order[1] if rank == 0 else order[0]
        margin = float(scores[best] - scores[second])
        matches.append(
            {
                "image": path.name,
                "same_animal_as_reference_card": best + 1,
                "similarity": round(float(scores[best]), 4),
                "margin_to_next_reference": round(margin, 4),
                "assignment_mode": "cover_all_references",
                "review_recommended": bool(scores[best] < 0.45 or margin < 0.06),
            }
        )
    return {"group": group.name, "reference_card_count": len(references), "matches": matches}


def main():
    parser = argparse.ArgumentParser(description="Classical OpenCV same-animal matching")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent / "类型二")
    args = parser.parse_args()
    if not args.root.is_dir():
        raise SystemExit(f"Folder does not exist: {args.root}")

    results = []
    groups = sorted((path for path in args.root.iterdir() if path.is_dir() and group_number(path) < 10**9), key=group_number)
    for index, group in enumerate(groups, 1):
        result = solve_group(group)
        if result:
            results.append(result)
        print(f"[{index}/{len(groups)}] {group.name}")

    output = args.root / "type2_opencv_matches.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(results)} groups to {output}")


if __name__ == "__main__":
    main()
