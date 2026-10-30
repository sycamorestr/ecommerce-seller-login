# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv


def get_shopname_xpath(platform_name):
    return  {
    "拼多多推广平台"    : '//*[contains(@class, "AccountNew_mallName")]',
    "拼多多商家后台"    : '(//span[@class="user-name-text"])[1]',
    "拼多多对账中心"    : '//span[contains(@class, "header_name")]',
    "京准通"           : '//*[@class="jzt-user-pin"]',
    "京东商智-品牌版"   : '//*[@ng-model="userName"]',
    "京东商智-商家版"   : '(//*[@class="shop-name"])[1]',
    # "引力魔方"         : '//*[text()="退出"]/..',
    # "品销宝"           : '//*[@mxv="configs"]/div[1]',
    "生意参谋"          : '//span[contains(@class, "module-title")]',
    "巨量千川"          : "//*[@class='shop-name']",
    "抖店/电商罗盘"      : '//*[contains(@class, "userName")]',
    "巨量引擎"      : '//div[@id="header-user" or @id="navigator-right-account" or @class="navigator-user-button"]',
}[platform_name]



def main(args):
    platform_name = args.get("平台名称")
    # platform_name = "引力魔方"
    page = args.get("web_page")

    # 这四个平台到生意参谋去拿
    almm = ["引力魔方", "品销宝", "阿里妈妈", "万相台"]
    if platform_name in almm:
        url = "https://sycm.taobao.com/portal/home.htm"
        xpath = '//span[contains(@class, "module-title")]'
        page = web.create(url, mode="chrome", load_timeout=120)
        sleep(2)
        try:
            args["店铺名"] = page.find_by_xpath(xpath).get_text().strip()
        except:
            pass
        page.close()
    else:
        xpath = get_shopname_xpath(platform_name)
        args["店铺名"] = page.find_by_xpath(xpath).get_text().strip()


    print("店铺名: ", args.get("店铺名"))
    return args.get("店铺名")

