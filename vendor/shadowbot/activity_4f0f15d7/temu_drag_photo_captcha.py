import xbot
import xbot_visual
from xbot import print, sleep, win32, web
from . import package
import json
import os
import base64
import ctypes
import math
import random
import sqlite3
from pathlib import Path
import re
import tempfile
import time
from urllib.parse import urljoin
import cv2
import numpy as np
import requests
from .classify_type2_rule_templates import classify_dataset

TRACK_DATABASE_NAME = "downward_trajectories.db"
# TRACK_DATABASE_FALLBACK = (
#     r"D:\download\temu_1\mouse_trajectory_recorder\downward_trajectories.db"
# )


def _log(message):
    """Use ShadowBot logging when available, but remain locally runnable."""
    try:
        import xbot

        xbot.logging.info(message)
    except Exception:
        print(message)


def _as_path(value, default=None):
    if value is None or str(value).strip() == "":
        return default
    return Path(os.path.expandvars(os.path.expanduser(str(value)))).resolve()


def _load_payload(output_path):
    if not output_path.is_file():
        raise FileNotFoundError(f"识别结果文件不存在: {output_path}")
    with output_path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError("识别结果不是 JSON 对象")
    return payload


def _summarize(payload, output_path):
    groups = payload.get("groups") or []
    images = [image for group in groups for image in group.get("images", [])]
    return {
        "success": True,
        "output_path": str(output_path),
        "groups": groups,
        "images": images,
        "review_count": sum(bool(image.get("review_recommended")) for image in images),
        "payload": payload,
    }


def _resolve_element(web_page, element, timeout=5):
    if hasattr(element, "get_bounding"):
        return element
    if web_page is None or not element:
        return None
    try:
        if isinstance(element, str):
            text = element.strip()
            if text.startswith("/") or text.startswith("./") or text.startswith("("):
                return web_page.find_by_xpath(text)
            return web_page.find(element, timeout=timeout)
        return web_page.find(element, timeout=timeout)
    except Exception:
        return None


def _read_attr(node, name):
    try:
        return node.get_attribute(name)
    except Exception:
        return None


def _is_image_node(node):
    tag_name = _read_attr(node, "tagName") or _read_attr(node, "localName")
    if tag_name:
        return str(tag_name).lower() == "img"
    return bool(_read_attr(node, "src"))


def _node_style(node):
    return _read_attr(node, "style") or ""


def _image_url(element):
    image_node = element
    try:
        if not _read_attr(image_node, "src"):
            image_node = element.find_by_xpath(
                ".//img[@src or @data-src or @currentSrc]"
            )
    except Exception:
        pass
    for attr in ("currentSrc", "src", "data-src", "data-original", "data-lazy-src"):
        value = _read_attr(image_node, attr)
        if value:
            return value
    style = _node_style(image_node) or _node_style(element)
    matched = re.search(r"url\((['\"]?)(.*?)\1\)", style)
    return matched.group(2) if matched else None


def _write_bytes(path, data):
    with open(path, "wb") as stream:
        stream.write(data)


def _download_image(web_page, element, path):
    source = _image_url(element)
    if not source:
        return False, None
    source = source.strip()
    try:
        if source.startswith("data:image/"):
            _, encoded = source.split(",", 1)
            _write_bytes(path, base64.b64decode(encoded))
            return True, "data:image"
        url = urljoin(getattr(web_page, "url", "") or "", source)
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": getattr(web_page, "url", "") or "",
            },
            timeout=15,
        )
        if response.status_code == 200 and response.content:
            _write_bytes(path, response.content)
            return True, url
    except Exception as exc:
        _log("下载类型二图片失败: %s" % exc)
    return False, source


def _capture_element(element, path):
    try:
        from xbot import win32

        x, y, width, height = element.get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(
            str(path),
            "png",
            int(x),
            int(y),
            int(x + width),
            int(y + height),
        )
        return True
    except Exception as exc:
        _log("截图类型二图片失败: %s" % exc)
        return False


def _screen_scale():
    try:
        from .utils import get_ppi

        return get_ppi()
    except Exception:
        try:
            from utils import get_ppi

            return get_ppi()
        except Exception:
            return 1


def _screen_rect(node):
    # Match dewu_captcha.py: use the browser element coordinates directly.
    # Multiplying get_bounding(to96dpi=False) by PPI here caused a second
    # scaling on some ShadowBot/browser DPI configurations.
    x, y, width, height = node.get_bounding()
    return x, y, width, height


def _screen_center(node):
    x, y, width, height = _screen_rect(node)
    return int(x + width / 2), int(y + height / 2)


def _randomized_point(point_x, point_y):
    """Add an independent -15..15 pixel offset to a screen coordinate."""
    return (
        int(point_x) + random.randint(-15, 15),
        int(point_y) + random.randint(-15, 15),
    )


def _randomized_center(node):
    center_x, center_y = _screen_center(node)
    return _randomized_point(center_x, center_y)


def _click_node_randomized(node):
    click_x, click_y = _randomized_center(node)
    _move_to(click_x, click_y)
    sleep(0.05)
    win32.mouse_click()


def _image_size(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("无法读取参考图片尺寸: %s" % path)
    return image.shape[1], image.shape[0]


def _move_to(point_x, point_y):
    """Move the Windows cursor exactly like the reference captcha script."""
    if os.name == "nt":
        ctypes.windll.user32.SetCursorPos(int(point_x), int(point_y))
    else:
        win32.mouse_move(
            point_x=int(point_x), point_y=int(point_y), move_speed="instant"
        )


def _trajectory_database_path():
    """Use the local recorder DB, with the ShadowBot resource as fallback."""
    candidates = []
    try:
        resource_path = xbot_visual.resourcesfile.get_resourcesfile_path(
            file_name=TRACK_DATABASE_NAME
        )
        if resource_path:
            candidates.append(Path(resource_path))
    except Exception:
        pass
    for candidate in candidates:
        if candidate.is_file():
            return candidate


def _trajectory_bucket(angle):
    """Map the actual start-to-target angle to the five recorded angle bins."""
    angle = max(-90.0, min(90.0, float(angle)))
    if angle >= 60:
        return 60
    if angle >= 30:
        return 30
    if angle > -30:
        return 0
    if angle > -60:
        return -30
    return -60


def _target_angle(start_x, start_y, target_x, target_y):
    offset_x = float(target_x) - float(start_x)
    offset_y = float(target_y) - float(start_y)
    if abs(offset_x) < 0.001 and abs(offset_y) < 0.001:
        return 0.0
    # 0 degrees is straight down; positive values point to the right.
    return math.degrees(math.atan2(offset_x, offset_y))


def _read_trajectory(angle_bucket):
    """Read one random trace for the selected target-angle bucket."""
    database_path = _trajectory_database_path()
    connection = sqlite3.connect(str(database_path))
    try:
        rows = connection.execute(
            """
            SELECT points_json, final_x, final_y
            FROM downward_tracks
            WHERE target_angle_deg = ?
            ORDER BY id
            """,
            (float(angle_bucket),),
        ).fetchall()
    finally:
        connection.close()
    if not rows:
        raise RuntimeError(
            "轨迹数据库中没有 %d° 轨迹，请先录制对应角度的轨迹" % angle_bucket
        )
    row = random.choice(rows)
    points = json.loads(row[0])
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("轨迹数据库中的 %d° 轨迹点无效" % angle_bucket)
    recorded_x = float(points[-1][0])
    recorded_y = float(points[-1][1])
    return points, recorded_x, recorded_y


def _scale_trajectory(points, recorded_x, recorded_y, target_x, target_y):
    """Scale a recorded trace so its final point equals the real target point."""
    scale_x = float(target_x) / recorded_x if abs(recorded_x) > 0.001 else 0.0
    scale_y = float(target_y) / recorded_y if abs(recorded_y) > 0.001 else 0.0
    scaled = []
    for point in points:
        scaled.append(
            [
                int(round(float(point[0]) * scale_x)),
                int(round(float(point[1]) * scale_y)),
                max(0.0, float(point[2])),
            ]
        )
    scaled[-1][0] = int(round(target_x))
    scaled[-1][1] = int(round(target_y))
    return scaled


def _drag_node_by_trajectory(
    node, target_x, target_y, angle_bucket, start_point=None
):
    if start_point is None:
        start_x, start_y = _randomized_center(node)
    else:
        start_x, start_y = start_point
    points, recorded_x, recorded_y = _read_trajectory(angle_bucket)
    relative_target_x = float(target_x) - start_x
    relative_target_y = float(target_y) - start_y
    scaled_points = _scale_trajectory(
        points,
        recorded_x,
        recorded_y,
        relative_target_x,
        relative_target_y,
    )

    win32.manual_motion_on()
    try:
        _move_to(start_x, start_y)
        win32.mouse_click(button="left", click_type="down")
        for offset_x, offset_y, delta_ms in scaled_points:
            _move_to(start_x + offset_x, start_y + offset_y)
            sleep(float(delta_ms) / 2000.0)
        _move_to(target_x, target_y)
    finally:
        win32.mouse_click(button="left", click_type="up")
        win32.manual_motion_off()


def drag_type2_matches(
    prompt_node,
    candidate_nodes,
    prompt_path,
    group_result,
    drag_only_matched=True,
    drag_duration=0.5,
    drag_pause=0.35,
):
    """Drag matched candidate nodes to the corresponding prompt-card centers."""
    reference_cards = group_result.get("reference_cards") or []
    image_results = group_result.get("images") or []
    if not reference_cards or not image_results:
        raise RuntimeError("识别结果中没有参考卡或候选图，无法执行拖拽")

    image_width, image_height = _image_size(prompt_path)
    prompt_x, prompt_y, prompt_width, prompt_height = _screen_rect(prompt_node)
    targets = {}
    for card in reference_cards:
        box = card.get("box") or []
        if len(box) != 4:
            continue
        center_x = (float(box[0]) + float(box[2])) / 2.0
        center_y = (float(box[1]) + float(box[3])) / 2.0
        targets[int(card["reference_card"])] = (
            int(prompt_x + center_x / image_width * prompt_width),
            int(prompt_y + center_y / image_height * prompt_height),
        )

    dragged = 0
    for item in image_results:
        image_name = item.get("image", "")
        if not image_name.startswith("img_"):
            continue
        candidate_index = int(Path(image_name).stem.split("_")[-1]) - 2
        if candidate_index < 0 or candidate_index >= len(candidate_nodes):
            # _log("找不到候选图网页节点: %s" % image_name)
            continue
        if drag_only_matched and not item.get("same_species_as_reference"):
            # _log("跳过未匹配候选图: %s (%s)" % (image_name, item.get("category")))
            continue
        reference_card = item.get("matched_reference_card")
        if reference_card not in targets:
            # _log("找不到参考卡目标: %s -> %s" % (image_name, reference_card))
            continue
        target_x, target_y = targets[reference_card]
        start_x, start_y = _randomized_center(candidate_nodes[candidate_index])
        target_x, target_y = _randomized_point(target_x, target_y)
        angle = _target_angle(start_x, start_y, target_x, target_y)
        angle_bucket = _trajectory_bucket(angle)
        # _log(
        #     "类型二拖动: %s -> 参考卡%d, start=(%d,%d), target=(%d,%d), angle=%.2f°, bucket=%d°"
        #     % (
        #         image_name,
        #         reference_card,
        #         start_x,
        #         start_y,
        #         target_x,
        #         target_y,
        #         angle,
        #         angle_bucket,
        #     )
        # )
        _drag_node_by_trajectory(
            candidate_nodes[candidate_index],
            target_x,
            target_y,
            angle_bucket,
            start_point=(start_x, start_y),
        )
        dragged += 1
        sleep(float(drag_pause))
        # _log("已拖拽 %s -> 参考卡%d" % (image_name, reference_card))
    # _log("类型二拖拽完成: %d 张" % dragged)


def _find_image_nodes(web_page, image_ele, image_xpath=".//img", max_images=9):
    container = _resolve_element(web_page, image_ele)
    if container is None:
        raise ValueError("找不到 image_ele 对应的网页元素")
    try:
        nodes = container.find_all_by_xpath(image_xpath or ".//img") or []
    except Exception:
        nodes = []
    try:
        if (
            _is_image_node(container)
            and _image_url(container)
            and all(node is not container for node in nodes)
        ):
            nodes.insert(0, container)
    except Exception:
        pass

    sortable = []
    for node in nodes:
        try:
            x, y, width, height = node.get_bounding(to96dpi=False)
            sortable.append((round(y / 20.0), x, node))
        except Exception:
            continue
    sortable.sort(key=lambda item: (item[0], item[1]))
    nodes = [item[2] for item in sortable]
    if max_images:
        nodes = nodes[: int(max_images)]
    if len(nodes) < 2:
        raise ValueError(
            "类型二至少需要 1 张参考图和 1 张候选图，请检查 image_ele 或 image_xpath"
        )
    return nodes


def capture_type2_images(
    web_page,
    image_ele,
    image_xpath=".//img",
    max_images=9,
    cache_dir=None,
    capture_mode="auto",
):
    """Capture img_1 (reference) and img_2... (candidates) from a page."""
    nodes = _find_image_nodes(web_page, image_ele, image_xpath, max_images)
    base_dir = _as_path(cache_dir, Path(tempfile.gettempdir()) / "temu_type2_species")
    run_dir = base_dir / ("run_%d" % int(time.time() * 1000))
    group_dir = run_dir / "group_1"
    group_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    sources = []
    for index, node in enumerate(nodes, 1):
        path = group_dir / ("img_%d.png" % index)
        downloaded = False
        source = None
        if capture_mode != "screenshot":
            downloaded, source = _download_image(web_page, node, path)
        if not downloaded:
            if not _capture_element(node, path):
                raise RuntimeError("无法保存第 %d 张类型二图片" % index)
            source = "screenshot"
        paths.append(str(path))
        sources.append({"index": index, "path": str(path), "source": source})
    return str(run_dir), paths, sources, nodes


def run_type2_from_web(
    web_page,
    image_ele,
    commit_ele=None,
    image_xpath=".//img",
    max_images=9,
    cache_dir=None,
    capture_mode="auto",
    template_root=None,
    output_path=None,
    drag_after_match=True,
    drag_only_matched=False,
    drag_duration=0.5,
    drag_pause=0.35,
):
    for _ in range(5):

        try:
            web_page.find(image_ele, timeout=2)
        except:
            break

        run_root, paths, sources, nodes = capture_type2_images(
            web_page,
            image_ele,
            image_xpath=image_xpath,
            max_images=max_images,
            cache_dir=cache_dir,
            capture_mode=capture_mode,
        )
        result = run_type2_classification(
            root=run_root,
            template_root=template_root,
            output_path=output_path,
        )
        if drag_after_match:
            groups = result.get("groups") or []
            if not groups:
                raise RuntimeError("类型二识别没有生成分组结果，无法拖拽")
            drag_type2_matches(
                prompt_node=nodes[0],
                candidate_nodes=nodes[1:],
                prompt_path=Path(run_root) / "group_1" / "img_1.png",
                group_result=groups[0],
                drag_only_matched=drag_only_matched,
                drag_duration=drag_duration,
                drag_pause=drag_pause,
            )
        if commit_ele:
            commit_target = _resolve_element(web_page, commit_ele)
            if commit_target is None:
                raise ValueError("找不到 confirm_ele/commit_ele 对应的确认元素")
            _click_node_randomized(commit_target)

        sleep(3)


def run_type2_classification(
    root,
    template_root=None,
    output_path=None,
):
    """Run the feature-only classifier through the same-directory import."""
    root_path = _as_path(root)
    if root_path is None or not root_path.is_dir():
        raise NotADirectoryError(f"图片根目录不存在: {root}")

    template_path = _as_path(template_root, Path(__file__).resolve().parent / "类型二")
    if template_path is None or not template_path.is_dir():
        raise NotADirectoryError(f"模板图库不存在: {template_path}")

    result_path = _as_path(output_path, root_path / "type2_rule_classification.json")
    if result_path is None:
        result_path = root_path / "type2_rule_classification.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)

    # _log("开始执行类型二物种识别: %s" % root_path)
    payload = classify_dataset(root_path, template_path, result_path)
    result = _summarize(payload, result_path)
    # _log(
    # "类型二识别完成: groups=%s, images=%s, review=%s"
    # % (len(result["groups"]), len(result["images"]), result["review_count"])
    # )
    return result


def test():
    if "xbot_extensions" not in __file__:
        web_page = web.get_active("chrome")
        image_ele = package.selector("temu_1")
        commit_ele = package.selector("temu_2")
        run_type2_from_web(web_page, image_ele, commit_ele)
        exit()


def main(args):
    """ShadowBot custom-instruction entry point."""
    test()
    web_page = args.get("web_page")
    image_ele = args.get("image_ele")
    if web_page is None or image_ele is None:
        raise ValueError("请传入 web_page 和 image_ele")
    run_type2_from_web(
        web_page=web_page,
        image_ele=image_ele,
        commit_ele=args.get("commit_ele") or args.get("confirm_ele"),
        image_xpath=args.get("image_xpath", ".//img"),
        max_images=int(args.get("max_images", 9)),
        cache_dir=args.get("cache_dir"),
        capture_mode=args.get("capture_mode", "auto"),
        template_root=args.get("template_root"),
        output_path=args.get("output_path"),
        drag_after_match=args.get("drag_after_match", True),
        drag_only_matched=args.get("drag_only_matched", True),
        drag_duration=float(args.get("drag_duration", 0.5)),
        drag_pause=float(args.get("drag_pause", 0.35)),
    )
