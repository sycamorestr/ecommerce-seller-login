# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from enum import Enum

def main(args):
    print(APIConfig.MAX_TIME_OUT.value)

class APIConfig(Enum):
    RETRIES_TIMES = 3
    MAX_TIME_OUT = 120


class APIBaseUrl(Enum):
    BASE_URL = 'https://openapi.njmbxx.com'


class APIEndpointEnum(Enum):

    TAX_LOGIN = "/api.svc/was.invsvr/electron.easy/tax_login"
    GET_QR_CODE = "/api.svc/was.invsvr/electron.easy/qrCode_query"
    QUERY_SECONDARY_AUTH_STATUS = "/api.svc/was.invsvr/electron.easy/secondaryAuthenticationStatus_query"
    ISSUE_INVOICE = "/api.svc/was.invsvr/electron.easy/blueInvoiceIssu_gm"
    QUERY_ORDER = "/api.svc/was.invsvr/electron.easy/order_query"
    TOKEN = "/api.svc/oauth_token"


class APIMappingEnum(Enum):
    # 传递给API的责任类型映射
    ZRRLX_MAPPING = {
        "法定代表人": "01",
        "财务负责人": "02",
        "办税员": "03",
        "管理员": "05",
        "领票员": "07",
        "社保经办人": "08",
        "开票员": "09",
        "销售人员": "10"
    }

    # 二维码类型映射
    QR_CODE_TYPE_MAPPING = {
        "税局二维码": "",
        "个税APP二维码": "2"
    }

    # 二维码受理状态映射
    QR_CODE_SLZT_MAPPING = {
        '1': '未扫码',
        '2': '扫码',
        '3': '扫码超时'
    }

    # 开票类型映射
    KPLX_MAPPING = {
        '蓝票': '1',
        '红票': '2'
    }

    # 购货方企业类型映射
    GHFQYLX_MAPPING = {
        '企业': '1',
        '机关事业单位': '2',
        '个人': '3',
        '其他': '4'
    }

    # 发票种类映射
    FPZL_ZM_MAPPING = {
        '增值税专用发票': '81',
        '普通发票': '82'
    }

    # 发票行性质映射
    FPHXZ_MAPPING = {
        '正常商品行': '0',
        '折扣行': '1',
        '被折扣行': '2'
    }

    # 含税标志映射HSBZ_MAPPING
    HSBZ_MAPPING = {
        '含税': '1',
        '不含税': '0'
    }

    # 优惠政策标识映射
    YHZCBS_MAPPING = {
        '不使用': '0',
        '使用': '1'
    }

    # 零税率标识映射
    LSLBS_MAPPING = {
        '非零税率': '',
        '免税': '1',
        '不征税': '2',
        '普通零税率': '3'
    }

    # 省份代码映射
    PROVINCE_CODE_MAPPING = {
        "北京": "1100",
        "天津": "1200",
        "河北": "1300",
        "山西": "1400",
        "内蒙古": "1500",
        "辽宁": "2100",
        "大连": "2102",
        "吉林": "2200",
        "黑龙江": "2300",
        "上海": "3100",
        "江苏": "3200",
        "浙江": "3300",
        "宁波": "3302",
        "安徽": "3400",
        "福建": "3500",
        "厦门": "3502",
        "江西": "3600",
        "山东": "3700",
        "青岛": "3702",
        "河南": "4100",
        "湖北": "4200",
        "湖南": "4300",
        "广东": "4400",
        "深圳": "4403",
        "广西": "4500",
        "海南": "4600",
        "重庆": "5000",
        "四川": "5100",
        "贵州": "5200",
        "云南": "5300",
        "西藏": "5400",
        "陕西": "6100",
        "甘肃": "6200",
        "青海": "6300",
        "宁夏": "6400",
        "新疆": "6500"
    }


class ErrorCodeEnum(Enum):
    COMMON_ERROR_CODE_MAPPING = {
        102: '基本参数校验错误',
        105: '扫脸认证未成功, 返回二维码',
        506: '业务操作错误'
    }

    KP_ERROR_CODE_MAPPING = {
        
    }