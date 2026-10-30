# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot_visual.web_service import rest_request
from xbot import print, sleep
from .import package
from .package import variables as glv
import re
import json
import random

from . import utils
from .utils import find_any_one_by_xpath, wait_responses, get_processName_and_exePath, to_page, get_domain

from . import _amazon_api
from .utils import print

class VoiceCustomerHandler:
    """
    买家之声页面数据抓取
    url: /voice-of-the-customer/ref_=xx_voc_dnav_xx
    """    

    def __init__(self, web_page):
        self.web_page = web_page


    # def to_voice_customer_page(self):
    #     url = '/voice-of-the-customer'
    #     utils.to_page(self.web_page, url, self.XPaths.page_href, self.XPaths.search_in)


    def stop_monitor(self):
        try:
            self.web_page.stop_monitor_network()
        except:
            pass  


    def get_pcrListings(self):
        web_page = self.web_page
        page_offset = 0
        page_size = 20

        domain = utils.get_domain(web_page)
        url = "{}/pcrHealth/pcrListingSummary?searchText=&pageSize={}&pageOffset={}&sortColumn=ORDERS_COUNT&sortDirection=DESCENDING&insufficientFeedback=false".format(domain, page_size, "{}")

        tag = True
        pcrListings: list = []
        total = 0
        while tag or len(pcrListings) < total:
            tmp_url = url.format(page_offset)
            http_response = rest_request(url=tmp_url, method="GET", headers="", body=None, save_to_file=False, save_folder=None, save_filename=None, connect_timeout_seconds="30", send_by_web=True, browser=web_page)
            if http_response.status_code != 200:
                return []
            content = http_response.content
            content = json.loads(content)
            print(content)
            assert content.get("totalListingsCount", False) is not False and content.get("pcrListings", False) is not False, "请求 pcrListings 数据失败"
            total: int = content.get("totalListingsCount")
            tmp_pcrListings: list = content.get("pcrListings")
            pcrListings += tmp_pcrListings
            sleep(1)
            tag = False
            page_offset += page_size
        print("total ->", total)
        print(pcrListings)
        print("pcrListings len ->", len(pcrListings))
        return pcrListings


    def get_data_by_pcrListings(self, pcrListings, ret_type, asin_list):
        web_page = self.web_page
    
        asin_data = []


        domain = utils.get_domain(web_page)

        # 将asin提取出来当key，方便取值        
        pcrListing_dict = {}
        for pcrListing in pcrListings:
            asin = pcrListing["asin"]
            pcrListing_dict.setdefault(asin, [])
            pcrListing_dict[asin].append(pcrListing)

        # 抓取到的 asins
        asins = pcrListing_dict.keys()
        not_exist_asin_list = [asin for asin in asin_list if asin not in asins]
        # 如果传入的 asin_list 为空值，则是直接抓取所有asin信息
        asin_list = asin_list if bool(asin_list) else asins
        for asin in asin_list:
            if asin not in asins:
                continue

            for pcrListing in pcrListing_dict[asin]:
                for retry_time in range(2):
                    try:
                        tmp_data = []

                        # mskus 和 fnsku 访问的链接有点区别
                        sku = pcrListing['mskus'] if pcrListing['fnsku'] is None else  pcrListing['fnsku']
                        _type = "MSKU"  if pcrListing['fnsku'] is None else "FNSKU"

                        sleep(random.uniform(1, 2))
                        print("sku", sku, "retry", retry_time)


                        # 进入商品页，监听买家反馈信息
                        sku_url = '{}/voice-of-the-customer/details?value={}&type={}'.format(domain, sku, _type)
                        mode, _ = utils.get_processName_and_exePath(web_page)
                        
                        utils.start_monitor_network(web_page)
                        web_page.navigate(sku_url, load_timeout=0)

                        # 获取买家反馈信息
                        feedback_url = "*/feedback/?*"
                        responses = utils.wait_responses(web_page, url=feedback_url, timeout=30)
                        print(1)
                        print(responses)
                        assert bool(responses), "进入商品详情页失败，网络延迟，未等到数据出现"

                        body = responses[0]['body']

                        assert bool(body), "获取商品详情请求，响应数据为空"

                        body = json.loads(body)

                        returnComments = body['returnComments']

                        if len(returnComments) == 0:
                            returnComments = [{"orderId": None, "timestamp": None, "comment": None, }]


                        # 解析数据
                        commonReturn = pcrListing['mostCommonReturnReasonBucket']
                        if commonReturn is None:
                            commonReturn = ""
                        else:
                            commonReturn = "{} - {}%".format(commonReturn[3:], pcrListing['mostCommonReturnReasonBucketPercent'])

                        for comment in returnComments:
                            item = {
                                "asin": asin,
                                "sku": sku,
                                "买家不满意率": "{:.2f}%".format(pcrListing['ncxRate'] * 100),
                                "买家不满意订单": pcrListing['ncxCount'],
                                "订单总数": pcrListing['orderCount'],
                                "造成负面买家体验的主要原因": commonReturn,
                                "买家满意度状况": pcrListing['pcxHealth'],
                                "订单编号": comment['orderId'],
                                "批准退货日期": comment['timestamp'],
                                "买家留言": comment['comment']
                            }
                            
                            if int(ret_type):
                                item = list(item.values())
                            tmp_data.append(item)
                        print(tmp_data)
                        asin_data += tmp_data
                        break
                    except Exception as e:
                        print("err ->", e)
                        if retry_time >= 2:
                            raise ValueError(str(e))
                    finally:
                        self.stop_monitor()
        

        return asin_data, not_exist_asin_list

    @utils.retry_processing(retry_time=0, err_output_args=[[], []])
    def run(self, site_name, asin_list, ret_type=0):
        print(21)
        # 切换站点
        _amazon_api.switch_site(self.web_page, site_name)
        # 获取数据
        pcrListings = self.get_pcrListings()
        # 获取详细数据
        asin_data, not_exist_asin_list = self.get_data_by_pcrListings(pcrListings, ret_type, asin_list)
        return asin_data, not_exist_asin_list

        
        
def main(args):

    content = {'pcrListings': [], 'totalListingsCount': 0}

    res = content.get("totalListingsCount", False) is not False and content.get("pcrListings", False) is not False
    print(content.get("totalListingsCount", False) is not False)
    print(res)

    pass
