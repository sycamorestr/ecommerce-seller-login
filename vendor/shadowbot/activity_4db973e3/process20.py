import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    识别结果 = ""
    if args is None:
        网页对象 = None
        验证码元素 = None
        账号 = ""
        密码 = ""
        验证码类型 = ""
        软件ID = "96001"
    else:
        网页对象 = args.get("网页对象", None)
        验证码元素 = args.get("验证码元素", None)
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        验证码类型 = args.get("验证码类型", "")
        软件ID = args.get("软件ID", "96001")
    try:
        xbot_visual.win32.clipboard_clear()
        dir_path = xbot_visual.dir.get_special_dir(special_dir_name="TEMP", _block=("超级鹰验证码识别", 2, "获取系统文件夹路径"))
        screenshot_save_file_name = xbot_visual.web.element.screenshot(browser=网页对象, capture_area="Element", element=验证码元素, folder_path=dir_path, random_filename=True, filename=None, overwrite_file=True, save_to_clipboard=False, height="25000", piece_height="3000", timeout="20", _block=("超级鹰验证码识别", 3, "网页截图"))
        识别结果 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="code_recognize", params={
            "username": 账号,
            "password": 密码,
            "softid": 软件ID,
            "codetype": 验证码类型,
            "image_path": screenshot_save_file_name,
        }, _block=("超级鹰验证码识别", 4, "调用模块"))
        xbot_visual.file.remove(paths=screenshot_save_file_name, _block=("超级鹰验证码识别", 5, "删除文件"))
    finally:
        args["识别结果"] = 识别结果
