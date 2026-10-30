import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process44", package=__name__, inputs={
            "查询日期": "月",
            "保存文件夹": "C:\\Users\\sjcjj\\Desktop\\env_text\\工作测试",
            "开启页面统计时间校验": True,
            "web_page": lambda: None,
            }, outputs=[
            "输出文件路径",
            "执行状态",
            "数据集对象列表",
        ], _block=("测试-首页-运营视窗-整体看板数据", 1, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.数据集对象列表, _block=("测试-首页-运营视窗-整体看板数据", 2, "打印日志"))
        #region 获取数据测试
        # programing.variable
        # web.get
        # web.element.get_all_elements
        # web.element.get_all_elements
        # web.element.get_all_elements
        # workflow.if
        # programing.raise
        # workflow.endif
        # list.append_or_insert
        # workflow.for
        # programing.variable
        # programing.variable
        # programing.log
        # programing.variable
        # list.append_or_insert
        # workflow.endloop
        # programing.log
        # programing.snippet
        #endregion
    finally:
        pass
