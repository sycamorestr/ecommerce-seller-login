# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import os
import re
import xbot
import winreg

import xml.etree.ElementTree as ET

from xbot import print, sleep
from .import package
from .package import variables as glv


def _get_ziniao_product_name():
    """获取紫鸟插件的名称"""
    ziniao_exe_list = ["superbrowser.exe", "ziniaobrowser.exe"]
    ziniao_product_name_list = []

    config_path = os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Local",
        "ShadowBot",
        "ChromiumBrowser.config",
    )
    if not os.path.exists(config_path):
        return ziniao_product_name_list

    # 解析XML文件
    tree = ET.parse(config_path)
    root = tree.getroot()

    # 查找匹配的产品名称
    for browser in root.findall(".//ChromiumBrowserInfo"):
        exe_path = browser.find("ExePath").text
        _, exe_name = os.path.split(exe_path)
        if exe_name in ziniao_exe_list:
            ziniao_product_name_list.append(browser.find("ProductName").text)

    return ziniao_product_name_list


def get_all_ziniao_info():
    """获取电脑上安装的全部紫鸟软件, 并获取在对应的browser_mode"""
    # 获取紫鸟的安装路径
    dialog_message = "紫鸟未安装插件或插件安装异常, 参考教程: https://www.yingdao.com/yddoc/rpa/zh-CN/711005983856115712"
    all_zn_info = {}

    ziniao_product_name = _get_ziniao_product_name()
    if not ziniao_product_name:
        xbot.app.dialog.show_message_box("插件异常提示", dialog_message)
        exit()

    reg_keys = [
        r"superbrowser\shell\open\command",
        r"superbrowserv6\shell\open\command",
    ]

    for index, reg_key in enumerate(reg_keys):
        zn_info = {}
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, reg_key) as key:
                value, _ = winreg.QueryValueEx(key, None)
                match = re.search(r'"([^"]*)"', value)
                if match:
                    exe_path = match.group(1)
                    zn_info["version"] = f"v{index+5}"
                    zn_info["exe_path"] = exe_path

        except FileNotFoundError:
            pass

        # TODO: 未自动识别对应的 product_name
        if zn_info.get("version") == "v5":
            zn_info["browser_mode"] = "superbrowser"

        if zn_info.get("version") == "v6":
            zn_info["browser_mode"] = "ziniaobrowser"

        if zn_info:
            all_zn_info[zn_info.get("version")] = zn_info

    return all_zn_info


def main(args):
    args["ziniao_info"] = get_all_ziniao_info()
    pass
