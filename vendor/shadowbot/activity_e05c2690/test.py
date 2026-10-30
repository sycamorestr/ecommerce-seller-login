# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,win32
from .import package
from .package import variables as glv
import xbot_visual
import base64
from PIL import Image
from io import BytesIO
import os

from xbot_extensions.activity_jfbym import chinatax_captcha
from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_click_select_captcha,std_slider_captcha
from .utils import get_xbot_activity_cache_folder
from .orangebank_slider_captcha import deal_deal_handle_captcha
# xbot.web.get_active().find


def decode_image(base64_string,file_path):
    """Decode a base64 string into an image"""
    # base64_string = base64_string + '=' * (-len(base64_string) % 4)
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    img.save(file_path)
    # return img


def main(args):
    web_page = xbot.web.get_active(mode="chrome")
    # web_page = xbot.web.get_active(mode="edge")
    # try_count =2
    # # ym_token = ''
    # ym_token = ''
    # captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
    #                                                     ele = package.selector("工商银行-企业版验证码背景图"),
    #                                                     captcha_type = '10103',
    #                                                     token = ym_token)
    # # print('验证码识别结果为:',captcha_result)
    # password_input = web_page.find("工商银行-企业版验证码输入框")
    # password_input.hover(anchor =("middleCenter",0,0))
    # win32.mouse_click()

    if web_page.is_element_displayed("南京银行-个人版滑动验证码"):
        for i in range(1,5):
            # 获取滑块长度
            x_1,y_1,width_1,height_1 = web_page.find("南京银行-个人版验证码滑块").get_bounding()
            # 获取滑条长度
            x_2,y_2,width_2,height_2 = web_page.find("南京银行-个人版验证码滑条").get_bounding()
            pos_center_x = x_1 + width_1 / 2
            pos_center_y = y_1 + height_1 / 2
            win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed='middle')
            win32.mouse_click(button="left", click_type="down")
            win32.manual_motion_on()
            win32.mouse_move(pos_center_x +width_2, pos_center_y, move_speed="middle")
            win32.manual_motion_off()
            win32.mouse_click(button="left", click_type="up")   
            
            # xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11", package=__name__, inputs={
            # "web_page": web_page,
            # "drag_start_element": package.selector("南京银行-个人版验证码滑块"),
            # "background_element": package.selector("南京银行-个人版验证码滑条"),
            # }, outputs=[])
            sleep(3)
            if not web_page.is_element_displayed("南京银行-个人版滑动验证码"):
                break
    # win32.send_keys(captcha_result,hardware_driver_input=True)
        
    #     web_page.find("中信银行-企业版验证码输入框").click() 
    #     # 识别验证码
    #     captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
    #                                                     ele = package.selector("中信银行-企业版验证码背景图"),
    #                                                     captcha_type = '10103',
    #                                                     token = ym_token)
    #     print('验证码识别结果为:',captcha_result)
    #     captcha_input = web_page.find("中信银行-企业版验证码输入框")    
    #     web_page.find("中信银行-企业版验证码输入框").click()   
    #     for i in range(1,4):
    #         captcha_input.input(captcha_result)
    #         text = captcha_input.get_text()
    #         if text == captcha_result:
    #             break
    #         if i == 3:
    #             raise Exception("验证码输入失败，请手动登录")

    # if web_page.is_element_displayed("浦发银行-企业版验证码背景图"):
    #     std_slider_captcha.handle_captcha(web_page = web_page,
    #                                         background_ele = package.selector("浦发银行-企业版验证码背景图"),
    #                                         drag_ele = package.selector("浦发银行-企业版验证码滑块"),
    #                                         retry_count = 1,
    #                                         offset = 0 , 
    #                                         speed = 1,
    #                                         ym_token = ym_token)
    # for i in range(1,3):
    #     try :
    #         std_slider_captcha.handle_captcha(web_page = web_page,
    #                                         background_ele = package.selector("宁波银行-个人版验证码背景图"),
    #                                         drag_ele = package.selector("宁波银行-个人版验证码滑块"),
    #                                         retry_count = 1,
    #                                         offset = 0 , 
    #                                         speed = 1,
    #                                         ym_token = ym_token)
    #     except Exception as e:
    #         print(e,"点击刷新重试图片中")
    #         ele_move =  web_page.find("宁波银行-个人版验证码滑块")
    #         x,y,_,_ = ele_move.get_bounding()
    #         print(x,y,_,_ )
    #         ele_move.hover()
    #         win32.mouse_click(click_type='down')
    #         win32.mouse_move(x+20,y)
    #         if web_page.is_element_displayed("宁波银行-个人版验证码请重试"):
    #             web_page.find("宁波银行-个人版验证码请重试").click()

    #     if web_page.is_element_displayed("宁波银行-个人版验证码验证成功"):
    #         break
    #     elif web_page.is_element_displayed("宁波银行-个人版验证码请重试"):
    #         web_page.find("宁波银行-个人版验证码请重试").click()
    #     sleep(1)

    # drag_distance= 0
    # web_page.find('北京银行-企业版验证码滑块').hover()
    # ele = web_page.find('北京银行-企业版验证码容器')
    # ele.set_attribute('style','display:block;opacity:1;')
    # sleep(1)
    # # 处理验证码
    # deal_deal_handle_captcha(web_page = web_page,
    #                         background_ele = '北京银行-企业版验证码背景图',
    #                         drag_ele = '北京银行-企业版验证码滑块',
    #                         gap_ele = '北京银行-企业版验证码缺口图片',
    #                         refresh_ele = '',
    #                         retry_count = try_count,
    #                         ym_token = ym_token,
    #                         drag_distance = drag_distance)
    # sleep(1)
    # password = ''
    # password_input = web_page.find("渤海银行-企业版密码输入框")
    # password_input.click()
    # win32.send_keys(password)
    # if web_page.is_element_displayed("渤海银行-企业版企业网银"):
    #     result=web_page.find('渤海银行-企业版企业网银').click()
    # ym_token=''
    # if web_page.is_element_displayed("苏州银行-个人版验证码图片"):
    #     for i in range(1,5):
    #         captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
    #                                                         ele = package.selector("苏州银行-个人版验证码图片"),
    #                                                         captcha_type = '10103',
    #                                                         token = ym_token)
    #         print('验证码识别结果为:',captcha_result)
    #         captcha_input = web_page.find("苏州银行-个人版验证码输入框")    
    #         web_page.find("苏州银行-个人版验证码输入框").click()   
    #         for i in range(1,4):
    #             captcha_input.input(captcha_result)
    #             text = captcha_input.get_text()
    #             if text == captcha_result:
    #                 break
    #             if i == 3:
    #                 raise Exception("验证码输入失败，请手动登录")
    #         if web_page.is_element_displayed("苏州银行-个人版验证码状态"):
    #             web_page.find("苏州银行-个人版验证码图片").click()
    #         else:
    #             break
    # if web_page.is_element_displayed("江苏银行-个人版验证码识别图片"):

    #     for i in range(1,3):
    #         captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
    #                                                         ele = package.selector("江苏银行-个人版验证码识别图片"),
    #                                                         captcha_type = '10103',
    #                                                         token = '')
    #         print('验证码识别结果为:',captcha_result)
    #         captcha_input = web_page.find("江苏银行-个人版验证码输入框")    
    #         web_page.find("江苏银行-个人版验证码输入框").input(captcha_result)
    #         # for i in range(1,4):
    #         #     captcha_input.input(captcha_result)
    #         #     text = captcha_input.get_text()
    #         #     if text == captcha_result:
    #         #         break
    #         #     if i == 3:
    #         #         raise Exception("验证码输入失败，请手动登录")
            
    #         web_page.find("江苏银行-个人版登录按钮").click()
    #         if web_page.is_element_displayed("江苏银行-个人版登录之后的提示"):
    #             result=web_page.find('江苏银行-个人版登录之后的提示内容').get_text()
    #             if "验证" in result:
    #                 web_page.find("江苏银行-登录之后的提示确定按钮").click()
    #             else:
    #                 break
        
        
        
    #     else:
    #         web_page.find("江苏银行-个人版登录按钮").click()
            


    # cache_folder = get_xbot_activity_cache_folder("activity_jfbym")  
    # print(cache_folder)
    # captcha_x,captcha_y,captcha_width,captcha_height = web_page.find('绵阳市商业银行-验证码图片大框').get_bounding(relative_to='screen')
    # tip_x,tip_y,tip_width,tip_height = web_page.find('绵阳市商业银行-验证码提示大框').get_bounding(relative_to='screen')       
    # # print(captcha_x, captcha_y, captcha_x + captcha_width, tip_y + tip_height) 
    # captcha_path = os.path.join(cache_folder, "screen_img.png")   
    # xbot.win32.screenshot.save_screen_to_file(captcha_path, "png", captcha_x, captcha_y, captcha_x + captcha_width, tip_y + tip_height)
    
    # captcha_result2 = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="66", third_party_code="ttshitu_66_predict", image_source="image_file", 
    #                                                   image_file=captcha_path, image_browser=None, image_web_selector=None, image_window=None, image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser=None, imageback_web_selector=None, imageback_window=None, imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="")
    
    # print(captcha_result2)
    
    # print(captcha_result)
    # if web_page.is_element_displayed("成都农商银行-登录失败原因"):
    #     load_result=web_page.find('成都农商银行-错误说明').get_text()
    #     raise Exception(f'登录失败，原因为{load_result}')
    # captcha_input.input('111')
    # cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    # web_page.start_monitor_network(url='https://ebank.cdrcbank.com/perbank/VerifyImage?update=*',use_wildcard=True,resource_type='Image')
    # url = "https://ebank.cdrcbank.com/perbank/"
    # web_page.navigate(url,load_timeout=40)
    # result = web_page.get_responses()
    # web_page.stop_monitor_network()
    # print(result)
    # img_base64 =result[0]['body'] 
    # img_path = os.path.join(cache_folder, "std_slider.gif")
    # image_data = base64.b64decode(img_base64)
    # with open(img_path, 'wb') as f:
    #     f.write(image_data)
    # captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="4", third_party_code="ttshitu_4_predict", image_source="image_file", image_file=img_path, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None)
    # print(captcha_result)
    
    
    
    # if web_page.is_element_displayed("成都农商银行-网银公告"):
    #     print('111111')
    #     web_page.find('成都农商银行-公告关闭按钮').click(simulative=False)
    # if web_page.is_element_displayed("广东华兴银行-请点此安装控件"):
    #     raise Exception('当前环境为安装银行控件，请检查控件是否安装')
    # username_input = web_page.find("广东华兴银行-账号输入框")
    # web_page.find("广东华兴银行-账号输入框").click()
    # username_input.input('212')

    # password_input = web_page.find("广东华兴银行-密码输入框")
    # password_input.click()
    # win32.send_keys('',hardware_driver_input=True)
    # # password_input.input('21',simulative=False,hardware_driver_input=True)
    #     # 等待
    # sleep(2)
    # web_page.find("广东华兴银行-验证码输入框").click()
    # ym_token = ''
    # if web_page.is_element_displayed("广东华兴银行-验证码图像"):
    # # 判断验证码是否可见
    #     print(std_alphanum_captcha.handle_captcha(web_page = web_page,ele = package.selector("广东华兴银行-验证码图像"),captcha_type = '10103',token = ym_token))
    # print(std_alphanum_captcha.handle_captcha()

    # [{'type': 'Image', 'url': 'https://ebank.cdrcbank.com/perbank/VerifyImage?update=0.2075667409677604', 'status': 200, 'headers': {'Cache-Control': 'no-cache', 'Connection': 'Keep-alive', 'Content-Type': 'image/gif', 'Date': 'Mon, 28 Oct 2024 06:47:40 GMT', 'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT', 'Pragma': 'No-cache', 'Server': 'default', 'Transfer-Encoding': 'chunked', 'Via': '1.1 ID-0314217255324612 uproxy-2', 'X-Frame-Options': 'SAMEORIGIN'}, 'body': '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', 'requestHeaders': {'Referer': 'https://ebank.cdrcbank.com/perbank/', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36', 'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"'}, 'method': 'GET', 'base64Encoded': True}]