#!/usr/bin/env python3
"""Classify the current 类型二 image set with handcrafted visual templates.

This script does not train or load a machine-learning/deep-learning model.
It compares each candidate against several manually selected examples of every
known class using foreground HSV colour, Hu shape moments, and a normalized
silhouette.  The template
indices refer to the catalogue generated from the current dataset, so this is
purposefully a rule set for this dataset, not a general animal classifier.

Install: pip install opencv-python numpy
Run:     python classify_type2_rule_templates.py
         python classify_type2_rule_templates.py --root "C:\\Users\\think\\Desktop\\zfb"
"""

import json
import hashlib
import itertools
import argparse
from collections import Counter
from pathlib import Path

import numpy as np

from .solve_type2_opencv import crop_card, descriptor, frame_boxes, imread, similarity

# Manually verified representatives from type2_contact_sheets.  More than one
# pose/view is retained for every category, which is essential for matching
# traditional (non-semantic) visual features.
TEMPLATE_INDICES = {
    "鲸": [
        1,
        14,
        15,
        21,
        26,
        28,
        55,
        62,
        76,
        95,
        100,
        128,
        137,
        138,
        158,
        160,
        186,
        189,
        200,
        214,
        228,
        231,
        257,
        258,
        261,
        275,
        278,
        286,
        303,
    ],
    "猴": [
        2,
        4,
        17,
        20,
        22,
        30,
        32,
        33,
        36,
        41,
        45,
        46,
        61,
        63,
        88,
        92,
        93,
        96,
        110,
        113,
        114,
        118,
        152,
        169,
        177,
        182,
        207,
        210,
        230,
        232,
        233,
        262,
        263,
        266,
        283,
        293,
        295,
    ],
    "狮": [
        3,
        16,
        23,
        24,
        31,
        37,
        39,
        42,
        44,
        50,
        59,
        60,
        68,
        78,
        80,
        85,
        102,
        105,
        106,
        109,
        117,
        119,
        124,
        135,
        141,
        175,
        178,
        181,
        185,
        187,
        190,
        193,
        195,
        202,
        204,
        205,
        220,
        227,
        240,
        242,
        250,
        251,
        253,
        255,
        265,
        268,
    ],
    "熊": [
        5,
        11,
        18,
        27,
        35,
        40,
        49,
        52,
        53,
        56,
        66,
        67,
        69,
        81,
        82,
        91,
        115,
        122,
        125,
        127,
        129,
        132,
        147,
        153,
        155,
        166,
        176,
        183,
        201,
        209,
        211,
        217,
        218,
        222,
        229,
        249,
        254,
        269,
        272,
        281,
        291,
        299,
        302,
    ],
    "草莓": [
        6,
        7,
        9,
        12,
        38,
        54,
        57,
        64,
        65,
        74,
        75,
        86,
        87,
        94,
        103,
        104,
        108,
        116,
        120,
        131,
        140,
        162,
        170,
        172,
        179,
        180,
        198,
        219,
        235,
        236,
        237,
        241,
        243,
        244,
        256,
        259,
        264,
        288,
        296,
        301,
        304,
    ],
    "兔": [
        8,
        10,
        43,
        48,
        83,
        89,
        90,
        98,
        99,
        101,
        126,
        133,
        139,
        143,
        144,
        146,
        151,
        156,
        159,
        161,
        163,
        167,
        168,
        171,
        173,
        174,
        188,
        194,
        197,
        199,
        206,
        208,
        212,
        215,
        223,
        225,
        226,
        245,
        248,
        252,
        260,
        274,
        276,
        280,
        294,
    ],
    "海豹": [
        13,
        19,
        47,
        58,
        70,
        72,
        77,
        97,
        107,
        130,
        149,
        150,
        157,
        164,
        165,
        184,
        191,
        192,
        203,
        213,
        216,
        221,
        224,
        238,
        239,
        246,
        267,
        270,
        282,
        284,
        289,
        300,
    ],
    "鹿": [
        25,
        29,
        34,
        51,
        71,
        73,
        79,
        84,
        111,
        112,
        121,
        123,
        134,
        136,
        142,
        145,
        148,
        154,
        196,
        234,
        247,
        271,
        273,
        277,
        279,
        285,
        287,
        290,
        292,
        297,
        298,
    ],
}


def classify_dataset(root, template_root=None, output_path=None):
    root = Path(root).resolve()
    template_root = Path(
        template_root or (Path(__file__).resolve().parent / "类型二")
    ).resolve()
    paths = sorted(root.glob("group_*/img_[2-9].png"))
    if not paths:
        raise SystemExit(f"No candidate images found in {root}")

    # Index-to-file order is identical to the contact-sheet catalogue: retain
    # only the first occurrence of every byte-identical icon.
    unique = {}
    template_paths = sorted(template_root.glob("group_*/img_[2-9].png"))
    for path in template_paths:
        unique.setdefault(hashlib.sha256(path.read_bytes()).hexdigest(), path)
    catalogue_paths = list(unique.values())
    catalogue_index = {
        hashlib.sha256(path.read_bytes()).hexdigest(): index
        for index, path in enumerate(catalogue_paths, 1)
    }

    features = {}
    for index, path in enumerate(catalogue_paths, 1):
        image = imread(path)
        boxes = frame_boxes(image)
        crop = (
            crop_card(image, max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])))
            if boxes
            else image
        )
        features[index] = descriptor(crop)

    templates = {
        name: [features[index] for index in indices]
        for name, indices in TEMPLATE_INDICES.items()
    }
    # Compute every traditional-feature comparison just once. The same
    # catalogue is used by normal classification and leave-one-out QA.
    size = len(catalogue_paths)
    scores_matrix = np.eye(size, dtype=np.float32)
    for first in range(1, size + 1):
        for second in range(first + 1, size + 1):
            score = similarity(features[first], features[second])
            scores_matrix[first - 1, second - 1] = score
            scores_matrix[second - 1, first - 1] = score

    def category_scores(index):
        """Score a catalogue icon without allowing the icon to match itself."""
        result = {}
        for name, indices in TEMPLATE_INDICES.items():
            eligible = [other for other in indices if other != index]
            if not eligible:
                eligible = indices
            result[name] = float(
                scores_matrix[index - 1, np.asarray(eligible) - 1].max()
            )
        return result

    def descriptor_category_scores(current):
        """Classify a non-catalogue descriptor against the category gallery."""
        return {
            name: max(similarity(current, template) for template in gallery)
            for name, gallery in templates.items()
        }

    def image_descriptor(path):
        image = imread(path)
        boxes = frame_boxes(image)
        crop = (
            crop_card(image, max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])))
            if boxes
            else image
        )
        return descriptor(crop)

    results = []
    for path in paths:
        icon_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        index = catalogue_index.get(icon_hash)
        if index is None:
            # New test images do not have to be byte-identical to the template
            # gallery. Describe them directly and compare against every
            # category gallery instead of looking up a catalogue index.
            current = image_descriptor(path)
            scores = descriptor_category_scores(current)
            match_mode = "unseen_image_template_gallery"
        else:
            current = features[index]
            scores = category_scores(index)
            match_mode = "catalogue_template_leave_one_out"
        ranked = sorted(scores, key=scores.get, reverse=True)
        best, next_best = ranked[:2]
        score = scores[best]
        margin = score - scores[next_best]
        results.append(
            {
                "group": path.parent.name,
                "image": path.name,
                "category": best,
                "catalogue_index": index,
                "match_mode": match_mode,
                "similarity": round(float(score), 4),
                "margin": round(float(margin), 4),
                "review_recommended": bool(score < 0.52 or margin < 0.04),
            }
        )

    # A genuine feature-only check: remove each icon from its own class gallery
    # and ask whether the remaining templates still identify its class.
    truth = {
        index: name for name, indices in TEMPLATE_INDICES.items() for index in indices
    }
    validation_total = validation_correct = 0
    validation_by_class = {
        name: {"correct": 0, "total": 0} for name in TEMPLATE_INDICES
    }
    for index, current in features.items():
        scores = category_scores(index)
        predicted = max(scores, key=scores.get)
        expected = truth[index]
        validation_total += 1
        validation_correct += predicted == expected
        validation_by_class[expected]["total"] += 1
        validation_by_class[expected]["correct"] += predicted == expected

    groups = []
    for group in sorted(
        {item["group"] for item in results}, key=lambda x: int(x.split("_")[1])
    ):
        items = [item for item in results if item["group"] == group]
        prompt_path = root / group / "img_1.png"
        reference_cards = []
        if prompt_path.exists():
            prompt = imread(prompt_path)
            boxes = frame_boxes(prompt, min_side=90)
            reference_descriptors = [
                descriptor(crop_card(prompt, box)) for box in boxes
            ]
            candidate_categories = sorted({item["category"] for item in items})
            candidate_paths = {
                item["image"]: root / group / item["image"] for item in items
            }
            candidate_features = {
                item["image"]: descriptor(
                    crop_card(
                        imread(candidate_paths[item["image"]]),
                        max(
                            frame_boxes(imread(candidate_paths[item["image"]])),
                            key=lambda box: (box[2] - box[0]) * (box[3] - box[1]),
                        ),
                    )
                    if frame_boxes(imread(candidate_paths[item["image"]]))
                    else imread(candidate_paths[item["image"]])
                )
                for item in items
            }
            category_scores_by_reference = [
                {
                    category: max(
                        similarity(reference, candidate_features[item["image"]])
                        for item in items
                        if item["category"] == category
                    )
                    for category in candidate_categories
                }
                for reference in reference_descriptors
            ]
            reference_category_scores = [
                descriptor_category_scores(reference)
                for reference in reference_descriptors
            ]

            # Infer the species of the prompt-card animals jointly with the
            # candidate labels. If there are enough distinct candidate species,
            # use every reference card once; this prevents one strong-looking
            # category from absorbing all prompt cards.
            if candidate_categories and len(candidate_categories) >= len(
                reference_descriptors
            ):
                assignments = itertools.permutations(
                    candidate_categories, len(reference_descriptors)
                )
                best_assignment = max(
                    assignments,
                    key=lambda assignment: sum(
                        category_scores_by_reference[index][category]
                        + 0.75
                        * reference_category_scores[index].get(category, 0.0)
                        for index, category in enumerate(assignment)
                    ),
                )
            else:
                best_assignment = tuple(
                    max(scores, key=scores.get)
                    for scores in category_scores_by_reference
                )

            for index, (box, current, inferred) in enumerate(
                zip(boxes, reference_descriptors, best_assignment), 1
            ):
                visual_scores = reference_category_scores[index - 1]
                visual_ranked = sorted(
                    visual_scores, key=visual_scores.get, reverse=True
                )
                reference_cards.append(
                    {
                        "reference_card": index,
                        "box": list(box),
                        "category": inferred,
                        "category_inference_mode": "mutual_candidate_gallery",
                        "visual_only_category": visual_ranked[0],
                        "visual_only_similarity": round(
                            float(visual_scores[visual_ranked[0]]), 4
                        ),
                        "visual_only_margin": round(
                            float(
                                visual_scores[visual_ranked[0]]
                                - visual_scores[visual_ranked[1]]
                            ),
                            4,
                        ),
                    }
                )

            # Attach the actual reference-card match to every candidate. The
            # gallery category is useful as a prior, but a clearly stronger
            # direct candidate-to-reference similarity must be allowed to
            # correct an unseen-image category mistake.
            for item in items:
                compatible = [
                    index
                    for index, card in enumerate(reference_cards)
                    if card["category"] == item["category"]
                ]
                candidate = candidate_features[item["image"]]
                visual_scores = [
                    similarity(candidate, reference)
                    for reference in reference_descriptors
                ]
                visual_best = (
                    max(
                        range(len(reference_cards)),
                        key=lambda index: visual_scores[index],
                    )
                    if reference_cards
                    else None
                )
                category_best = (
                    max(compatible, key=lambda index: visual_scores[index])
                    if compatible
                    else None
                )
                best_card = category_best
                if visual_best is not None and category_best is None:
                    item["category_before_reference_match"] = item["category"]
                    item["category"] = reference_cards[visual_best]["category"]
                    item["review_recommended"] = True
                    best_card = visual_best
                    item["species_match_mode"] = "reference_visual_fallback"
                elif visual_best is not None and visual_best != category_best:
                    visual_gap = (
                        visual_scores[visual_best] - visual_scores[category_best]
                    )
                    if visual_gap >= 0.15:
                        item["category_before_reference_match"] = item["category"]
                        item["category"] = reference_cards[visual_best]["category"]
                        item["review_recommended"] = True
                        best_card = visual_best
                        item["species_match_mode"] = "reference_visual_override"
                item["matched_reference_card"] = (
                    None if best_card is None else best_card + 1
                )
                item["same_species_as_reference"] = bool(
                    best_card is not None
                    and item["category"] == reference_cards[best_card]["category"]
                )
                item.setdefault("species_match_mode", "category_then_visual_tiebreak")

        groups.append(
            {
                "group": group,
                "counts": dict(Counter(item["category"] for item in items)),
                "reference_cards": reference_cards,
                "images": items,
            }
        )

    output = (
        Path(output_path).resolve()
        if output_path
        else root / "type2_rule_classification.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "method": "manually curated category templates; foreground HSV + colour layout + Hu moments + silhouette + ORB; no machine learning",
        "known_categories": list(TEMPLATE_INDICES),
        "catalogue_unique_icons": len(catalogue_paths),
        "leave_one_icon_out_feature_accuracy": round(
            validation_correct / validation_total, 4
        ),
        "leave_one_icon_out_by_category": validation_by_class,
        "groups": groups,
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    review = sum(item["review_recommended"] for item in results)
    print(f"Classified {len(results)} images in {len(groups)} groups; review={review}")
    print(f"Saved {output}")
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Classify type2 images with handcrafted visual templates"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent / "类型二",
        help="测试图片根目录，目录下应包含 group_*/img_*.png",
    )
    parser.add_argument(
        "--template-root",
        type=Path,
        default=Path(__file__).resolve().parent / "类型二",
        help="模板图库根目录；默认使用项目内的 类型二",
    )
    args = parser.parse_args()
    classify_dataset(args.root, args.template_root)


if __name__ == "__main__":
    main()
