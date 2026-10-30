# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv
import os, json, time
import xbot_visual
import datetime

# 针对chrome已打开运行，不能使用更改配置文件的方式切换配置
# 1. 获取当前chrome配置文件存放目录，不适用默认路径是因为可能存在多版本chrome存在的情况
# 2. 读取配置文件，获取当前配置默认下载目录，以及是否开启了询问下载保存
# 3. 如果开启询问保存路径则主动关闭

def sort_file_by_create_time(dir_path):
    return xbot_visual.dir.find_files(path=dir_path, patterns="*.*", find_subdir=False, skip_hidden_file=False, is_sort=True, sort_by="create_time", sort_way="decrease", _block=("__内置指令", 14, "获取文件列表"))


# 获取当前浏览器配置路径
def _get_chrome_pref_path():
    url = "chrome://version/"
    page = web.create(url, mode="chrome")
    page.reload(ignore_cache=True)
    # time.sleep(3)

    wnd = win32.get_active()
    pref_dir = wnd.find("版本_个人资料路径").get_text()

    pref_path = os.path.join(pref_dir, "Preferences")
    page.close()
    return pref_path

def get_pref_path():
    default_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\Preferences"
    
    # 获取文件状态信息
    if os.path.exists(default_path):
        file_stat = os.stat(default_path)
        
        t = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        minute = (datetime.datetime.now() - t).seconds // 60 
        
        # 默认配置文件24个小时内存在过更新则认为有效
        if minute < 60 * 24:
            return default_path

    return _get_chrome_pref_path()


def close_prompt_download():
    url = "chrome://settings/downloads"
    page = web.create(url, mode="chrome")
    wnd = win32.get_active()
    wnd.find("设置_下载设置_下载前询问每个文件的保存位置_按钮").click()
    page.reload(ignore_cache=True)
    page.close()
    # sleep(3)

def main(args):

    # 获取配置文件路径
    pref_path = get_pref_path()
    # 解析配置文件
    with open(pref_path, "r", encoding="utf-8") as f:
        pref = json.load(f)
    # 获取配置
    default_download_path = pref.get("download").get("default_directory")
    is_prompt = pref.get("download").get("prompt_for_download")
    print(default_download_path)
    if not default_download_path:
        raise Exception("配置文件内没有找到默认文件路径，请手动前往chrome://settings/downloads重新设置保存路径设置后重试。")
    # print(pref_path)
    # print(default_download_path)
    # print(is_prompt)

    
    args["是否弹窗下载"] = is_prompt
    if is_prompt:
        # 关闭保存路径询问
        #close_prompt_download()
        pass
    
    args["默认下载路径"] = default_download_path or os.path.join(os.path.expanduser("~"), "Downloads")
    args["下载路径下已存在文件数"] = len(sort_file_by_create_time(args["默认下载路径"]))
    