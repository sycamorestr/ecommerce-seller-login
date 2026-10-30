# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import http
import json
import base64
import xbot_visual
import os
from xbot import print, sleep, web 
from . import package 
from .package import variables as glv
from urllib.parse import urlparse
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value


def ym_captcha_recognition(payload, timeout:float=10):
    """请求云码识别验证码，支持自定义超时时间"""
    conn = http.client.HTTPConnection("api.jfbym.com", timeout=timeout)
    headers = {'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST",
                 "/api/YmServer/customApi",
                 body=data_json,
                 headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    # print(response_data)
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict, timeout:float=10):
    """使用增值服务请求验证码，支持自定义超时时间"""
    # captcha_type = payload.get("type")
    # payload.pop("type")

    # common_info = robot.execute(f'Common.CommonConfig', None)
    # token = common_info.get("token")
    # conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc, timeout=timeout)
    # conn.timeout = 60

    captcha_type = payload.get("type")
    # print(captcha_type)
    payload.pop("type")
    payload.pop("token")
    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.netloc


    if is_ssl:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)

    res_payload = json.dumps(
        {
            "aiToolInterfaceCodeId": f"jfbym_{captcha_type}",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": str(captcha_type),
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": payload,
            },
        }
    )
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/v2/aiservice/call",
                 res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data


# def handle_captcha(web_page, web_element, direction, ym_token,
#                    retry_count, confirm, timeout:float=10) -> str:
#     """处理验证码 - 终极多屏兼容版"""
#     captcha_type = 30009
#     import glob

#     for i in range(retry_count):
#         print(f"\n--- 🔄 正在执行第 {i+1} 次尝试 ---")

#         # 1. 获取物理像素与逻辑像素计算缩放比
#         e_x, e_y, e_w, e_h = web_page.find(web_element).get_bounding(to96dpi=False)
#         e_a_x, e_a_y, e_a_w, e_a_h = web_page.find(web_element).get_bounding(to96dpi=True)

#         scale_x = e_w / e_a_w if e_a_w != 0 else 1.0
#         scale_y = e_h / e_a_h if e_a_h != 0 else 1.0

#         # ==========================================
#         # 2. 核心修复：传入桌面文件夹路径，而非文件路径
#         # ==========================================
#         desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
#         debug_folder = os.path.join(desktop_path, "captcha_debug") # 在桌面建个专用的文件夹

#         # 如果文件夹不存在就创建，存在就清空里面的旧图，防止读取到上一轮的错图
#         if not os.path.exists(debug_folder):
#             os.makedirs(debug_folder)
#         else:
#             for f in glob.glob(os.path.join(debug_folder, "*.png")):
#                 try: os.remove(f)
#                 except: pass

#         target_element = web_page.find(web_element)

#         # 传入文件夹，影刀会自动在里面生成一个随机数字的 .png 文件并返回完整路径
#         saved_file_path = target_element.screenshot(debug_folder)

#         # 兜底逻辑：如果 API 没返回路径，我们自己去文件夹里抓那张图
#         if not saved_file_path or not os.path.isfile(str(saved_file_path)):
#             png_files = glob.glob(os.path.join(debug_folder, "*.png"))
#             if not png_files:
#                 raise Exception("元素截图失败：未在文件夹中找到图片！")
#             saved_file_path = png_files[0]

#         print(f"📸 [完美截图] 元素直接截图成功！图片绝对路径: {saved_file_path}")

#         image_base64 = file2base64(saved_file_path)

#         payload = {"image": image_base64, 'token': ym_token, 'type': captcha_type, "direction":direction}

#         if ym_token:
#             data = ym_captcha_recognition(payload, timeout=timeout)
#         else:
#             data = yd_captcha_recognition(payload, timeout=timeout)

#         data = data.get("response").get("data")
#         print(f"📥 [打码返回] 原始物理坐标数据: {data}")

#         # ==========================================
#         # 3. 坐标换算与点击
#         # ==========================================
#         positions = [item.split(",") for item in data.split("|")]

#         for idx, (t_x, t_y) in enumerate(positions):
#             if os.name =='nt':
#                 # 将打码平台返回的物理偏移，按比例缩小为逻辑偏移
#                 logical_offset_x = int(t_x) / scale_x
#                 logical_offset_y = int(t_y) / scale_y

#                 # 基准逻辑坐标 + 逻辑偏移 = 最终屏幕位置
#                 target_p_x = e_a_x + int(logical_offset_x)
#                 target_p_y = e_a_y + int(logical_offset_y)
#             else:
#                 target_p_x = e_a_x + int(t_x)
#                 target_p_y = e_a_y + int(t_y)

#             print(f"🎯 第 {idx+1} 个点击点: 鼠标移动至 X={target_p_x}, Y={target_p_y}")
#             xbot.win32.mouse_move(target_p_x, target_p_y)
#             xbot.win32.mouse_click()
#             sleep(0.5) 

#         if confirm:
#             web_page.find(confirm).click()

#         sleep(3)

#         if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=web_element):
#             print("--- 🎉 验证码通过 ---")
#             break
#         else:
#             print("--- ❌ 验证码未通过，准备下一次重试 ---")

def handle_captcha(web_page, web_element, direction, ym_token,
                   retry_count, confirm, timeout:float=10) -> str:
    """处理验证码，支持自定义超时时间"""
    captcha_type = 30009
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    for i in range(retry_count):
        e_x, e_y, e_w, e_h = web_page.find(web_element).get_bounding(
        to96dpi=False)
        e_a_x, e_a_y, _, _ = web_page.find(web_element).get_bounding(
            to96dpi=True)
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        temp_file = os.path.join(cache_folder, "std_click_plus_temp.png")
        xbot.win32.screenshot.save_screen_to_file(temp_file, "png", e_x, e_y, e_x + e_w, e_y + e_h)
        image_base64 = file2base64(temp_file)

        if os.path.exists(temp_file):
            os.remove(temp_file)
        payload = {"image": image_base64, 'token': ym_token, 'type': captcha_type, "direction":direction}

        if ym_token:
            data = ym_captcha_recognition(payload, timeout=timeout)
            data = data.get("data").get("data")
        else:
            data = yd_captcha_recognition(payload, timeout=timeout)
            data = data.get("response").get("data")

        positions = [item.split(",") for item in data.split("|")]
        for t_x, t_y in positions:
            if os.name =='nt':
                target_p_x = e_a_x + int(int(t_x) * get_ppi())
                target_p_y = e_a_y + int(int(t_y) * get_ppi())
            else:
                target_p_x = e_a_x + int(t_x)
                target_p_y = e_a_y + int(t_y)
            xbot.win32.mouse_move(target_p_x, target_p_y)
            xbot.win32.mouse_click()
        if confirm:
            web_page.find(confirm).click()
        
        sleep(3)
        
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=web_element):
            break
    return 


def main(args):
    web_page = args.get("web_page")
    web_element = args.get("web_element")
    direction = args.get("direction", "bottom")
    ym_token = args.get("ym_token", )
    confirm = args.get("confirm",'')
    retry_count = args.get("retry_count", 5)
    timeout = args.get("timeout", 10)

    # web_page = web.get_active(mode="chrome")
    # web_element = "click_select_element"
    # ym_token = ""

    handle_captcha(web_page, web_element, direction, ym_token, retry_count, confirm, timeout=timeout)
