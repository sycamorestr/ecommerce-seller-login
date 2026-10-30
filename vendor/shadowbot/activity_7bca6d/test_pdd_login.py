# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from . import package
from .package import variables as glv
import os
import json
import importlib


def get_flow_pyfile(flow_name):
    path, _ = os.path.split(__file__)
    package_path = os.path.join(path, "package.json")
    with open(package_path, encoding='utf8') as f:
        package_json = json.load(f)
        flows = package_json.get("flows")
        for flow in flows:
            if flow.get("name") == flow_name:
                return flow.get("filename")


def test_pdd_login_main():
    args = {"浏览器类型": "chrome", "账号": "", "密码": ""}
    flow_demo_main = importlib.import_module(
        f"xbot_robot.{get_flow_pyfile('拼多多登录')}")
    flow_demo_main.main(args)
    assert args["输出结果"] == 3, "测试失败"

def main(args):
    test_pdd_login_main()
    pass
