# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os

import xbot
from xbot import print, sleep, web

from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler


def goods_list_download(web_page, goods_type, file_folder, file_name):
    """进行商品列表的下载"""

    # 轮询判断temu店铺是否有商品列表模块
    for _ in range(2):
        # 获取当前站点域名
        url = web_page.get_url()
        if 'goods/list' in url:
            break
            
        # 获取网站域名
        domain_url = Tools.get_domain_from_url(url)
        # 进行页面跳转
        web_page.navigate(f'{domain_url}/goods/list')
    else:
        raise Exception('未找到商品列表模块')

    # 进行商品类型点击
    goods_type_xpath = f'//div[contains(@class,"TAB_tabContentInnerContainer")]//div[contains(text(),"{goods_type}")]'
    web_page.find_by_xpath(goods_type_xpath).click()

    # 等待数据加载完毕，下载结果信息更新
    Tools.wait_loading(web_page)

    # 点击下载查询结果
    query_download_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[contains(text(),"下载查询结果")]'
    web_page.find_by_xpath(query_download_xpath).click()

    # 点击导出
    export_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[text()="导出"]'
    web_page.find_by_xpath(export_xpath).click()

    # 进行下载配置
    file_path = download_handler(
        web_page=web_page,
        file_folder=file_folder,
        file_name=file_name
    )
    
    return file_path

def test():
    """测试模块"""
    if "xbot_extensions" in __file__:
        return
        
    web_page = web.get_active(mode='superbrowser')
    file_folder = os.path.join(os.path.expanduser('~'),'Desktop\导出列表+财务明细')
    file_name = '12'
    goods_list_download(web_page, '未发布到站点', file_folder, file_name)
    exit()


def main(args):
    # 测试模块
    test()

    # 功能模块
    web_page = args.get('web_page')
    goods_type = args.get('goods_type','全部')
    print(goods_type)
    desktop = os.path.join(os.path.expanduser('~'),'Desktop')
    file_folder= args.get('file_folder',f'{desktop}')
    file_name = args.get('file_name')

    # 调用函数
    file_path = goods_list_download(web_page, goods_type, file_folder, file_name)
    args['file_path'] = file_path

