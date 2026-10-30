# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import json
import requests

from xbot import print, sleep, web
from .import package
from .package import variables as glv

def google_verify(token, googlekey, pageurl, invisible=1, data_s=""):
    _headers = {
        'Content-Type': 'application/json'
    }
    """
    第一步，创建验证码任务
    :param
    :return taskId : string 创建成功的任务ID
    """
    url = "http://122.9.52.147/api/YmServer/funnelApi"
    payload = json.dumps({
        "token": token,
        # "type": "40011", ## v3
        "type": "40010",  ## v2
        "googlekey": googlekey,
        "enterprise": 0,  ## 是否为企业版
        "pageurl": pageurl,
        "invisible": invisible,
        "data-s": data_s,
        # 'action':"TEMPLATE" #V3必传
    })
    # 发送JSON格式的数据
    result = requests.request("POST", url, headers=_headers, data=payload).json()
    print(result)
    # {'msg': '识别成功', 'code': 10000, 'data': {'code': 0, 'captchaId': '51436618130', 'recordId': '74892'}}
    captcha_id = result.get('data').get("captchaId")
    record_id = result.get('data').get("recordId")
    times = 0
    while times < 150:
        try:
            url = f"http://122.9.52.147/api/YmServer/funnelApiResult"
            data = {
                "token": token,
                "captchaId": captcha_id,
                "recordId": record_id
            }
            result = requests.post(url, headers=_headers, json=data).json()
            print(result)
            # {'msg': '结果准备中，请稍后再试', 'code': 10009, 'data': []}
            if result['msg'] == "结果准备中，请稍后再试":
                sleep(5)
                times += 5
                continue
            if result['msg'] == '请求成功' and result['code'] == 10001:
                print(result['data']['data'])
                return result['data']['data']
                # {'msg': '请求成功', 'code': 10001, 'data': {'data': '03AGdBq2611GTOgA2v9HUpMMEUE70p6dwOtYyHJQK4xhdKF0Y8ouSGsFZt647SpJvZ22qinYrm6MYBJGFQxMUIApFfSBN6WTGspk6DmFdQAoWxynObRGV7qNMQOjZ_m4w3_6iRu8SJ3vSUXH_HHuA7wXARJbKEpU4J4R921NfpKdahgeFD8rK1CFYAqLd5fz4l-8_VRmRE83dRSfkgyTN338evQ1doWKJRipZbk4ie-89Ud0KGdOsP4QzG3stRZgj2oaEoMDSAP62vxKGYqtDEqTcwtlgo-ot3rF5SmntaoKGwcKPo0NrekWA5gtj0vqKLU6lY2GcnSci_tgBzBwuH40uvyR1PFu02VK_E44mopJ7FOO4cUukNaLGqypU2YCA8QuaaebOIoCMU7RGqGs_41RYNCG1GSdthiwcwk2hHFbi-TXuICXSwh4Er5mgVW9A3t_9Ndp0eJcyr3HtuJrcA7BtlcgruuQxK5h4Ew4ert4KPH_aQGN9ww5VsUtbSManzUDnUOs7aEdvFk1DOOPmLys-aX20ZFN2CcQcZZSO-7HZpZZt3EDeWWE5S02HFDY8gl3_0xqIts8774Tr4GMVJaddG0NR6pcBFC11FqNcK2a18gM3gaKDy3_2ZMeSU4nj4NWwoAhPjQN2BS8JxX4kKVpX4rD959kc93vczVD3TYD6_4GJahGSpBvM7Y5_GGIdLL8imXde1R35mZnEcFYXQ40zcy3DdJFkk_gzGTVOEb1Q1IZpjMxzCxyGgwjgL9dtDIgst5H5CSZoerX_Lz-DmsBvYIYZdpbPLEMROx9MODImaEw8Cp6M8Xj7_foijiGE9hh-pzJSTlKl3HytiSUyJJ7r1BssrX5C_TFWxl0IXNg8azP8H-ZIOWwnYlMWCS1w9piHdoLg5zACiYIN3Txdlsvi61MuPmzJggJd1_dlyMdAlzb5_zdfweqj0_Ko1ODP378YT7sV7LECgRj5QJU6sF5nlf4m2g5sFypBw9GFAkEE-OaWGYxRJOy2ioU41ggAJIkcza2B_N5AL2KLROtm0-c2MxplM4ZzHxrUv9A24zlgzo3Pz4NONwU_gaOcDB7j1dZKXD8UaoIrZv0BTd8JeojYowm9Usdg7Rt4Fpo_vDLJdrEUfbxVlXieDD9Fr1fu72-d4AduT_J3n-rIhyX4gFav-KfP-qOxqOZsmjXZirsBxZs7042NYeirRYnLv35cxIAJARz03FJmeKViUivwC5mCWw64hjRad9XyyBOP2n8KFOrTXhPskC-WwEfksGtfLxi6VW76FHGvRdwHXzMwVfNqe3P5H_WZUc-vxeTAsTnqZz3WA97lM4MLrX0nTZYgXxCEiS6raSOiEMqcx_Nv7Zxre-abj4LZRbFpH8nx1SEiaOV2Dm-a1iPFEmCs0L4kDtt6VImSVIQaTOAd3KFSo7W_XTvRPsQJOtblrcKyuagztX_Yr0lT0YqN9I9MZAARo7M5OfwSLJW16rdmp4NuRefEvNPNHO2cVh1Xha1qNGuF_QDvWFFmWG0Y6IbRqLmF-Dv8BY4TWyOeVnADJftGQw2QSr8RmbCHryA'}}
        except Exception as e:
            print(e)
            continue

def main(args):

    

# pageurl "https://yescaptcha.com/auth/register"
# sitekey "6Lch4iAfAAAAAPoj7hHZMKvYaHlU2Koks63tZOWR"
# version "V2"

    page_url = "https://yescaptcha.com/auth/register"
    token = ""

    web_page = web.get_active(mode="chrome")
    google_v2_std_trigger_ele = web_page.find("google_v2_std_trigger_ele")
    google_key =google_v2_std_trigger_ele.get_attribute("data-sitekey")
    # google_v2_std_trigger_ele.click()
    google_verify(token,google_key, page_url)

    pass
