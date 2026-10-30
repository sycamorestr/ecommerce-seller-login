# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot import web


def get_start_args(args):
    args_map = {
        "窗口最大化": "--start-maximized",
        "每个TAB使用单独进程": "--process-per-tab",
        "每个站点使用单独进程": "--process-per-site	",
        "调试端口": "--remote-debugging-port={}",
        "禁用弹窗阻止": "--disable-popup-blocking",
        "缓存路径": '--disk-cache-dir="{}"',
        "禁用缓存": "--disk-cache-dir=null --disk-cache-size=1",
        "禁用图片": "--disable-images"
    }

    # 拼接启动参数字符串
    start_args = []
    for key, val in args.items():
        if not val or key not in args_map:
            continue
        
        if key in ["调试端口", "缓存路径"]: 
            start_args.append(args_map[key].format(val))
        else:
            start_args.append(args_map[key])

    return " ".join(start_args)


def main(args):
    url = args.get("URL")
    time_out = args.get("超时时长")

    arguments = get_start_args(args)

    # print(arguments)
    args["web_page"] = web.create(url, mode="chrome", load_timeout=time_out, arguments=arguments)
    return args["web_page"]
