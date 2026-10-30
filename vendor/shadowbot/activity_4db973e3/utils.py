# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import base64
import os
import sys
import xbot
import json
from codecs import encode
if os.name =='nt':
    from ctypes import windll 
import xbot_visual
import http.client
import mimetypes
import urllib.request
import urllib.parse
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
from PIL import Image, ImageChops, ImageOps, ImageFont, ImageDraw
from xbot import print, sleep, win32
from .resources import trace_api
from . import package
import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv
from xbot.win32.element import Win32Element

arch = 'x86' if '86' in os.environ['PROCESSOR_ARCHITECTURE'] else 'x64'
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.environ['PYTHONPATH'])),
                 f"support_{arch}\cv-engine\site-packages"))
try:
    import cv2

except Exception as e:
    pass

def get_ppi():
    """
    获取屏幕的缩放
    """
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
    except:
        return 1


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


class Chaojiying_Client(object):
    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = password
        self.soft_id = soft_id
        self.headers = {
            "Connection":
            "Keep-Alive",
            "User-Agent":
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)",
        }

    def PostPic(self, im_byte, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        conn = http.client.HTTPSConnection("upload.chaojiying.net")
        dataList = []
        boundary = "wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T"
        dataList.append(encode("--" + boundary))
        dataList.append(encode("Content-Disposition: form-data; name=user;"))

        dataList.append(encode("Content-Type: {}".format("text/plain")))
        dataList.append(encode(""))

        dataList.append(encode(self.username))
        dataList.append(encode("--" + boundary))
        dataList.append(encode("Content-Disposition: form-data; name=pass;"))

        dataList.append(encode("Content-Type: {}".format("text/plain")))
        dataList.append(encode(""))

        dataList.append(encode(self.password))
        dataList.append(encode("--" + boundary))
        dataList.append(encode("Content-Disposition: form-data; name=softid;"))

        dataList.append(encode("Content-Type: {}".format("text/plain")))
        dataList.append(encode(""))

        dataList.append(encode(self.soft_id))
        dataList.append(encode("--" + boundary))
        dataList.append(
            encode("Content-Disposition: form-data; name=codetype;"))

        dataList.append(encode("Content-Type: {}".format("text/plain")))
        dataList.append(encode(""))

        dataList.append(encode(codetype))
        dataList.append(encode("--" + boundary))
        dataList.append(
            encode(
                "Content-Disposition: form-data; name=userfile; filename={0}".
                format("/path/to/file")))

        fileType = (mimetypes.guess_type("/path/to/file")[0]
                    or "application/octet-stream")
        dataList.append(encode("Content-Type: {}".format(fileType)))
        dataList.append(encode(""))

        dataList.append(im_byte)
        dataList.append(encode("--" + boundary + "--"))
        dataList.append(encode(""))
        body = b"\r\n".join(dataList)
        payload = body
        headers = {
            "Content-type": "multipart/form-data; boundary={}".format(boundary)
        }
        conn.request("POST", "/Upload/Processing.php", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        return json.loads(data)

    def ReportError(self, im_id):
        """
            im_id:报错题目的图片ID
        """
        params = {"id": im_id}
        params.update(self.base_params)
        data = urllib.parse.urlencode(params).encode()

        url = "http://upload.chaojiying.net/Upload/ReportError.php"
        request = urllib.request.Request(url=url,
                                         data=data,
                                         headers=self.headers)
        response = urllib.request.urlopen(request).read()

        return json.loads(response.decode("utf-8"))


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


def drag(point_x, point_y, distance, move_speed):
    """拖动滑块
    :param poit_x: 鼠标开始拖动的 x 坐标
    :param point_y: 鼠标开始拖动的 y 坐标
    :param distance: 鼠标拖动的距离
    """
    # win32.mouse_move(point_x=point_x, point_y=point_y, move_speed="middle")
    print(move_speed)
    if move_speed == "瞬间":
        move_speed = "instant"
    elif move_speed == "快速":
        move_speed = "fast"
    elif move_speed == "中速":
        move_speed ="middle"
    elif move_speed == "慢速":
        move_speed = "slow"
    win32.mouse_move(point_x=point_x, point_y=point_y, move_speed=move_speed)

    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    invoke_result = time_ease(distance)
    xPoint, yPoint = point_x, point_y
    for loop_item in invoke_result:
        point_x_offset, delay = loop_item
        xPoint = point_x + point_x_offset
        ponit_y_offset = y_offset()
        if ponit_y_offset != 0: yPoint += ponit_y_offset
        win32.mouse_move(
            xPoint,
            yPoint,
            move_speed=move_speed,
            delay_after=delay,
        )
    sleep(1)
    win32.mouse_click(button="left", click_type="up")


def drag_by_xbot(point_x, point_y, distance, move_speed):
    if move_speed == "瞬间":
        move_speed == "instant"
    elif move_speed == "快速":
        move_speed == "fast"
    elif move_speed == "中速":
        move_speed == "middle"
    elif move_speed == "慢速":
        move_speed == "slow"

    win32.mouse_move(point_x=point_x, point_y=point_y, move_speed=move_speed)
    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    win32.mouse_move(int(point_x + distance), point_y, relative_to="screen", move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up")


def code_recognize(username, password, softid, codetype, image_path):
    with open(image_path, "rb") as f:
        chaojiying = Chaojiying_Client(username, password, softid)
        result = chaojiying.PostPic(f.read(), codetype)

        if result.get("err_str") == "OK":
            return result.get("pic_str")
        else:
            raise ValueError(result.get("err_str"))


def distance_ty(background_file, gap_file):
    """
    通过 cv 计划滑块验证码的滑动距离
    """
    background_img = cv2.imread(background_file)
    gap_img = cv2.imread(gap_file)
    background_edge = cv2.Canny(background_img, 100, 200)
    gap_edge = cv2.Canny(gap_img, 100, 200)
    background_pic = cv2.cvtColor(background_edge, cv2.COLOR_GRAY2RGB)
    gap_pic = cv2.cvtColor(gap_edge, cv2.COLOR_GRAY2RGB)
    res = cv2.matchTemplate(background_pic, gap_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    X = max_loc[0]
    return X




def move(self, start_x, start_y, length):
    data = [[0.0, 0.0, 0.0], [0.17, 0.008492569002123142, 0.0010615711252653928],
            [0.01, 0.0021231422505307855, 0.0010615711252653928],
            [0.01, 0.0031847133757961785, 0.0010615711252653928],
            [0.0, 0.0021231422505307855, 0.0010615711252653928],
            [0.01, 0.0031847133757961785, 0.0010615711252653928],
            [0.0, 0.0021231422505307855, 0.0010615711252653928],
            [0.0, 0.0021231422505307855, 0.0010615711252653928],
            [0.01, 0.004246284501061571, 0.0010615711252653928],
            [0.0, 0.0031847133757961785, 0.0010615711252653928],
            [0.01, 0.0031847133757961785, 0.0010615711252653928],
            [0.01, 0.0074309978768577496, 0.0010615711252653928],
            [0.0, 0.005307855626326964, 0.0021231422505307855], [0.0, 0.010615711252653927, 0.0010615711252653928],
            [0.0, 0.010615711252653927, 0.0010615711252653928], [0.0, 0.012738853503184714, 0.0010615711252653928],
            [0.0, 0.018046709129511677, 0.0021231422505307855], [0.0, 0.02335456475583864, 0.0010615711252653928],
            [0.01, 0.05201698513800425, 0.0010615711252653928], [0.01, 0.06794055201698514, 0.0010615711252653928],
            [0.03, 0.23142250530785563, 0.0021231422505307855], [0.0, 0.032908704883227176, 0.0021231422505307855],
            [0.01, 0.059447983014861996, 0.0010615711252653928], [0.01, 0.05626326963906582, 0.0021231422505307855],
            [0.0, 0.024416135881104035, 0.0010615711252653928], [0.01, 0.0732484076433121, 0.0021231422505307855],
            [0.02, 0.08598726114649681, 0.0010615711252653928], [0.08, 0.16348195329087048, -0.0010615711252653928],
            [0.01, 0.006369426751592357, -0.0010615711252653928],
            [0.01, 0.0031847133757961785, -0.0010615711252653928],
            [0.01, 0.0031847133757961785, -0.0010615711252653928],
            [0.05, 0.004246284501061571, -0.004246284501061571],
            [0.34, 0.012738853503184714, -0.006369426751592357],
            [0.0, 0.0010615711252653928, -0.0010615711252653928]]
    point_x, point_y = start_x, start_y
    yd_tool.touch_down(self.device_session, point_x, point_y)
    # self.d.touch.down(point_x, point_y)
    for i, (t, x, y) in enumerate(data):
        point_x, point_y = point_x + x * length, point_y + y * length
        if i > 21:
            yd_tool.move_to(self.device_session, point_x, point_y)
        # if i % 3 != 0: continue
        # self.d.touch.move(point_x, point_y)

    yd_tool.touch_up(self.device_session, point_x, point_y)

def main(args):
    print(get_ppi())
    pass
