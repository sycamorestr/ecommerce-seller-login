# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import Tools

def save_screenshot(web_page, folder_path, station):
    Tools.check_web(web_page, 'labor/account')
    img_xpath = "//*[text()='总金额']/../.."
    store_name = web_page.find_by_xpath("//div[contains(@class,'account-info_accountInfo')]/div[2]").get_text().split("\n")[0]

    # 消除信息框
    Tools.handle_info(web_page)

    # 进行点击贷款账户，用于应用中适配智能屏蔽弹窗以及自动处理弹窗指令
    web_page.find_by_xpath('//span[text()="货款账户"]').click()

    web_page.screenshot(folder_path=folder_path, file_name=f"{store_name}-{station}-余额截图.png")
    print(f"{store_name}-{station}-余额截图.png")
    return folder_path + '\\' + f"{store_name}-{station}-余额截图.png"

def main(args):

    web_page = args.get("web_page")
    folder_path = args.get("folder_path", r"C:\Users\11758\Desktop\test")
    station = args.get("station")
    # web_page = web.get_active(mode='chrome')
    img_path = save_screenshot(web_page, folder_path, station)
    args['img_path'] = img_path
