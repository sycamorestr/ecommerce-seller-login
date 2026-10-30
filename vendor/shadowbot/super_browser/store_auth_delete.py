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
        store_id_list = ['16312460989784']
        staff_id = '17703601878008'
        result = zn.store_auth_delete(store_id_list, staff_id)
        print(result)
        exit()

def main(args):
    test_func()
    ziniao_instance: ZiniaoAPI = args.get("ziniao_instance")
    store_id_list = args.get("store_id_list")
    staff_id = args.get("staff_id")
    
    assert isinstance(ziniao_instance, ZiniaoAPI), "请选择紫鸟对象"
    result = ziniao_instance.store_auth_delete(store_id_list, staff_id)
    args["result"] = result
