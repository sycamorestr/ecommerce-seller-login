# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .tax_invoice_api import TaxInvoiceAPI

def main(args):
    api =  args.get('invoice_instance', None)
    if api is None or not isinstance(api, TaxInvoiceAPI): raise Exception('系统未登录')


    kplsh = args.get('kplsh', '')
    if not kplsh: raise Exception('开票流水号值为空')

    response = api.query_order(fpqqlsh=kplsh)
    if response.get('result') == 'f':
        raise Exception('请求失败：{}'.format(response['response']['msg']))
    args['invoice_detail'] = response