import os
import json
import http.client
import time


import xbot  # type: ignore
import xbot_visual  # type: ignore


if os.name == "nt":
    from ctypes import windll

from urllib.parse import urlparse
from xbot._core import robot  # type: ignore
from xbot import sleep, win32  # type: ignore
from xbot.web.element import WebElement  # type: ignore
from xbot.selector import Selector

from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {"Content-Type": "application/json"}
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload):
    # 判断客户端版本, 是否使用ssl, host, 以及token
    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.hostname


    if is_ssl:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)

    payload = json.dumps(
        {
            "aiToolInterfaceCodeId": "jfbym_22222",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "22222",
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {"image": payload.get("image")},
            },
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    conn.request("POST", "/api/v2/aiservice/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json.get("data")


def drag(drag_ele: WebElement, distance: int, target_ele: Selector, web_page: xbot.web.WebBrowser):
    x, y, width, height = drag_ele.get_bounding()
    drag_start_x = x + width / 2
    drag_start_y = y + height / 2
    drag_ele.hover()
    move_speed = "middle"
    win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.1,
        max_time=0.5,
    )
    win32.mouse_move(drag_start_x, drag_start_y, move_speed=move_speed, delay_after=1 / 2000)

    # 获取缺口元素初始位置
    x_1, y_1, width_1, height_1 = web_page.find(target_ele).get_bounding()
    gap_start_x = x_1 + width_1 / 2
    print(f'缺口初始位置 target_distance: {gap_start_x}')
    print(f'目标移动距离 distance: {distance}')

    max_iterations = 60  # 最大拖动次数，防止死循环
    timeout_seconds = 30
    tolerance = 2
    start_time = time.time()
    iteration = 0
    last_gap_moved = 0.0
    stagnant_count = 0

    # 记录已知的“拖动量 -> 缺口移动量”区间，用于后续插值/二分逼近
    lower_drag_total = 0.0
    lower_gap_moved = 0.0
    upper_drag_total = None
    upper_gap_moved = None

    # 第一次先拖一小段，再根据测量结果校正
    next_drag_total = max(6.0, min(float(distance), max(12.0, float(distance) * 0.5)))

    try:
        win32.mouse_click(button="left", click_type="down", delay_after=0)

        current_mouse_x = drag_start_x
        current_mouse_y = drag_start_y

        while iteration < max_iterations:
            iteration += 1

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                print(f'超时退出：已运行 {elapsed_time:.2f} 秒，超过 {timeout_seconds} 秒限制')
                break

            current_drag_total = current_mouse_x - drag_start_x
            desired_delta = next_drag_total - current_drag_total

            if abs(desired_delta) < 0.5:
                desired_delta = 1.0 if distance > last_gap_moved else -1.0

            # 每次只拖一小段，允许回拉，回拉步长略小一些
            if desired_delta > 0:
                step = max(1.0, min(16.0, desired_delta))
            else:
                step = -max(1.0, min(12.0, abs(desired_delta)))

            next_mouse_x = current_mouse_x + step
            print(f'第{iteration}次循环 - 当前累计拖动: {current_drag_total:.2f}, 本次步长: {step:.2f}, 计划累计拖动: {next_drag_total:.2f}')
            print(f'鼠标当前位置: {current_mouse_x:.2f}, 下一步目标位置: {next_mouse_x:.2f}')
            win32.mouse_move(next_mouse_x, current_mouse_y, move_speed=move_speed, delay_after=1 / 2000)
            current_mouse_x = next_mouse_x
            sleep(0.03)

            # 重新测量缺口元素移动距离
            x_2, y_2, width_2, height_2 = web_page.find(target_ele).get_bounding()
            gap_current_x = x_2 + width_2 / 2
            gap_moved = gap_current_x - gap_start_x
            error = distance - gap_moved
            current_drag_total = current_mouse_x - drag_start_x
            print(f'第{iteration}次测量 - 鼠标累计拖动: {current_drag_total:.2f}, 缺口已移动距离: {gap_moved:.2f}, 当前误差: {error:.2f}')

            if abs(error) <= tolerance:
                print('达到目标位置，退出循环')
                break

            # 更新停滞检测
            if abs(gap_moved - last_gap_moved) < 0.5:
                stagnant_count += 1
            else:
                stagnant_count = 0

            # 根据“鼠标累计拖动 -> 缺口移动距离”的测量结果维护上下边界
            if gap_moved < distance:
                lower_drag_total = current_drag_total
                lower_gap_moved = gap_moved
            else:
                upper_drag_total = current_drag_total
                upper_gap_moved = gap_moved

            # 有上下界时优先在区间内插值/二分；没有上下界时按当前测得比例估算
            if upper_drag_total is not None and upper_gap_moved is not None:
                gap_span = upper_gap_moved - lower_gap_moved
                drag_span = upper_drag_total - lower_drag_total
                if abs(gap_span) > 0.5 and abs(drag_span) > 0.5:
                    next_drag_total = lower_drag_total + (distance - lower_gap_moved) * drag_span / gap_span
                else:
                    next_drag_total = (lower_drag_total + upper_drag_total) / 2

                next_drag_total = max(lower_drag_total + 0.5, min(upper_drag_total - 0.5, next_drag_total))
            else:
                if abs(gap_moved) > 1:
                    drag_gap_ratio = current_drag_total / gap_moved
                else:
                    drag_gap_ratio = 1.0

                next_drag_total = current_drag_total + error * drag_gap_ratio * 0.9

            # 临近目标时进一步缩小调节量，避免刚过线又大幅回拉
            if abs(error) <= 10:
                delta = next_drag_total - current_drag_total
                delta = max(-3.0, min(3.0, delta))
                next_drag_total = current_drag_total + delta

            # 连续停滞时，按误差方向明确给出一个更大的鼠标修正
            if stagnant_count >= 2:
                next_drag_total = current_drag_total + (3.0 if error > 0 else -3.0)
                print(f'检测到位置停滞，强制微调到累计拖动: {next_drag_total:.2f}')

            next_drag_total = max(0.0, next_drag_total)
            last_gap_moved = gap_moved

        else:
            print(f'达到最大拖动次数 {max_iterations}，停止拖动')
    finally:
        sleep(1)
        win32.mouse_click(button="left", click_type="up")
        win32.manual_motion_off()


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele,
    drag_ele,
    retry_count: int = 5,
    offset=0,
    ym_token="",
    refresh_elem=None,
    target_ele=None,
):

    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache folder: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    if not retry_count:
        retry_count = 5

    for _ in range(retry_count):
        if refresh_elem != "" and refresh_elem != None:
            web_page.find(refresh_elem).click()
        drag_element = drag_ele

        # 截图
        image_path = os.path.join(cache_folder, "std_slider.png")

        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(
            image_path, "png", b_x, b_y, b_x + b_w, b_y + b_h
        )

        background_ele_base64 = file2base64(image_path)

        # 识别
        payload = {"image": background_ele_base64, "token": ym_token, "type": 22222}

        with open(image_path, "w") as f:
            json.dump(payload, f, ensure_ascii=False)

        if ym_token:
            data = ym_captcha_recognition(payload)
            data = data.get("data")
        else:
            data = yd_captcha_recognition(payload)
            print(data)
            if data.get("statusCode") != "200":
                raise Exception(data.get("msg"))
            data = data.get("response")

        if data.get("success"):
            raise Exception(data.get("msg"))

        distance = int(data.get("data"))

        # 拖拽
        distance = (distance + int(offset))
        # distance = 143
        if os.name == "nt":
            distance = int(distance * get_ppi())
        xbot.logging.info(f"Distant:{distance}")
        drag(web_page.find(drag_element), distance, target_ele, web_page)

        sleep(3)

        try:
            _, _, width, height = web_page.find(drag_element).get_bounding()
            if width and height == 0:
                break
        except:
            pass
        if not xbot_visual.web.browser.element_display(
            browser=web_page, selector=background_ele, content_type="display"
        ):
            break
            
def test_fun():
    def select_ele(xpath, web_page):
        if "frame" in xpath:
                xpaths = xpath.split(">>")
                data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
                selector = Selector(data)
                return selector
        else:
            data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [xpath]}}
            selector = Selector(data)
            return selector

    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active('chrome')
        background_ele = select_ele(web_page=web_page, xpath='//div[@class="dx_captcha_basic_bg"]')
        slider_ele = select_ele(web_page=web_page, xpath='//div[@class="dx_captcha_basic_slider"]')
        target_ele = select_ele(web_page=web_page, xpath='//div[@class="dx_captcha_basic_sub-slider"]')
        retry_count = 3
        offset = 0
        ym_token = ''
        refresh_elem = ''
        handle_captcha(
            web_page,
            background_ele,
            slider_ele,
            retry_count,
            offset,
            ym_token,
            refresh_elem,
            target_ele
        )
        exit()

def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    target_ele = args.get('target_ele')
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    ym_token = args.get("ym_token", "")
    refresh_elem = args.get("refresh_elem", "")
    test_fun()
    handle_captcha(
        web_page,
        background_ele,
        slider_ele,
        retry_count,
        offset,
        ym_token,
        refresh_elem,
        target_ele
    )

