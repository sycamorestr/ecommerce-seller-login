# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import http.client
import json
import xbot
from urllib.parse import urlparse
from xbot._core import robot
from  xbot.selector import Selector

def gen_selector(xpath_expression):
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [xpath_expression]}}
    selector = Selector(data)
    return selector

def check_enterprise():
    """校验企业版权益"""
    common_info: dict = robot.execute(f"Common.CommonConfig", {})

    token = common_info.get("token")
    web_api = common_info.get("webApi")
    is_publish_client = common_info.get("isPublicClient")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.hostname

    # 公有云客户端
    if is_publish_client:
        host = "api.yingdao.com"
        is_ssl = True

    timeout = 3
    host_str = host.decode() if isinstance(host, bytes) else str(host)
    if is_ssl:
        conn = http.client.HTTPSConnection(host_str, timeout=timeout)
    else:
        conn = http.client.HTTPConnection(host_str, timeout=timeout)

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "origin": "https://console.yingdao.com",
    }
    try:
        conn.request("GET", "/api/rpa/user/v1/info", headers=headers)
        res = conn.getresponse()
        if res.status != 200:
            raise Exception(f"HTTP error: {res.status} {res.reason}")
        data = res.read()
        data_json = json.loads(data)
        
        # 调用接口失败
        if not data_json.get("success"):
            raise
        
        return data_json.get("data").get("rpaUserGrade") == "enterprise"

    except Exception as e:
        xbot.logging.warning("该指令为企业版专享指令，非企业用户可限时体验，后续将仅对企业版用户开放。")
