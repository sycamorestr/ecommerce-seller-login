# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

from cgi import test
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
        nickname = "测试RPA"
        name = "江诚"
        password = ""
        role_id = "16808677948111"
        auth_device = "1"
        is_update_person_info = "1"
        is_limit_login = "1"
        is_two_step_verify = "1"
        allow_login_windows = "1"
        allow_login_mac = "1"
        allow_login_android = "1"
        allow_login_web = "1"
        allow_login_ios = "1"
        allow_login_miniprog = "1"
        department_ids = "17022947974301"
        login_limit_start_time = "09:00"
        login_limit_end_time = "18:00"
        login_limit_start_date = "2026-02-24"
        login_limit_end_date = "2026-02-24"
        create_result = zn.create_account(nickname, name, password, role_id, auth_device, is_update_person_info, is_limit_login, is_two_step_verify, allow_login_windows, allow_login_mac, allow_login_android, allow_login_web, allow_login_ios, allow_login_miniprog, department_ids, login_limit_start_time, login_limit_end_time, login_limit_start_date, login_limit_end_date)
        print(create_result)
        exit()

def main(args):
    test_func()
    ziniao_instance: ZiniaoAPI = args.get("ziniao_instance")
    nickname = args.get("nickname")
    name = args.get("name")
    password = args.get("password")
    role_id = args.get("role_id")
    auth_device = args.get("auth_device")
    is_update_person_info = args.get("is_update_person_info")
    is_limit_login = args.get("is_limit_login")
    is_two_step_verify = args.get("is_two_step_verify")
    allow_login_windows = args.get("allow_login_windows")
    allow_login_mac = args.get("allow_login_mac")
    allow_login_android = args.get("allow_login_android")
    allow_login_web = args.get("allow_login_web")
    allow_login_ios = args.get("allow_login_ios")
    allow_login_miniprog = args.get("allow_login_miniprog")
    department_ids = args.get("department_ids")
    login_limit_start_time = args.get("login_limit_start_time", None)
    login_limit_end_time = args.get("login_limit_end_time", None)
    login_limit_start_date = args.get("login_limit_start_date", None)
    login_limit_end_date = args.get("login_limit_end_date", None)

    assert isinstance(ziniao_instance, ZiniaoAPI), "请选择紫鸟对象"
    create_result = ziniao_instance.create_account(nickname, name, password, role_id, auth_device, is_update_person_info, is_limit_login, is_two_step_verify, allow_login_windows, allow_login_mac, allow_login_android, allow_login_web, allow_login_ios, allow_login_miniprog, department_ids, login_limit_start_time, login_limit_end_time, login_limit_start_date, login_limit_end_date)
    args["create_result"] = create_result

