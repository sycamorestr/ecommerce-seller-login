# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import hashlib
import time
import json

import requests 

import xbot
# from xbot import print, sleep
from .import package
from .package import variables as glv
from .api_enum import *


class TaxInvoiceAPI: 
    def __init__(self):
        """
        初始化 TaxInvoiceAPI 类。
        
        :param base_url: API的基础URL。
        """
        self.base_url = APIBaseUrl.BASE_URL.value
        self.cache = {}
        self.token = None
        self.tax_login_status = False


    def _get_cached_param(self, param_name: str, input_value=''):
        """
        获取缓存中的参数值，如果没有缓存则使用输入的值。
        
        :param param_name: 参数名称。
        :param input_value: 用户输入的值。
        :return: 返回参数值。
        :raises ValueError: 如果参数既没有缓存也没有用户输入。
        """
        if input_value is not None and input_value:
            self.cache[param_name] = input_value
            return input_value
        elif param_name in self.cache:
            return self.cache[param_name]
        else:
            raise ValueError(f"参数 '{param_name}' 未提供且未在缓存中找到。")


    def set_token(self, app_id: str, secret: str):
        self.token = self.get_token(app_id, secret)
        return (self.token is not None)


    def _post_request(self, endpoint: str, payload: dict):
        """
        发送POST请求的通用方法。
        
        :param endpoint: API端点。
        :param payload: 请求负载。
        :return: 返回响应的JSON数据。
        """
        timestamp = int(time.time())
        params = {
            'appid': self._get_cached_param('app_id'),
            'format': 'json',
            'timestamp': timestamp,
            'token': self.token,
            'version': '1.0',
            'sign': get_sign(self._get_cached_param('app_id'), self.token, payload, timestamp)
        }

        url = f"{self.base_url}{endpoint.value}"
        headers = {'Content-Type': 'application/json'}  
        for _i in range(APIConfig.RETRIES_TIMES.value):
            try:
                response = requests.post(url, json=payload, headers=headers, params=params, timeout=APIConfig.MAX_TIME_OUT.value)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_err:
                if _i != APIConfig.RETRIES_TIMES.value - 1: 
                    sleep(3)
                    continue
                print(f'{_i} -> HTTP error occurred: {http_err}')  # 处理 HTTP 错误

            except Exception as err:
                if _i != APIConfig.RETRIES_TIMES.value - 1: 
                    sleep(3)
                    continue
                print(f'{_i} -> Other error occurred: {err}')     # 处理其他错误
        
        raise Exception(f'Post endpoint err-> {endpoint}')


    def _get_request(self, endpoint: str, payload: dict):
        """
        发送GET请求的通用方法。
        
        :param endpoint: API端点。
        :param payload: 请求负载。
        :return: 返回响应的JSON数据。
        """
        url = f"{self.base_url}{endpoint.value}"
        headers = {'Content-Type': 'application/json'}
        for _i in range(APIConfig.RETRIES_TIMES.value):
            try:
                response = requests.get(url, params=payload, headers=headers, timeout=APIConfig.MAX_TIME_OUT.value)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as http_err:
                if _i != APIConfig.RETRIES_TIMES.value - 1: 
                    sleep(3)
                    continue
                print(f'HTTP error occurred: {http_err}')  # 处理 HTTP 错误

            except Exception as err:
                if _i != APIConfig.RETRIES_TIMES.value - 1: 
                    sleep(3)
                    continue
                print(f'Other error occurred: {err}')     # 处理其他错误

        raise Exception(f'Get endpoint err-> {endpoint}')


    def tax_login(self, nsrsbh='', username='', password='', reqid='', zrrlx='', dqbm='', sms_code='', reloginflag=''):
        """
        企业账户登录接口。
        
        :param nsrsbh: 纳税人识别号。
        :param username: 用户名。
        :param password: 密码。
        :param reqid: 请求ID。
        :param zrrlx: （可选）责任人类型。
        :param dqbm: （可选）地区编码。
        :param sms_code: （可选）短信验证码。
        :param reloginflag: （可选）重新登录标志。
        :return: 返回登录响应的JSON数据。
        """
        payload = {
            "reqid": reqid,
            "nsrsbh": self._get_cached_param('nsrsbh', nsrsbh),
            "username": self._get_cached_param('username', username),
            "password": self._get_cached_param('password', password),
            "zrrlx": zrrlx,
            "dqbm": dqbm,
            "sms_code": sms_code,
            "reloginflag": reloginflag
        }
        response = self._post_request(APIEndpointEnum.TAX_LOGIN, payload)
        # print(response)
        r_response = xhei_response_wash(response)
        if r_response.get('status'):
            self.tax_login_status = True
        return r_response


    def ensure_login(self):
        """
        确保用户已登录，如果未登录则提示登录。
        """
        if not self.tax_login_status:
            raise Exception("请先登录。")
    
    def logout(self):        
        """
        退出登录。
        """
        self.tax_login_status = False


    def get_qr_code(self, reqid='', code_type=''):
        """
        获取二维码接口。
        
        :param reqid: 请求ID。
        :param nsrsbh: 纳税人识别号。
        :param username: 用户名。
        :param type: （可选）二维码类型。
        :return: 返回二维码响应的JSON数据。
        """
        self.ensure_login()
        payload = {
            "reqid": reqid,
            "nsrsbh": self._get_cached_param('nsrsbh'),
            "username": self._get_cached_param('username'),
            "type": APIMappingEnum.QR_CODE_TYPE_MAPPING.value[self._get_cached_param('qrcode_type', code_type)],
        }

        response = self._post_request(APIEndpointEnum.GET_QR_CODE, payload)

        r_response = xhei_response_wash(response)
        if not r_response.get('status'):
            return r_response
        r_response['msg'] = response['response']['ewm']
        self.cache['rzid'] = response['response']['rzid']
        return r_response


    def query_secondary_auth_status(self, reqid=''):
        """
        二次认证状态查询接口。
        
        :param reqid: 请求ID。
        :param nsrsbh: 纳税人识别号。
        :param username: 用户名。
        :param rzid: 认证ID。
        :param type: （可选）认证类型。
        :return: 返回二次认证状态响应的JSON数据。
        """
        self.ensure_login()
        payload = {
            "reqid": reqid,
            "nsrsbh": self._get_cached_param('nsrsbh'),
            "username": self._get_cached_param('username'),
            "rzid": self._get_cached_param('rzid'),
            "type": self._get_cached_param('qrcode_type'),
        }
        response = self._post_request(APIEndpointEnum.QUERY_SECONDARY_AUTH_STATUS, payload)
        r_response = xhei_response_wash(response)
        if not r_response.get('status'):
            return r_response
        # self.cache['rzid'] = response['response']['rzid']
        r_response['msg'] = APIMappingEnum.QR_CODE_SLZT_MAPPING.value[str(response['response']['slzt'])]
        
        return r_response


    def issue_invoice(self, fpkjxx_fptxx: dict, fpkjxx_xmxxs: list):
        """
        直接发票开具接口。
        
        :param nsrsbh: 纳税人识别号。
        :param username: 用户名。
        :param fpkjxx_fptxx: 发票开具信息-发票头信息。
        :param fpkjxx_xmxxs: 发票开具信息-项目明细信息列表。
        :return: 返回发票开具响应的JSON数据。
        """
        self.ensure_login()
        payload = {
            "nsrsbh": self._get_cached_param('nsrsbh'),
            "username": self._get_cached_param('username'),
            "fpkjxx_fptxx": fpkjxx_fptxx,
            "fpkjxx_xmxxs": fpkjxx_xmxxs,
        }
        return self._post_request(APIEndpointEnum.ISSUE_INVOICE, payload)


    def query_order(self, fpqqlsh: str):
        """
        订单查询接口。
        
        :param reqid: 请求ID。
        :param nsrsbh: 纳税人识别号。
        :param username: 用户名。
        :param fpqqlsh: 发票请求流水号。
        :return: 返回订单查询响应的JSON数据。
        """
        self.ensure_login()
        payload = {
            "fpqqlsh": fpqqlsh,
        }
        return self._post_request(APIEndpointEnum.QUERY_ORDER, payload)


    def get_token(self, app_id: str, secret: str):
        """
        TOKEN获取接口。
        
        :param app_id: appid。
        :param secret: 密钥。
        :return: 返回接口的JSON数据。
        """
        payload = {
        'version': '1.0',
        'grant_type': 'password',
        'username': self._get_cached_param('app_id', app_id),
        'password': self._get_cached_param('secret', secret)
        }
        response = self._get_request(APIEndpointEnum.TOKEN, payload)
        # print(response)
        token = response.get('access_token', None)
        # print("token:",token)
        return token
        

def get_sign(appid: str, token: str, data: dict, timestamp: int):
    """
    sign 获取

    :param app_id: appid
    :param token: token
    :param data: 数据字典
    :param timestamp: 时间戳
    """
    data = json.dumps(data, ensure_ascii=False).replace(": ", ":").replace(', ', ',')
    sign = f'appid={appid}&format=json&timestamp={timestamp}&token={token}&version=1.0{data}'
    # print("加密前sign:",sign)
    sign = sha1_hash(md5_hash(sign)).upper()
    # print("加密后的sign",sign)
    return sign


def md5_hash(text: str):
    # 创建 MD5 对象
    md5 = hashlib.md5()
    # 更新对象的输入字符串
    md5.update(text.encode('utf-8'))
    # 返回 MD5 加密结果
    return md5.hexdigest()


def sha1_hash(text: str):
    # 创建 SHA-1 对象
    sha1 = hashlib.sha1()
    # 更新对象的输入字符串
    sha1.update(text.upper().encode('utf-8'))
    # 返回 SHA-1 加密结果
    return sha1.hexdigest()


def xhei_response_wash(response: requests.Response):
    if response['result'] == 's':
        return {'status': True, 'msg': response['response'].get('msg', '成功！')}

    elif response['result'] == 'f':
        return {'status': False, 'msg': response['response']['errinfo']}
