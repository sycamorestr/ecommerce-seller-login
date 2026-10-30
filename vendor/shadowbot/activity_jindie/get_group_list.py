import xbot
from xbot import print
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .utils import gen_selector


def get_group_list(web_page: WebBrowser):
    '''获取当前表单所有分组标题。'''
    group_xpath = '//div[contains(@class,"kd-fluid-ct-title")]/parent::*[not(contains(@style,"display"))]//span[@class="kd-fluid-ct-title-text"]'
    group_selector = gen_selector(group_xpath, '分组列表')

    if not web_page.is_element_displayed(group_selector):
        raise Exception(f'分组元素不存在，定位：{group_xpath}')

    group_list = web_page.find_all(group_selector)
    return [g.get_text() for g in group_list]


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        groups = get_group_list(web_page)
        print(groups)
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    args['out_group_list'] = get_group_list(web_page)
