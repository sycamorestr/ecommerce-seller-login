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
        staff_ids = "17719310817969"
        delete_result = zn.delete_account(staff_ids)
        print(delete_result)
        exit()

def main(args):
    test_func()
    ziniao_instance: ZiniaoAPI = args.get("ziniao_instance")
    staff_ids = args.get("staff_ids")
    status = args.get("status", "2")
    
    assert isinstance(ziniao_instance, ZiniaoAPI), "请选择紫鸟对象"
    delete_result = ziniao_instance.delete_account(staff_ids, status)
    args["delete_result"] = delete_result
