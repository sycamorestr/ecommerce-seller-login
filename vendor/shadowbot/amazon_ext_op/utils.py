# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
from xbot import print, sleep
from xbot.web import WebBrowser, WebElement

from .import package
from .package import variables as glv

import time
import traceback
import os
from os.path import join
import json
import re
import xml.etree.ElementTree as ET 
from urllib.parse import urlparse
from ._amazon_core_beta import login


from .download_utils import download_handler
from typing import Union


print = [lambda *_, **__: None, print][__package__ == "xbot_robot" or hasattr(xbot, "__log")]



def handler_container(web_page):
    """通过js消除弹窗"""
    AD_XPATH = '//div[@id="hmd2f-container"]'
    ads = web_page.find_all_by_xpath(AD_XPATH, timeout=3)
    if len(ads) > 0:
        dis = """
        function hideAds(context, args) {
            document.querySelectorAll('[id="hmd2f-container"]')
                    .forEach(el => el.style.display = args);
        }
        """
        web_page.execute_javascript(dis, "none")
    sleep(0.5)

def handler_feedback(web_page):
    """通过js消除feedback"""
    dis = """
        function hideAds(context, args) {
            document.querySelectorAll('[id="hmd2f-trigger-tab"]')
                    .forEach(el => el.style.display = args);
        }
        """
    web_page.execute_javascript(dis, "none")
    sleep(0.5)

def select_click(keyword, keyword_list, elem_list):
    """
    映射出一个位置关系进行选择
    :param keyword: 客户填写的文本内容
    :param keyword_list: 自定义的列表
    :param elem_list: 网页相似元素组
    :return: 
    """
    
    mapping = {element: index for index, element in enumerate(keyword_list)}
    elem_list[mapping[keyword]].click()

def request_error(web_page):
    """判断是否请求下载失败"""
    request_error_xpath = '//p[@class="request-report-error"]'
    request_error = web_page.find_all_by_xpath(request_error_xpath,timeout=5)
    if len(request_error) > 0:
        return True
    else:
        return False


def get_domain_from_url(url):
    # 获取域名
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc  # 例如：www.example.com
    except Exception as e:
        return None   

def retry_processing(retry_time: int=2, err_output_args: list=[], name: str=""):
    """
    重试处理
    :param retry_time: 运行失败重试的次数
    :param err_output_args: 运行失败返回的参数列表，会拼接上 运行状态 和 异常信息 一起返回
    :return: 
    """
    name = name if bool(name) else "亚马逊卖家后台扩展操作"
    def outer(func):
        def wrapper(*args, **kwargs):
            err_msg = None
            for _retry_time in range(retry_time + 1):
                try:
                    _res = func(*args, **kwargs)
                    res = (True, "", *_res) if len(err_output_args) > 1 else (True, "", _res)
                    return res
                except ValueError as value_e:
                    err_msg = str(value_e)
                    break
                except Exception as e:
                    if _retry_time >= retry_time:
                        err_msg = traceback.format_exc()
                        print("【{}】指令日志 - 第{}次操作失败，不再重试. 异常信息如下：".format(name, _retry_time + 1))
                        print(err_msg)
                    else:
                        print("【{}】指令日志 - 第{}次操作失败，即将重试...".format(name, _retry_time + 1))
                        print(traceback.format_exc())
                        sleep(1)
            
            res = (False, err_msg, *err_output_args)
            return res
        return wrapper
    return outer


def start_monitor_network(web_page):
    """网页监听，先停止监听再开始，停止监听可以清空之前监听到的结果"""
    
    web_page.start_monitor_network(url="*", use_wildcard=True)
    web_page.stop_monitor_network()
    sleep(1)
    web_page.start_monitor_network(url="*", use_wildcard=True)


def find_by_parent(web_page, selector, parent, timeout=10):
    """使用元素选择器，关联父元素查找元素"""
    if isinstance(selector, str):
        selector = package.selector(selector)
    web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=selector, css_selector="", xpath_selector="", is_related_parent=True, parent=parent, timeout=timeout)
    return web_element


def download_file(web_page, selector_or_element, save_dir, save_name, wait_time):
    """下载文件"""

    product_name = web_page.product_name
    if isinstance(selector_or_element, xbot.selector.Selector):
        download_ele = web_page.find(selector_or_element)
    if isinstance(selector_or_element, str):
        download_ele = web_page.find_by_xpath(selector_or_element)
    else:
        download_ele = selector_or_element

    download_file_path = download_handler(web_page, download_ele, save_dir, file_name=save_name)
    assert xbot_visual.file.wait(path=download_file_path, desired_state="created", is_wait=True, timeout_seconds=wait_time), "长时间等待文件下载失败"

    return download_file_path


# def find_by_xpath(func):
#     """通过xpath查找网页元素，异常信息中提示XPath，方便排查"""
#     def w(xpath_selector, * ,timeout=20):
#         err_msg = None
#         try:
#             res = func(xpath_selector, timeout=timeout)
#             return res
#         except Exception as err:
#             err_msg = str(err)
#             pass
#         raise Exception("XPath - {}，{}".format(xpath_selector, err_msg).replace("\n", ""))
#     return w



def find_any_one_by_xpath(web_page, xpath_map, timeout=10):
    """查找任意一个xpath，提高查找效率"""
    timeout = int(timeout)
    xpath = "|".join(xpath_map.values())
    print(xpath)
    err_msg = None
    try:
        web_page.find_all_by_xpath(xpath, timeout=timeout)
    except Exception as find_any_one_error:
        err_msg = f"{find_any_one_error}"
        
        
    if err_msg:
        print(err_msg)
        raise Exception(err_msg)

    for name, xpath in xpath_map.items():
        try:
            ele = web_page.find_by_xpath(xpath, timeout=0)
            return name, ele
        except Exception as e:
            if "未找到元素" in str(e):
                continue
            raise

    raise Exception(f"XPath - {xpath}，未找到元素")

# def wait_responses(web_page, url, use_wildcard=True, resource_type='XHR', timeout=100):
#     """等待网页监听的响应结果， """
#     start_time = time.time()
#     while True:
#         responses = web_page.get_responses(url=url, use_wildcard=use_wildcard, resource_type=resource_type)
#         if len(responses) != 0:
#             return responses
        
#         if time.time() - start_time >= timeout:
#             return None

def wait_responses(web_page, url, use_wildcard=True, resource_type='XHR|Fetch', timeout=100):
    """获取响应内容"""
    start = time.time()
    data = []
    while time.time() - start <= timeout:
        responses = web_page.get_responses(url=url, use_wildcard=use_wildcard, resource_type=resource_type)
        for response in responses:
            if not bool(response.get('body')): continue
            data.append(response)
            
        if len(data) != 0: return data
        sleep(1)
    return None

def get_processName_and_exePath(web_page):
    """获取浏览器进程和路径"""
    if not hasattr(web_page, "product_name"):
        return 'cef', None
    mode_map = {
        'Google Chrome': 'chrome',
        'Microsoft Edge': 'edge',
        'Internet Explorer': 'ie',
        'Firefox': 'firefox'
    }
    product_name = web_page.product_name

    process_name = mode_map.get(product_name, None)
    if process_name:
        return process_name, None

    try:
        config_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ShadowBot', 'ChromiumBrowser.config')
        
        if not os.path.exists(config_path):
            return None, None

        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()

        # 查找匹配的产品名称
        matching_nodes = root.findall(".//ChromiumBrowserInfo[ProductName='{}']".format(product_name))
        if len(matching_nodes) == 0:
            return None, None
        # 提取ProcessName和ExePath
        node = matching_nodes[0]
        return node.find('ProcessName').text, node.find('ExePath').text
    except Exception as e:
        print("get_processName_and_exePath_by_productName err...", e)
        return None, None


def get_domain(web_page: WebBrowser):
    """获取domain"""
    url = web_page.get_url()
    
    res = re.search("https?://sellercentral.+?amazon.+?(?=/)", url)
    if not res:
        raise Exception("请先进入亚马逊商家后台")
    domain = res.group()
    return domain

def get_ad_domain(web_page: WebBrowser):
    url = web_page.get_url() 
    
    res = re.search(r"https?://(sellercentral|advertising).+?amazon.+?(?=/|$)", url)
    
    if not res:
        raise Exception("请先进入亚马逊[商家后台]或[广告活动管理页面]")
    
    domain = res.group()

    # 如果已经在广告台，直接返回
    if "advertising" in domain:
        return domain
        
    # 如果在商家后台，进行关键词替换
    elif "sellercentral" in domain:
        ad_domain = domain.replace("sellercentral", "advertising", 1)
        return ad_domain
        
    return domain


def to_page(web_page, url, url_ele_xpath=None, suss_ele_xpath=None, is_to_home=True):
    """
    通过url进入指定页面
    :param web_page: 网页对象
    :param url: 目标页面url
    :param url_ele_xpath: 点击即可进入目标页面的元素，主要用于判断当前站点是否可以进入该页面
    :param suss_ele_xpath: 判断是否成功进入页面的元素
    :param is_to_home: 是否先进入首页
    :return: 
    """

    assert isinstance(web_page, xbot.web.WebBrowser)
    domain = get_domain(web_page)    
    url = "{}{}".format(domain, url)

    def to_home():
        """进入首页"""
        home_url = "{}/home".format(domain)
        # xpath = '//*[@id="sc-trim-site-map"]'   # 首页页脚元素
        # xpath = '//*[@id="KPI_CARD_PAYMENTS"]'   # 首页页脚元素
        xpath = '//*[@id="sc-footer-container"]'
        try:
            if not web_page.get_url().startswith(home_url):
                try:
                    web_page.navigate(home_url, load_timeout=0)
                except:
                    pass
                web_page.find_by_xpath(xpath, timeout=100)
                web_page.stop_load()
        except Exception as e:
            raise Exception("进入首页失败 - {}".format(e))

    err_msg = ""
    for _retry_time in range(3):
        try:
            if not web_page.get_url().startswith(url) or _retry_time != 0:
                # 第一次需要进入首页
                if is_to_home and _retry_time == 0 :
                    to_home()

                    try:
                        web_page.find_by_xpath(url_ele_xpath, timeout=2)
                    except Exception as e:
                        err_msg = "当前站点无法打开该页面 - {}".format(e)
                        try:
                            web_page.find_by_xpath('//*[@id="go-to-credit-card-info"]', timeout=2)
                            err_msg = "当前站点支付方式无效 - {}".format(e)
                        except Exception as e:
                            pass
                        break
                try:
                    web_page.navigate(url, load_timeout=200)
                    login(web_page)
                    sleep(2)
                except:
                    pass
            if 'failed' in web_page.get_url():
                raise Exception('页面不可用')
            web_page.find_by_xpath(suss_ele_xpath, timeout=200)
            return
        except Exception as e:
            if _retry_time == 2:
                err_msg = str(e)
                break
    
    # 处理一下异常信息再抛出，否则会被影刀截断
    raise Exception(err_msg.replace("\n", " "))


def main(args):
    web_page = xbot.web.get_active(mode="superbrowser")
    # find_by_xpath(web_page, '//*[@id="publisher:create-post:caption-input"]')
    pass
