import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    文件路径 = ""
    if args is None:
        是否弹窗下载 = ""
        保存文件夹 = ""
        文件名 = "不带扩展名"
        下载前文件数量 = ""
        浏览器下载保存路径 = ""
        最大等待时长 = 120
    else:
        是否弹窗下载 = args.get("是否弹窗下载", "")
        保存文件夹 = args.get("保存文件夹", "")
        文件名 = args.get("文件名", "不带扩展名")
        下载前文件数量 = args.get("下载前文件数量", "")
        浏览器下载保存路径 = args.get("浏览器下载保存路径", "")
        最大等待时长 = args.get("最大等待时长", 120)
    try:
        if xbot_visual.workflow.test(operand1=是否弹窗下载, operator="is true", operand2="", operator_options="{}", _block=("下载一个文件", 1, "IF 条件")):
            文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=False, file_name=None, wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout=最大等待时长, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("下载一个文件", 2, "处理下载对话框"))
        else:
            无弹窗下载 = xbot_visual.process.run(process="DownAndMoveFile", package=__name__, inputs={
                "等待下载完成最大时长": lambda: 最大等待时长,
                "浏览器下载保存路径": lambda: 浏览器下载保存路径,
                "是否重命名": True,
                "重命名_文件名": 文件名,
                "下载前文件数量": lambda: 下载前文件数量,
                "保存文件夹路径": 保存文件夹,
                }, outputs=[
                "文件路径列表",
            ], _block=("下载一个文件", 4, "调用流程"))
            文件路径 = 无弹窗下载.文件路径列表[0]
        #endif
    finally:
        args["文件路径"] = 文件路径
