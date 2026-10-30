import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        web_page = xbot_visual.web.create(web_type="chrome", value="https://www.baidu.com", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("测试_拼多多登录", 1, "打开网页"))
        process_result = xbot_visual.process.run(process="process21", package=__name__, inputs={
            "浏览器类型": "edge",
            "账号": "",
            "密码": "",
            "识别引擎": "影刀引擎(付费增值服务)",
            "验证码重试次数": lambda: 5,
            "是否创建新页面": True,
            }, outputs=[
            "网页对象",
        ], _block=("测试_拼多多登录", 2, "调用流程"))
    finally:
        pass
