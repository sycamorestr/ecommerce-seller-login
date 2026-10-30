import xbot
from xbot import print
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .utils import gen_selector
from .get_group_list import get_group_list


def hide_group(web_page: WebBrowser, group_name, hide_all: bool = False):
    '''收起分组。支持单个字符串或列表。'''
    if isinstance(group_name, str):
        group_name = [group_name]

    target_groups = get_group_list(web_page) if hide_all else (group_name or [])

    for name in target_groups:
        group_xpath = (
            '//div[contains(@class,"kd-fluid-ct-title")]/parent::*[not(contains(@style,"display"))]'
            f'//span[@class="kd-fluid-ct-title-text"][contains(., "{name.strip()}")]/following-sibling::span[not(contains(@class, "kd-fluid-ct-title-extbtn-"))]'
        )
        group_selector = gen_selector(group_xpath, '分组收起按钮')
        if web_page.is_element_displayed(group_selector):
            web_page.find(group_selector).click()

    return web_page


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        hide_group(web_page, '', hide_all=True)
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    group_name = args.get('group_name', '')
    hide_all = args.get('hide_all', False)
    args['out_web_page'] = hide_group(web_page, group_name, hide_all)
