import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .utils import gen_selector


def close_tab(web_page: WebBrowser, tab_name):
    '''关闭标签页，支持字符串或列表。'''
    if isinstance(tab_name, str):
        tab_name = [tab_name]

    for name in (tab_name or []):
        tab_xpath = f'//li[contains(@class, "contentHeadEL kd_sortable")]/span[contains(., "{name.strip()}")]'
        tab_selector = gen_selector(tab_xpath, '标签页')
        if not web_page.is_element_displayed(tab_selector):
            continue

        tab_list = web_page.find_all(tab_selector)
        for tab_index, tab_ele in enumerate(tab_list):
            tab_ele.hover()
            close_xpath = f'(//li[contains(@class, "contentHeadEL kd_sortable")]/span[contains(., "{name.strip()}")]/following-sibling::span)[1]'
            close_selector = gen_selector(close_xpath, '关闭按钮')
            if not web_page.is_element_displayed(close_selector):
                raise Exception(f'关闭按钮不存在，定位：{close_xpath}')
            web_page.find(close_selector).click()
            sleep(1)
    return web_page


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        close_tab(web_page, '采购订单 - 新增')
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    tab_name = args.get('tab_name')
    args['out_web_page'] = close_tab(web_page, tab_name)
