import xbot
from xbot import print
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .utils import gen_selector


def get_all_tab(web_page: WebBrowser):
    '''获取当前页面所有 Tab 标题。'''
    all_tab_xpath = '//li[contains(@class, "contentHeadEL kd_sortable")]'
    all_tab_selector = gen_selector(all_tab_xpath, '所有标签页')

    if not web_page.is_element_displayed(all_tab_selector):
        raise Exception(f'标签元素不存在，定位：{all_tab_xpath}')

    all_tab_list = web_page.find_all(all_tab_selector)
    return [tab.get_text() for tab in all_tab_list]


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        tabs = get_all_tab(web_page)
        print(tabs)
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    args['out_all_tab_list'] = get_all_tab(web_page)
