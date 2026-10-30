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
        department_list = zn.query_department_list()
        print(department_list)
        exit()

def main(args):
    test_func()
    ziniao_instance: ZiniaoAPI = args.get("ziniao_instance")
    
    assert isinstance(ziniao_instance, ZiniaoAPI), "请选择紫鸟对象"
    department_list = ziniao_instance.query_department_list()
    args["department_list"] = department_list
