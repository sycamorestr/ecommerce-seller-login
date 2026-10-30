import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        验证重试次数 = 5
        账号 = ""
        密码 = ""
        浏览器类型 = ""
    else:
        验证重试次数 = args.get("验证重试次数", 5)
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        浏览器类型 = args.get("浏览器类型", "")
    try:
        variable = xbot_visual.programing.variable(value=lambda: {"影刀浏览器":'cef',"Google Chrome浏览器":"chrome","Microsoft Edge浏览器":"edge","Firefox浏览器":"firefox"}
        , _block=("爱库存登录", 1, "设置变量"))
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证重试次数, step="1", _block=("爱库存登录", 2, "For次数循环")):
            web_page = xbot_visual.process.invoke_module(module="utils", package=__name__, function="sdk_create_web_page", params={
                "url": "https://merc.aikucun.com/login.html",
                "mode": lambda: variable[浏览器类型],
                "load_timeout": lambda: 30,
                "stop_if_timeout": True,
            }, _block=("爱库存登录", 3, "调用模块"))
            xbot_visual.web.element.input(browser=web_page, element=package.selector("用户名"), text=账号, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("爱库存登录", 4, "填写输入框(web)"))
            xbot_visual.web.element.input_password(browser=web_page, element=package.selector("密码框"), text=xbot_visual.decrypt(密码), input_check=False, retry_times="3", simulate=True, save_to_clipboard=False, input_type="simulate", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", timeout="20", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", _block=("爱库存登录", 5, "填写密码框(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("登录"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("爱库存登录", 6, "点击元素(web)"))
            for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="20", step="1", _block=("爱库存登录", 7, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("登录"), _block=("爱库存登录", 8, "IF 元素可见(web)")):
                    break
                else:
                    # web.element.click
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("刷新元素_1"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("爱库存登录", 12, "点击元素(web)"))
                    # xbot_extensions.activity_jfbym.std_slider_captcha
                    try:
                        xbot_visual.process.run(process="xbot_extensions.activity_4f0f15d7.slider_captcha", package=__name__, inputs={
                            "web_page": web_page,
                            "background_ele": package.selector("图形_2"),
                            "slider_ele": package.selector("爱库存_滑块元素"),
                            "drag_ele": package.selector("图片_dx_captcha_basic_slider-img-normal_1_1"),
                            "retry_count": lambda: 1,
                            "offset": lambda: -4,
                            "move_speed": "fast",
                            }, outputs=[
                        ], _block=("爱库存登录", 14, "滑块拼图验证免费版(web)"))
                    except Exception as e:
                        xbot_visual.programing.log(type='info',text=e,_block=("爱库存登录", 14,"滑块拼图验证免费版(web)"))
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("爱库存登录", 15, "等待"))
                #endif
            #endloop
            if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="not_contains_element", selector=package.selector("登录"), text="", _block=("爱库存登录", 18, "IF 网页包含")):
                xbot_visual.programing.log(type="info", text="登录成功", _block=("爱库存登录", 19, "打印日志"))
                return
            else:
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("帐号或密码不正确，剩余79次机..."), text="", _block=("爱库存登录", 22, "IF 网页包含")):
                    raise Exception("账号密码错误")
                #endif
            #endif
        #endloop
        raise Exception("验证码" + xbot_visual.sh_str(验证重试次数) + "次未通过，登录失败")
    finally:
        args["web_page"] = web_page
