# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import get_domain
from xbot._core.retry import Retry


def switch_old_ui(web_page):
    """切换亚马逊旧版ui界面"""

    # 进行切换旧版页面
    for _ in Retry(timeout=20, ignore_exception=True):
        # 获取买家中心旧版页面连接
        saller_center_xpath = '//*[@id="Classic Seller Central" or @id="传统卖家平台"]'
        old_url = web_page.find_all_by_xpath(saller_center_xpath, timeout=3)

        # 判断是否处于新版页面
        if len(old_url) == 0:
            print('当前页面处于旧版页面，不进行切换操作')
            return

        # 进行连接重组
        domain = get_domain(web_page)
        url = domain + old_url[0].get_attribute('data-value')
        web_page.navigate(url)
        web_page.wait_load_completed()
        print('亚马逊旧版页面切换成功')
        return
    else:
        raise Exception('旧版页面切换失败')


def test():
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active('ziniaobrowser')
    switch_old_ui(web_page)
    exit()

def main(args):
    test()
    web_page = args.get('web_page')
    switch_old_ui(web_page)
