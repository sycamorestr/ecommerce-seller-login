import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # process.run
        process_result = xbot_visual.process.run(process="process7", package=__name__, inputs={
            "userid": "",
            "password": "",
            "mode": "edge",
            "path_to_chrome_exe": "",
            "加载超时时间": "20",
            "ym_token": "",
            "是否退出已登录": True,
            "重试次数": lambda: 5,
            }, outputs=[
            "web_page",
        ], _block=("测试_淘宝登录", 2, "调用流程"))
        # web.get
        # web.element.click
        # workflow.for
        # web.browser.contains_element_or_text
        # xbot_extensions.activity_jfbym.ali_slider_captcha
        # workflow.else
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # web.get
        # web.element.get_details
        # asset.get_asset
        # programing.log
        # programing.log
    finally:
        pass
