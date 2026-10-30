# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import base64
import os
import xbot  
import json  

try:
    from ctypes import windll 
except:
    pass

from PIL import Image, ImageChops, ImageOps, ImageFont, ImageDraw
from xbot import print, sleep, web, win32
try:
    from .resources import trace_api
except:
    pass
    
from . import package   
import uuid
from xbot.selector import Selector

class PIL_API:
    def __init__(self, file_name=None, im=None):
        if file_name: 
            if not os.path.exists(file_name):
                raise ValueError(f'图像 {file_name} 不存在')

            try:
                self.im = Image.open(file_name)
                self.file_name = file_name
            except:
                raise ValueError(f'打开图片{file_name}失败，请检查图片是否有效')
        elif im:
            self.im = im
        else:
            raise ValueError(f"初始化失败")

    def size(self):
        '''
        获取图片尺寸
        * @return <tuple>: width, height
        '''
        return self.im.size

    def resize(self, width, height, save_name=None):
        '''
        修改图片尺寸
        * @param width, 修改后的宽度
        * @param height, 修改后的高度
        * @save_name, 保存的文件名
        '''
        resize_img = self.im.resize((int(width), int(height)))
        resize_img = PIL_API(im=resize_img)
        if save_name:
            resize_img.save(save_name)
        return resize_img

    def save(self, save_name):
        '''
        图片保存，可以实现格式转换
        '''
        if not save_name:
            raise ValueError(f'图片路径未指定，无法保存')

        rgb_im = self.im
        _, file_extension = os.path.splitext(save_name)
        if file_extension.lower() == '.jpg' or file_extension.lower(
        ) == '.jpeg':
            rgb_im = rgb_im.convert('RGB')

        #文件夹处理
        file_folder = os.path.dirname(save_name)
        self._createfolderIfNeeded(file_folder)

        rgb_im.save(save_name)

    def crop(self, left, top, right, bottom):
        return self.im.crop((left, top, right, bottom))


def base64_to_image(data, image_name):
    prefex = 'data:image/png;base64,'
    if data.startswith(prefex):
        data = data[len(prefex):]
    with open(image_name, 'wb') as f:
        f.write(base64.decodebytes(bytearray(data, 'utf-8')))


def time_ease(xOffset):
    return trace_api.time_ease(xOffset)


def y_offset():
    return trace_api.y_offset()


def get_ppi():
    """
    获取屏幕的缩放
    """
    try:
        for _ in range(5):
            try:
                LOGPIXELSX = 88
                LOGPIXELSY = 90
                user32 = windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
                user32.ReleaseDC(0, dc)
                res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
                return res[1] / res[0]
            except Exception as e:
                sleep(1)
                pass
        else:
            return 1
    except:
        return 1


def get_web_url(mode="chrome",
                load_timeout=30,
                stop_if_timeout=False):
    """
    获取网址
    mode:str 浏览器类型
    """
    web_url = web.get_active(mode=mode,
                             load_timeout=load_timeout,
                             stop_if_timeout=stop_if_timeout).get_url()
    return web_url


def validate_input_content(username, password):
    """校验账号密码是否符合验证规则"""
    assert bool(username) and isinstance(username,
                                         str), "请检查登录账号密码是否为字符串类型, 且不为空"
    assert bool(password) and isinstance(password,
                                         str), "请检查登录账号密码是否为字符串类型, 且不为空"


def sdk_create_web_page(url="",
                        mode="chrome",
                        load_timeout=30,
                        stop_if_timeout=False):
    """
    自定义浏览器类型, 打开网页, 参数参考 sdk 
    """
    return web.create(
        url=url,
        mode=mode,
        load_timeout=load_timeout,
        stop_if_timeout=stop_if_timeout,
        silent_running=False
    )

def get_active_by_web_page(web_page, silent_running=False):
    ''' 获取浏览器类型， 开启静默模式
    '''
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return xbot.web.get_active(mode=product_name, silent_running=silent_running)

def drag(point_x, point_y, distance, move_speed):
    """拖动滑块
    :param poit_x: 鼠标开始拖动的 x 坐标
    :param point_y: 鼠标开始拖动的 y 坐标
    :param distance: 鼠标拖动的距离
    :param move_speed: 移动速度, instant, fast, middle, slow
    """
    win32.mouse_move(point_x=point_x, point_y=point_y, move_speed=move_speed)

    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.manual_motion_on()
    win32.mouse_click(button="left", click_type="down")
    win32.mouse_move(point_x + distance, point_y, move_speed="middle",)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()


    # invoke_result = time_ease(distance)
    # xPoint, yPoint = point_x, point_y
    # for loop_item in invoke_result:
    #     point_x_offset, delay = loop_item
    #     xPoint = point_x + point_x_offset
    #     ponit_y_offset = y_offset()
    #     if ponit_y_offset != 0: yPoint += ponit_y_offset
    #     win32.mouse_move(
    #         xPoint,
    #         yPoint,
    #         move_speed=move_speed,
    #         delay_after=delay,
    #     )
    # sleep(1)


def create_web(url, mode='cef', load_timeout=20, stop_if_timeout=False, silent_running=False, executable_path=None, arguments=None):
    return web.create(url, mode='cef', load_timeout=20, stop_if_timeout=False, silent_running=False, executable_path=None, arguments=None)


def get_active_web(mode='cef', load_timeout=20, stop_if_timeout=False, silent_running=False):
    return web.get_active(mode='cef', load_timeout=20, stop_if_timeout=False, silent_running=False)

def sdk_create_web_page_plus(url="",
                        mode="chrome",
                        load_timeout=30,
                        stop_if_timeout=True):
    """
    自定义浏览器类型, 打开网页, 参数参考 sdk 
    """
    return web.create(
        url=url,
        mode=mode,
        load_timeout=load_timeout,
        stop_if_timeout=stop_if_timeout,
        silent_running=True
    )


def get_mode(web_page):
    ''' 获取浏览器类型
    '''
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return product_name

def gen_selector(xpath, name):
    if isinstance(xpath, str):
        xpath = xpath.split(">>")
    data = {
        "id": str(uuid.uuid4()),
        "name": name,
        "framework": "chrome",
        "type": "simple",
        "version": 2,
        "xpath": {"enable": "true", "segments": xpath},
    }
    selector = Selector(data)
    return selector

def main(args):
    print(get_ppi())
    pass
    