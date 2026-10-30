import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # system.run_or_open
        process_result = xbot_visual.process.run(process="open_store", package=__name__, inputs={
            "店铺名称": "美国亚马逊",
            "匹配类型": "相等",
            "打开账号": "点击",
            "超时时间": lambda: 50,
            "隐私模式": False,
            "处理在线人员上限": "取 消",
            }, outputs=[
            "web_page",
            "完整店铺名称",
        ], _block=("main", 2, "调用流程"))
        # process.run
    finally:
        pass
