import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        品牌帖子网址 = ""
        文件路径 = ""
        标题 = ""
        asin列表 = []
        开始时间 = ""
        结束时间 = ""
        发送类型 = ""
    else:
        网页对象 = args.get("网页对象", None)
        品牌帖子网址 = args.get("品牌帖子网址", "")
        文件路径 = args.get("文件路径", "")
        标题 = args.get("标题", "")
        asin列表 = args.get("asin列表", [])
        开始时间 = args.get("开始时间", "")
        结束时间 = args.get("结束时间", "")
        发送类型 = args.get("发送类型", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_ad_api", package=__name__, function="upload_post", params={
            "web_page": 网页对象,
            "post_url": 品牌帖子网址,
            "post_type": 发送类型,
            "file_path": 文件路径,
            "title": 标题,
            "asin_list": asin列表,
            "start_time": 开始时间,
            "end_time": 结束时间,
        }, _block=("E4 发送POST", 1, "调用模块"))
    finally:
        pass
