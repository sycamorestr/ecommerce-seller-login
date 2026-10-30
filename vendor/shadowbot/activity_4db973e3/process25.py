import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process24", package=__name__, inputs={
            "账号": "",
            "密码": "",
            "验证码类型": "5000",
            "本地图片路径": "\\\\Mac\\Home\\Desktop\\突出颜色\\图片55.png",
            "软件ID": "",
            }, outputs=[
            "识别结果",
        ], _block=("测试-超级鹰本地验证码识别", 1, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.识别结果, _block=("测试-超级鹰本地验证码识别", 2, "打印日志"))
    finally:
        pass
