import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from collections import defaultdict

from PIL import Image
import os


def sectional_by_color(img_path, output_img_path, color):
    """
    指令名：突出验证码颜色
    把需要识别的字符转换成黑色，其他颜色都转换成白色

    :param img_path:
    :param output_img_path: 
    :param color:
    :return:
    """
    img = Image.open(img_path)

    pixdata = img.load()
    rgb_mapper = defaultdict(int)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            pix = pixdata[x, y]
            rgb_mapper[(pix[0], pix[1], pix[2])] += 1

    # 图片中像素点rgb值的统计数中最多的就是背景的颜色
    bg_color = max(rgb_mapper, key=rgb_mapper.get)
    # print('背景颜色是', bg_color)

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            pix = pixdata[x, y]
            if (pix[0], pix[1], pix[2]) == bg_color:
                pixdata[x, y] = (255, 255, 255)
                continue
            if color == "红色":   # 255, 0, 0
                if pix[0] >= 200 and pix[1] < 128 and pix[2] < 128:
                    pixdata[x, y] = (0, 0, 0)
                else:
                    pixdata[x, y] = (255, 255, 255)
            elif color == "黄色":  # 255, 255, 0
                if pix[0] > 128 and pix[1] > 128 and pix[2] < 128:
                    pixdata[x, y] = (0, 0, 0)
                else:
                    pixdata[x, y] = (255, 255, 255)
            elif color == "蓝色":   # 0, 0, 255
                if pix[0] < 100 and pix[1] < 100 and pix[2] > 220:
                    pixdata[x, y] = (0, 0, 0)
                else:
                    pixdata[x, y] = (255, 255, 255)
            # elif color == "粉色": # (255,192,203)
            #     if pix[0] < 100 and pix[1] < 100 and pix[2] > 160:
            #         pixdata[x, y] = (0, 0, 0)
            #     else:
            #         pixdata[x, y] = (179, 51, 170)

            # not reachable
            else:   # 0, 0, 0
                if pix[0] < 128 and pix[1] < 128 and pix[2] < 128:
                    pixdata[x, y] = (0, 0, 0)
                else:
                    pixdata[x, y] = (255, 255, 255)
    
    save_to = output_img_path
    img.save(save_to)
    return save_to


def main(args):
    args['结果图片路径'] = sectional_by_color(args['验证码图片路径'], args['输出图片路径'], args['要突出的颜色'])
