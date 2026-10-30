import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        # https://dun.163.com/trial/picture-click
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-坐标点选验证", 2, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试-坐标点选验证", 2,"获取已打开的网页对象"))
            time.sleep(3)
        _ = xbot_visual.process.run(process="process21", package=__name__, inputs={
            "网页对象": lambda: web_page,
            "验证码图片": package.selector("唯品会验证码背景"),
            "点选提示": package.selector("块元素_1"),
            "识别模式": "点选3个坐标",
            "图鉴账号": "",
            "图鉴密码": "",
            }, outputs=[
        ], _block=("测试-坐标点选验证", 3, "调用流程"))
        # web_service.captcha_paid
        # win32.move_mouse
    finally:
        pass
