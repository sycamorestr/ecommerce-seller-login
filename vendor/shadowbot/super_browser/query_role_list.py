import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .ziniaoapi import ZiniaoAPI

def test_func():
    if "xbot_extensions" not in __file__:
        appid = "202504091359548590430744576"
        appsecret = ""
        zn = ZiniaoAPI(appid, appsecret)
        role_list = zn.query_role_list()
        print(role_list)
        exit()

def main(args):
    test_func()
    ziniao_instance: ZiniaoAPI = args.get("ziniao_instance")
    
    assert isinstance(ziniao_instance, ZiniaoAPI), "请选择紫鸟对象"
    role_list = ziniao_instance.query_role_list()
    args["role_list"] = role_list
