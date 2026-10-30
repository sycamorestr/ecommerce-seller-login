import xbot
from xbot import print
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .input_data import input_data


def batch_input_data(web_page: WebBrowser, data_list: list):
    '''批量填写字段数据。
    data_list 每项格式：{"group_name": "基本信息", "key": "供应商", "value": "E00001"}
    '''
    for item in (data_list or []):
        group_name = item.get('group_name')
        key = item.get('key')
        value = item.get('value')

        if not group_name or not key:
            print(f'跳过无效项：{item}')
            continue

        input_data(web_page, group_name, key, value)

    return web_page


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        data_list = [
            {'group_name': '基本信息', 'key': '单据编号', 'value': 'E00001'},
        ]
        batch_input_data(web_page, data_list)
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    data_list = args.get('data_list')
    args['out_web_page'] = batch_input_data(web_page, data_list)
