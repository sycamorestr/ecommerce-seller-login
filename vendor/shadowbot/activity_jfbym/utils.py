# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import xbot
import xbot_visual
import sqlite3
import json
import random
import os
import base64
import ast
import ctypes
import mimetypes
import hashlib
import urllib
import http.client
import urllib.parse
import time


from .package import variables as glv
from . import package
from .xtrace import XTrace

from xbot import web
from codecs import encode
if os.name == 'nt':
    from ctypes import windll
from xbot.web import WebElement
from xbot._core import robot
from xbot import print, sleep, win32
from xbot.web.chromium import ChromiumElement
import socket
import uuid
from xbot.selector import Selector
import platform

# 设置全局连接超时时间为 5 秒
socket.setdefaulttimeout(10)

def clear_clipboard():
    """清空剪贴板 - 跨平台版本"""
    for i in range(100):
        try:
            # 优先使用 xbot.win32 (跨平台)
            if hasattr(win32, 'clipboard') and hasattr(win32.clipboard, 'clear'):
                win32.clipboard.clear()
                break
            elif os.name == 'nt':
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
                break
            else:
                # macOS/Linux 使用 tkinter
                try:
                    import tkinter as tk
                    root = tk.Tk()
                    root.withdraw()
                    root.clipboard_clear()
                    root.destroy()
                    break
                except Exception:
                    pass
        except Exception as e:
            sleep(0.1)

def _moveTo(x, y):
    """移动鼠标到指定位置 - 跨平台版本
    Args:
      x (int): 目标 x 坐标
      y (int): 目标 y 坐标
    """
    if os.name == 'nt':
        ctypes.windll.user32.SetCursorPos(x, y)
    else:
        win32.mouse_move(x, y, move_speed="instant")


def get_md5(file_path):
    """计算图片的 MD5"""
    with open(file_path, "rb") as f:
        md5 = hashlib.md5()
        md5.update(f.read())
        return md5.hexdigest()


def get_xbot_activity_cache_folder(activity_code):
    """根据指令code 获取本地缓存目录, 不存在则创建 - 跨平台版本"""
    if os.name == 'nt':
        base_cache_path = os.getenv('LOCALAPPDATA', os.getenv('TEMP', '/tmp'))
    elif platform.system() == 'Darwin':
        base_cache_path = os.path.expanduser('~/Library/Caches')
    else:
        base_cache_path = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
    xbot_app_cache_dir = os.path.join(base_cache_path, "xbot_app", activity_code)
    if not os.path.exists(xbot_app_cache_dir):
        os.makedirs(xbot_app_cache_dir, exist_ok=True)
    return xbot_app_cache_dir


def get_ppi():
    """获取屏幕的缩放 - 跨平台版本"""
    for _ in range(5):
        try:
            if os.name == 'nt':
                # Windows: 使用 ctypes 获取真实 DPI
                LOGPIXELSX = 88
                LOGPIXELSY = 90
                user32 = windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
                user32.ReleaseDC(0, dc)
                res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
                return res[1] / res[0]
            else:
                # macOS/Linux: xbot.win32 已处理平台差异，返回 1
                return 1
        except Exception as e:
            sleep(1)
            pass
    else:
        return 1



def get_data_by_distance(distance, one=True):
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(
        file_name="database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if distance < 50:
        di = 50
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 50")
    elif 50 < distance < 150:
        di = 100
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 100")
    else:
        di = 150
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 150")

    rows = cursor.fetchall()

    if one:
        random_index = random.randint(0, len(rows) - 1)

        data = json.loads(rows[random_index][2])
        tmp = []
        for item in data:
            tmp.append([item[0], item[1] + random.randint(-2, 2), item[2]])
        # print("rows[random_index][2]:", rows[random_index][2])

        result = ast.literal_eval(rows[random_index][2])

        for i in range(len(result)):
            result[i][0] = result[i][0] / di * distance

        # print("result:", result)
        result = json.dumps(result)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]


def get_title(current_file_name):
    script_dir = os.path.dirname(__file__)  
    file_path = os.path.join(script_dir, "prototype.block.json")  
    with open(file_path,'r',encoding='utf-8') as f:
        info_dict = f.read()
    info_dict = json.loads(info_dict)
    capture_type = ''
    for info in info_dict['blocks']:
        if current_file_name.split('.')[0] in info['name']:
            capture_type = info['title']
            break
    return capture_type

def version_number():
    script_dir = os.path.dirname(__file__)  
    file_path = os.path.join(script_dir, "package.json")  
    with open(file_path,'r',encoding='utf-8') as f:
        info_dict = f.read()
    info_dict = json.loads(info_dict)

def file2base64(file_path) -> str:
    """将本地文件转换成 base64"""
    with open(file_path, "rb") as f:
        image_data = f.read()
        base64_str = base64.b64encode(image_data).decode("utf-8")
        return base64_str


def drag(drag_ele:WebElement, distance:int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()
    

def drag_gen(drag_ele: WebElement, distance: int):
    # x, y, width, height = drag_ele.get_bounding()
    # pos_center_x = x + width / 2
    # pos_center_y = y + height / 2
    # move_speed = "middle"
    # win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    # win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    # win32.mouse_click(button="left", click_type="down", delay_after=0)
    # win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    # win32.mouse_click(button="left", click_type="up", )
    # win32.manual_motion_off()

    # return

    mouse_pos_path = get_data_by_distance(distance)
    x = XTrace()
    _, mouse_pos_path = x.get_mouse_pos_path(distance)
    xbot.win32.manual_motion_on()
    drag_ele.hover(simulative=True)
    point_x, point_y = xbot.win32.get_mouse_position()
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        xPoint = point_x + int(offset_x)
        yPoint = point_y + int(offset_y)
        # _moveTo(xPoint, yPoint)
        xbot.win32.mouse_move(xPoint, yPoint, delay_after=0)
        sleep(t / 800)

    win32.mouse_click(button="left", click_type="up")
    xbot.win32.manual_motion_off()



def start_upload(web_page, current_file_name):
    pass


def end_upload(web_page, count, current_file_name):
    pass


def send_log(message,*,level=20,exception='',logContextStr=''):
    """
    写日志到elastic平台
    * @param module, 写入的模块
    * @param message, 日志信息，重要的查询条件
    * @param exception, 异常信息
    """
    args={
        'module':'engine',
        'message':message,
        'level':level,
        'exception':exception,
        'context':logContextStr
    }
    robot.execute(f'Stats.Log', args)

def get_boundary_value(web_page, ele)->list:
    x, y, width, height = web_page.find(ele).get_bounding(to96dpi=False, relative_to='window')
    return [x, y, width, height]

def report_data(site_url, captcha_url="", file_path="", captcha_count="", read_url="", captcha_code="", **kwargs):
    """上报云码验证码数据
    :param site_url: 验证码出现网页的地址
    :param captcha_url: 验证码iframe的地址
    :param file_path: 网页截图地址
    :param captcha_count : 识别次数
    :param read_url : 上传oss的read_url
    :param captcha_code: 验证码类型type
    """
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    captcha_filename = "captcha_upload.png"
    captcha_file_path = os.path.join(cache_folder, captcha_filename)
    captcha_type = get_title(file_path) #得到验证码指令名称
    md5_key = get_md5(captcha_file_path)
    message = {
        "boundary":kwargs,
        "site_url":site_url,
        "captcha_type": captcha_type,
        "captcha_code": captcha_code,
        "captcha_url": captcha_url,
        "captcha_image_read_url": read_url,
        "captcha_count": captcha_count,
        "captcha_md5": md5_key,
        "version_situation":"new"
       }
    send_log(f"云码验证码数据上报" + json.dumps(message, ensure_ascii=False))

def get_upload_url(file_path):
    """获取上传地址
    data 的 secondDir 可自定义
    """
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    md5_key = get_md5(file_path)

    secondDir = 'ym_captcha'

    data = {
        "fileOriginScene": "common_image",
        "fileKeyAttrs": {
            "firstDir": "117582",
            "secondDir": secondDir,
            "fileMd5Name": md5_key,
        },
        "fileType": "image",
    }

    conn = http.client.HTTPSConnection(urllib.parse.urlparse(common_info.get("webApi")).netloc, timeout=5)
    conn.request("POST", "/api/v2/user/file/getUploadUrlV2", json.dumps(data), headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def upload_oss(upload_url, file_path) -> None:
    """上传文件至 oss
    :upload_url
    :file_path
    """
    parsed_url = urllib.parse.urlparse(upload_url)
    hostname = parsed_url.hostname
    path = parsed_url.path + "?" + parsed_url.query

    filesize = os.path.getsize(file_path)

    headers = {
        "Content-Length": str(filesize),
        "x-oss-object-acl": "public-read",
        "x-amz-acl": "public-read",
    }

    conn = http.client.HTTPSConnection(hostname)

    with open(file_path, "rb") as file:
        conn.request("PUT", path, body=file, headers=headers)

        response = conn.getresponse()
        response_data = response.read()
    conn.close()


def upload_captcha_screenshot(web_page: xbot.web.WebBrowser) -> str:
    """网页截图并将图片上传至对象存储
    :return: 返回图片的fileKeyMd5
    """
    # 网页截图, 并保存到本地换成目录
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    captcha_filename = "captcha_upload.png"
    captcha_file_path = os.path.join(cache_folder, captcha_filename)
    try:
        if os.path.exists(captcha_file_path):
            os.remove(captcha_file_path)
        # print(time.time())
        web_page.screenshot(cache_folder, file_name=captcha_filename, full_size=False)
        # print(time.time())
        file_md5 = get_md5(captcha_file_path)
        # 获取对象存储上传URL
        upload_info = get_upload_url(captcha_file_path)
        # print(upload_info)
        upload_url = upload_info.get("data").get("uploadUrl")
        read_url = upload_info.get("data").get("readUrl")
        # file_key_md5 = upload_info.get("data").get("fileKeyMd5")

        # 上传图片
        upload_oss(upload_url, captcha_file_path)
        return read_url
    except Exception as e:
        pass


def test_upload_captcha_screenshot():
    web_page = xbot.web.create(url="baidu.com", mode="chrome")
    res = upload_captcha_screenshot(web_page)


def test_report_data():
    report_data()

def gen_selector(xpath, name):
    if isinstance(xpath, str):
        xpath = xpath.split(">>")
    data = {
        "id": str(uuid.uuid4()),
        "name": name,
        "framework": "chrome",
        "type": "simple",
        "version": "2",
        "processName": "chrome",
        "productName": "Google Chrome",
        "xpath": {"enable": "true", "segments": xpath},
    }
    selector = Selector(data)
    return selector

def main(args):
    # test_report_data()
    # get_upload_url(r"C:\Users\11758\Desktop\飞书.png")
    # test_upload_captcha_screenshot()
    # version_number()
    # pass
    web_page = xbot.web.get_active('chrome')
    test_selector = package.selector('test_selector')
    print(type(test_selector))
    assert type(test_selector) != ChromiumElement, web_page.find(test_selector)
    print(type(test_selector))
    # test_ele = web_page.find(test_selector)
    # print(type(test_ele))
    