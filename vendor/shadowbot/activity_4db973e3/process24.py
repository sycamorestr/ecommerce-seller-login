import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    识别结果 = ""
    if args is None:
        账号 = ""
        密码 = ""
        验证码类型 = ""
        本地图片路径 = ""
        软件ID = ""
    else:
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        验证码类型 = args.get("验证码类型", "")
        本地图片路径 = args.get("本地图片路径", "")
        软件ID = args.get("软件ID", "")
    try:
        识别结果 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="code_recognize", params={
            "username": 账号,
            "password": 密码,
            "softid": 软件ID,
            "codetype": 验证码类型,
            "image_path": 本地图片路径,
        }, _block=("超级鹰本地验证码识别", 1, "调用模块"))
    finally:
        args["识别结果"] = 识别结果
