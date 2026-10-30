import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        验证邮箱 = None
        邮箱授权码 = None
        获取授权码间隔时长 = 0
        验证码失败最大重试次数 = 0
    else:
        web_page = args.get("web_page", None)
        验证邮箱 = args.get("验证邮箱", None)
        邮箱授权码 = args.get("邮箱授权码", None)
        获取授权码间隔时长 = args.get("获取授权码间隔时长", 0)
        验证码失败最大重试次数 = args.get("验证码失败最大重试次数", 0)
    try:
        try:
            邮箱 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[text()=\"邮箱\"]", is_related_parent=False, parent=None, timeout="5", _block=("抖音平台邮箱验证", 1, "获取元素对象(web)"))
        except Exception as e:
            pass
            邮箱 = None
        if xbot_visual.workflow.test(operand1=邮箱, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖音平台邮箱验证", 2, "IF 条件")):
            xbot_visual.web.element.click(browser=web_page, element=邮箱, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖音平台邮箱验证", 3, "点击元素(web)"))
        #endif
        try:
            发送验证码 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[text()=\"发送验证码\"]", is_related_parent=False, parent=None, timeout="4", _block=("抖音平台邮箱验证", 5, "获取元素对象(web)"))
        except Exception as e:
            pass
            发送验证码 = None
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 发送验证码,"operand2": "","operator": "not none"}], _block=("抖音平台邮箱验证", 6, "IF 多条件")):
            # ---------------------------进入-邮箱验证
            if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 邮箱授权码,"operand2": "","operator": "is empty"},{"operand1": 邮箱授权码,"operand2": "","operator": "is empty"}], _block=("抖音平台邮箱验证", 8, "IF 多条件")):
                raise Exception("需要进行邮箱验证， 请正确填写【验证邮箱】和【授权码】后重试！")
            #endif
            xbot_visual.web.element.click(browser=web_page, element=发送验证码, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖音平台邮箱验证", 11, "点击元素(web)"))
            # ---部分项目转发时间比较长，时间拉长点
            xbot_visual.programing.sleep(random_number=False, seconds=获取授权码间隔时长, start_number="1", stop_number="5", _block=("抖音平台邮箱验证", 13, "等待"))
            最新邮件对象 = xbot_visual.process.run(process="xbot_extensions.activity_47680f64.latest_email", package=__name__, inputs={
                "email": 验证邮箱,
                "password": 邮箱授权码,
                "select_from": "INBOX",
                }, outputs=[
                "latest_email",
            ], _block=("抖音平台邮箱验证", 14, "获取收件箱最新的一封邮件"))
            # ---获取到的验证码对象格式： {'text': '【五道口流程中心】任务执行通知：2087, 请关注。', 'send_time': '2023-04-27 08:06:19'}
            邮件内容 = xbot_visual.programing.variable(value=lambda: 最新邮件对象.get("text")
            , _block=("抖音平台邮箱验证", 16, "设置变量"))
            验证码 = xbot_visual.text.extract_content_from_text(text=邮件内容, extract_way="custom", regular_pattern="(?<![a-zA-Z0-9])([a-zA-Z0-9~`!@#$%^&*]{6})(?![a-zA-Z0-9])", just_get_first=True, ignore_case=False, _block=("抖音平台邮箱验证", 17, "从文本中提取内容"))
            if xbot_visual.workflow.test(operand1=验证码, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖音平台邮箱验证", 18, "IF 条件")):
                # ---------提取六位验证码如果是空则匹配4位验证码
                验证码 = xbot_visual.text.extract_content_from_text(text=邮件内容, extract_way="custom", regular_pattern="(?<![a-zA-Z0-9])([a-zA-Z0-9~`!@#$%^&*]{4})(?![a-zA-Z0-9])", just_get_first=True, ignore_case=False, _block=("抖音平台邮箱验证", 20, "从文本中提取内容"))
            #endif
            xbot_visual.programing.log(type="info", text="邮件内容： " + xbot_visual.sh_str(邮件内容), _block=("抖音平台邮箱验证", 22, "打印日志"))
            xbot_visual.programing.log(type="info", text="提取到的验证码： " + xbot_visual.sh_str(验证码), _block=("抖音平台邮箱验证", 23, "打印日志"))
            # ---------输入验证码
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.InputByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpath": "//input[@placeholder=\"验证码\"]",
                "输入内容": 验证码,
                "iframe跨域元素": False,
                "输入方式": "剪切板",
                "追加按键": "{ENTER}",
                "等待元素存在": lambda: 20,
                "操作完成后等待": lambda: 1,
                "追加输入": False,
                }, outputs=[
            ], _block=("抖音平台邮箱验证", 25, "输入内容ByXpath"))
            xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖音平台邮箱验证", 26, "等待"))
            try:
                xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                    "web_page": web_page,
                    "xpathSelector": "//button[text()=\"验证\"]",
                    "获取元素超时": lambda: 5,
                    "执行成功后等待": lambda: 1,
                    "是否模拟人工": False,
                    "按钮": "left",
                    "retry_count": lambda: 1,
                    "refresh": False,
                    "是否为iframe对象": False,
                    }, outputs=[
                ], _block=("抖音平台邮箱验证", 28, "点击Xpath元素"))
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                pass
            #endtry
            # 验证按钮点击后有可能还会再次出现验证
            _ = xbot_visual.process.run(process="process48", package=__name__, inputs={
                "web_page": web_page,
                "验证码失败最大重试次数": 验证码失败最大重试次数,
                }, outputs=[
            ], _block=("抖音平台邮箱验证", 32, "调用流程"))
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码失败最大重试次数, step="1", _block=("抖音平台邮箱验证", 33, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("抖店滑块_图像"), _block=("抖音平台邮箱验证", 34, "IF 元素可见(web)")):
                    break
                #endif
                _ = xbot_visual.process.run(process="process45", package=__name__, inputs={
                    "web_page": web_page,
                    }, outputs=[
                ], _block=("抖音平台邮箱验证", 37, "调用流程"))
            #endloop
        #endif
    finally:
        pass
