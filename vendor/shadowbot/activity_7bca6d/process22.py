import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # web.get
        web_page = xbot_visual.web.create(web_type="chrome", value="www.baidu.com", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("测试_抖店登录", 2, "打开网页"))
        # process.run
        process_result2 = xbot_visual.process.run(process="process4", package=__name__, inputs={
            "username": "",
            "password": "",
            "验证邮箱": "",
            "邮箱授权码": "",
            "获取授权码间隔时长": lambda: 20,
            "验证码失败最大重试次数": lambda: 10,
            "退出已登录账户": True,
            "retry_cnt": lambda: 3,
            "网页对象": lambda: web_page,
            }, outputs=[
            "web_page",
        ], _block=("测试_抖店登录", 4, "调用流程"))
        # web.browser.get_details
        # xbot_extensions.activity_47680f64.latest_email
    finally:
        pass
