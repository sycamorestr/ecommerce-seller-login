# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
from datetime import datetime

import xbot
from xbot import print, sleep, web, win32
from xbot.selector import Selector
from PIL import Image, ImageDraw, ImageFont

from .import package
from .package import variables as glv
from .utils import Tools


def add_time_watermark(src_path, dst_path=None):
    """给截图加时间水印（右下角自适应宽度）"""

    img = Image.open(src_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("msyh.ttc", 40)
    text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    w, h = img.size
    # 1. 先量文字尺寸
    tw, th = draw.textsize(text, font=font)
    # 2. 右下角定位，左右各留 10 px 边距
    bar_w, bar_h = tw + 20, th + 10
    x, y = w - bar_w - 10, h - bar_h - 10
    # 3. 画半透明条 + 文字
    draw.rectangle([x, y, x + bar_w, y + bar_h], fill=(0, 0, 0, 128))
    draw.text((x + 10, y + 5), text, font=font, fill=(255, 255, 255, 255))

    dst = dst_path or src_path
    img.save(dst)
    return dst


def gen_selector(xpath):
    # 判断元素是否存在
    data = {
        'id': 'ifream-xpath',
        'name': 'ifream-xpath',
        'type': 'simple',
        'xpath': {'enable': 'true', 'segments': [xpath]}
    }
    return Selector(data)


def pending_data_screenshot(web_page, file_folder, station):
    """Temu店铺的结算数据截图"""

    # 等待页面加载完毕
    web_page.wait_load_completed()

    Tools.check_target_web(web_page, 'labor/settle')

    # 等待店铺名称出现，获取店铺名称
    shop_name_xpath = '(//div[contains(@class,"account-info_accountInfo")]//span[contains(@class,"elli_outerWrapper")])[1]'
    shop_name_sel = gen_selector(shop_name_xpath)
    web_page.wait_appear(shop_name_sel)
    shop_name = web_page.find_by_xpath(shop_name_xpath).get_text()

    # 消除信息框
    Tools.handle_info(web_page)

    # 判断新旧页面
    judgment_new_xpath = '//div[@id="step1"]'
    judgement_new_sel = Tools.gen_selector(judgment_new_xpath)
    if web_page.wait_appear(judgement_new_sel, timeout=5):
        web_page.find_by_xpath(judgment_new_xpath).click()
    else:
        # 随便点击一下，用于智能屏蔽弹窗以及自动处理弹唱的指令适配
        web_page.find_by_xpath('//div[text()="结算数据" and @data-testid="beast-core-box"]').click()

    # 设置图片名称
    file_name = f"{shop_name} {station}-待结算数据截图.png"
    # 设置截图路径
    file_path = file_folder + '\\' + file_name
    try:
        # 进行截图
        win32.screenshot.save_screen_to_file(file_path, 'png')
        sleep(1)
        # 添加水印
        add_time_watermark(file_path)
    except Exception as e:
        print(e)
        raise Exception('{shop_name} 店铺截图保存失败')
    
    return file_path


def test():
    """测试模块"""
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active(mode='chrome')
    file_folder = os.path.join(os.path.expanduser('~'),'Desktop')
    station = 'xsdadadsd'
    pending_data_screenshot(web_page, file_folder, station)
    
    exit()

def main(args):
    # 测试模块
    test()

    # 功能模块
    web_page = args.get('web_page')
    file_folder = args.get('file_folder')
    station = args.get('station')

    if not file_folder:
        # 文件夹默认为桌面
        file_folder = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    file_path = pending_data_screenshot(web_page, file_folder, station)
    args['file_path'] = file_path