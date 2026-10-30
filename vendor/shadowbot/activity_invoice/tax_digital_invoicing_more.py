# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from datetime import datetime
from .api_enum import *
from .tax_invoice_api import TaxInvoiceAPI

def main(args):
    api = args.get('invoice_instance', None)
    if api is None or not isinstance(api, TaxInvoiceAPI): raise Exception('系统未登录')
    zzstsgl = "免税" if args.get("lslbs") == "免税" else ""
    yhzcbs = "使用" if args.get("lslbs") == "免税" else args.get("yhzcbs")

    fpkjxx_fptxx = {
        "fpqqlsh": "RPAYD" + str(datetime.now().strftime("%Y%m%d%H%M%S")),
        "kpxm": args.get("kpxm"),
        "kplx": APIMappingEnum.KPLX_MAPPING.value['蓝票'],
        "xhfmc": '',
        "xhf_dz": '',
        "xhf_dh": '',
        "xhf_yh": '',
        "xhf_zh": '',
        "ghfqylx": APIMappingEnum.GHFQYLX_MAPPING.value[args.get("ghfqylx")],
        "ghfmc": args.get("ghfmc"),
        "ghf_nsrsbh": args.get("ghf_nsrsbh"),
        "ghf_dz": args.get("ghf_dz"),
        "ghf_dh": args.get("ghf_dh"),
        "ghf_yh": args.get("ghf_yh"),
        "ghf_zh": args.get("ghf_zh"),
        "sfzsgmfyhzh": args.get("sfzsgmfyhzh"),
        "sfzsxsfyhzh": args.get("sfzsxsfyhzh"),
        "fpzl_dm": APIMappingEnum.FPZL_ZM_MAPPING.value[args.get("fpzl_dm")],
        "xsfzrr_bz": args.get("xsfzrr_bz"),
        "gmfzrr_bz": args.get("gmfzrr_bz"),
        "sfkqzdrz": "false",
        "type": "",
        "kphjje": args.get("kphjje"),
        "bz": args.get("bz")
    }
    
    fpkjxx_xmxxs = args.get('fpkjxx_xmxxs')

    response = api.issue_invoice(fpkjxx_fptxx=fpkjxx_fptxx, fpkjxx_xmxxs=fpkjxx_xmxxs)
    if response.get('result') == 'f':
        raise Exception('请求失败：{}'.format(response['response']['msg']))

    args['invoiced_result'] = response