import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        # https://dun.163.com/trial/inference
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-推理图片验证", 2, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info', text=f'第2条指令: {e}')
            time.sleep(3)
        _ = xbot_visual.process.run(process="process16", package=__name__, inputs={
            "网页对象": lambda: web_page,
            "验证码图片": package.selector("测试-推理图片验证码-网易"),
            "图鉴账号": "",
            "图鉴密码": "",
            }, outputs=[
        ], _block=("测试-推理图片验证", 3, "调用流程"))
    finally:
        pass
