import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        企业名称 = ""
        企业用户名 = ""
        密码 = ""
        是否填写账号密码 = False
        是否退出登录 = False
        紫鸟版本 = "V5"
    else:
        企业名称 = args.get("企业名称", "")
        企业用户名 = args.get("企业用户名", "")
        密码 = args.get("密码", "")
        是否填写账号密码 = args.get("是否填写账号密码", False)
        是否退出登录 = args.get("是否退出登录", False)
        紫鸟版本 = args.get("紫鸟版本", "V5")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="api", package=__name__, function="login", params={
            "company_name": 企业名称,
            "company_username": 企业用户名,
            "password": 密码,
            "is_fill": 是否填写账号密码,
            "is_close": 是否退出登录,
            "version": 紫鸟版本,
        }, _block=("A4 紫鸟登录", 1, "调用模块"))
    finally:
        pass
