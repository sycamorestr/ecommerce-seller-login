# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

from re import I
import xbot
import http
import json
import base64
from xbot import request
import xbot_visual
import os
from io import BytesIO
from xbot import print, sleep, web 
from . import package 
from .package import variables as glv
from PIL import ImageGrab
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
from urllib.parse import urlparse
import time
import threading
from xbot.web import WebBrowser
import requests

def monitor_network(web_page:WebBrowser):
    '''
    监听图片
    '''
    js_code = '''
    function () {
        /***********************
        * 1️⃣ 定义全局图片池（原型链）
        ***********************/
        if (!Object.prototype.__LATEST_IMAGES__) {
            Object.defineProperty(Object.prototype, "__LATEST_IMAGES__", {
            value: [],
            writable: true,
            enumerable: false,
            configurable: false
            });
        }

        /***********************
        * 2️⃣ 重置并写入最新图片
        ***********************/
        function resetAndSave(img) {
            const store = Object.prototype.__LATEST_IMAGES__;

            // 每次监听到图片，清空旧数据
            store.length = 0;

            store.push({
            src: img.currentSrc || img.src,
            width: img.naturalWidth,
            height: img.naturalHeight,
            time: Date.now()
            });

            console.log("📸 捕获最新图片（已清空历史）:", img.src);
        }

        /***********************
        * 3️⃣ 监听单个 img
        ***********************/
        function listenImg(img) {
            if (img.__imgHooked) return;
            img.__imgHooked = true;

            // 已完成加载
            if (img.complete) {
            if (img.naturalWidth > 0) {
                resetAndSave(img);
            }
            return;
            }

            img.addEventListener("load", function () {
            resetAndSave(img);
            });

            img.addEventListener("error", function () {
            // 失败的不写入
            });
        }

        /***********************
        * 4️⃣ 监听已有图片
        ***********************/
        document.querySelectorAll("img").forEach(listenImg);

        /***********************
        * 5️⃣ 监听动态新增图片
        ***********************/
        new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType !== 1) return;

                if (node.tagName === "IMG") {
                listenImg(node);
                } else {
                node.querySelectorAll &&
                    node.querySelectorAll("img").forEach(listenImg);
                }
            });
            });
        }).observe(document.documentElement, {
            childList: true,
            subtree: true
        });

        console.log("👀 全局图片池 + 图片监听 已启动");
        }
    '''
    web_page.execute_javascript(js_code, execution_world='MAIN')

def get_latest_images(web_page:WebBrowser):
    '''
    获取最新图片
    '''
    js_code = '''
    function () {
        return Object.prototype.__LATEST_IMAGES__;
    }
    '''
    img_list = web_page.execute_javascript(js_code, execution_world='MAIN')
    img_url = img_list[0]['src']
    # 下载图片url变成base64
    img_base64 = base64.b64encode(requests.get(img_url).content).decode('utf-8')
    return img_base64


def get_xbot_client():
    """获取客户端 token"""
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST",
                 "/api/YmServer/customApi",
                 body=data_json,
                 headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json.get('data')


def yd_captcha_recognition(payload: dict):
    # 判断客户端版本, 是否使用ssl, host, 以及token
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

    payload = json.dumps(
        {
            "aiToolInterfaceCodeId": "jfbym_32110",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "32110",
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {'label_image': payload.get('label_image'), "svg_xml": payload.get('svg_xml')},
            },
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    conn.request("POST", "/api/v2/aiservice/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json.get("data").get("response")

def get_point_position(num, weight, height):
    ''' 计算当前图片需要点击的位置
    :params num: list, 图片点击位置列表, 由接口返回
    :params weight: int, 图片的宽度
    :params height: int, 图片的高度
    '''
    center_x = int(weight * 0.25)
    center_y = int(height * 0.25)
    return 0.5 * num[1] * weight - center_x, 0.5 * num[0] * height - center_y

def handle_captcha(web_page, image_ele, refresh_ele, ym_token, retry_count=5):
    """处理验证码"""
    captcha_type = 32110
    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache folder: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    for i in range(retry_count):
        label_image_ele_path = os.path.join(cache_folder, "label_image_ele.png")
        # 通过监听拿原图
        web_page.start_monitor_network()
        web_page.find(refresh_ele).click()
        # 先注入js监听图片
        monitor_network(web_page)
        while True:
            # data = web_page.get_responses(resource_type='Image')
            data = get_latest_images(web_page)
            if data:
                break
                
        img_base64 = data
        with open(label_image_ele_path, 'wb') as f:
            f.write(base64.b64decode(img_base64))
        
        e_a_x, e_a_y, e_a_w, e_a_h = web_page.find(image_ele).get_bounding(to96dpi=True)
        start_time = time.time()
        
        label_image_base64 = img_base64
        # 获取svg下的所有js字段
        svg_xml = web_page.find(image_ele).get_html()
        payload = {'token': ym_token, 'type': captcha_type, 'label_image': label_image_base64, "svg_xml": svg_xml}

        if ym_token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)

        # 解析三方平台返回
        if isinstance(data, dict) and 'data' in data:
            try:
                data_json = json.loads(data['data'])
            except Exception:
                print('三方平台返回data字段解析失败:', data['data'])
                continue
        else:
            print('三方平台返回格式异常:', data)
            continue
        print(data_json)
        serial_page = data_json.get('serial_page')
        serial_num_list = data_json.get('serial_num', [])
        switch_interval = 2.5
        x, y = get_point_position(serial_num_list, e_a_w, e_a_h)
        now = time.time()
        elapsed = now - start_time
        # 当前是第几张
        current_page = int(elapsed // switch_interval) % 3 + 1
        # 距离目标图片还需几步
        step = (serial_page - current_page) % 3
        wait_time = switch_interval - (elapsed % switch_interval) + (step - 1) * switch_interval if step else 0
        if wait_time > 0:
            time.sleep(wait_time)

        for num in serial_num_list:
            # if os.name == 'nt':
            #     target_p_x = e_a_x + int(x)
            #     target_p_y = e_a_y + int(y)
            # else:
            target_p_x = e_a_x + int(x)
            target_p_y = e_a_y + int(y)
            xbot.win32.mouse_move(target_p_x, target_p_y, move_speed='instant', delay_after=0)
            xbot.win32.mouse_click()
        sleep(2)
        # 判断是否验证通过，未通过则break
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=image_ele):
            break
    
    # return 
def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        image_ele = package.selector('微博四方格点选')
        refresh_ele = package.selector('微博四方格点选_刷新元素')
        ym_token = ''
        retry_count = 5
        handle_captcha(web_page, image_ele, refresh_ele, ym_token, retry_count)
        exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    image_ele = args.get('image_ele')
    ym_token = args.get("ym_token", )
    retry_count = args.get("retry_count", 5)
    refresh_ele = args.get('refresh_ele')
    handle_captcha(web_page, image_ele, refresh_ele, ym_token, retry_count)
