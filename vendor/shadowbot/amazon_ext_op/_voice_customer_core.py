# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能的功能
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
# --- 新增时间处理模块导入 ---
import datetime
from datetime import timedelta
# -------------------------

from . import utils
from .utils import find_any_one_by_xpath, wait_responses, get_processName_and_exePath, to_page, get_domain, handler_container

from . import _amazon_api
# from .utils import print
def calculate_updated_after(days: int) -> str:
    """
    根据天数计算 updatedAfter 参数所需的 UTC 时间戳（ISO 8601 格式）。
    如果 days=0 或 None，返回 None，表示不添加时间筛选参数（即“全部”）。
    
    格式示例：2025-10-05T07:12:02.474Z
    """
    if days is None or days <= 0:
        return None 
    
    # 确保使用 UTC 时间
    utc_now = datetime.datetime.utcnow()
    
    # 计算 N 天前的日期
    target_date = utc_now - timedelta(days=days)
    
    # 格式化为 ISO 8601 格式: YYYY-MM-DDTHH:MM:SS.mmmZ
    iso_string = target_date.strftime("%Y-%m-%dT%H:%M:%S")
    # 确保毫秒部分为三位，不足补零
    micro_seconds = str(target_date.microsecond)[:3].ljust(3, '0')
    
    return f"{iso_string}.{micro_seconds}Z"


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


    def get_pcrListings(self, time_days=0): # 接收天数参数，0 为全部
        web_page = self.web_page
        page_offset = 0
        page_size = 20  

        # --- 时间筛选逻辑：计算 updatedAfter 参数 ---
        updated_after = calculate_updated_after(time_days)
        time_param = ""
        if updated_after:
            # 如果 updated_after 有值（即 time_days > 0），则添加参数
            # rest_request 会自动处理 URL 编码
            time_param = f"&updatedAfter={updated_after}"
        # ------------------------------------------------

        domain = utils.get_domain(web_page)

        # 构造带有动态时间参数的 URL 模板
        url = "{}/pcrHealth/pcrListingSummary?searchText=&pageSize={}&pageOffset={}&sortColumn=ORDERS_COUNT&sortDirection=DESCENDING&insufficientFeedback=false{}".format(domain, page_size, "{}", time_param)

        tag = True
        pcrListings: list = []
        total = 0

        while tag or len(pcrListings) < total:
            tmp_url = url.format(page_offset)
            print("发送请求的完整URL:",tmp_url)
            
            # 使用动态构造的 tmp_url 发送请求
            http_response = rest_request(url=tmp_url, method="GET", headers="", body=None, save_to_file=False, save_folder=None, save_filename=None, connect_timeout_seconds="30", send_by_web=True, browser=web_page)
            
            if http_response.status_code != 200:
                return []
            content = http_response.content
            content = json.loads(content)
            # print('--------------------',content)
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
                        handler_container(web_page)

                        # 获取买家反馈信息
                        feedback_url = "*/feedback/?*"
                        responses = utils.wait_responses(web_page, url=feedback_url, timeout=30)

                        # print(responses)
                        assert bool(responses), "进入商品详情页失败，网络延迟，未等到数据出现"
                        
                        # print('相应数据',responses[0])
                        body = responses[0]['body']
                        assert bool(body), "获取商品详情请求，响应数据为空"

                        body = json.loads(body)

                        returnComments = body['returnComments']
                        productReviews = body['productReviews']
                        customerComplaintSummaries = body['customerComplaintSummaries']

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
                                "买家留言": comment['comment'],
                            }
                            
                            if int(ret_type):
                                item = list(item.values())
                            tmp_data.append(item)

                        # 将评论写进返回列表中
                        if productReviews:
                            productReviews = [tmp['body'] for tmp in productReviews]
                            productReviews.insert(0, '评论')
                            tmp_data.append(productReviews)
                            # print(tmp_data)
                        
                        # 将其他来源写进返回列表中
                        if customerComplaintSummaries:
                            for data in customerComplaintSummaries:
                                item = {
                                    '订单ID': data['orderId'],
                                    '其他来源': data['customerComplaintSummary']
                                }
                                item = list(item.values())
                                tmp_data.append(item)
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
    # 新增 time_days 参数，默认 0 为全部
    # time_days: 0=全部，7=7天，30=30天，90=90天，365=1年, 也可以自定义任意天数
    def run(self, site_name, asin_list, ret_type=0, time_days=0): 
        try:
            time_days = int(time_days)
        except (ValueError, TypeError):
            print(f"警告：time_days 参数 '{time_days}' 无法转换为整数，将使用默认值 0 (全部)。")
            time_days = 0
        # 切换站点
        _amazon_api.switch_site(self.web_page, site_name)
        # 获取数据，传入 time_days
        pcrListings = self.get_pcrListings(time_days=time_days)
        # 获取详细数据
        asin_data, not_exist_asin_list = self.get_data_by_pcrListings(pcrListings, ret_type, asin_list)
        return asin_data, not_exist_asin_list
        
        
def main(args):

    content = {'pcrListings': [], 'totalListingsCount': 0}

    res = content.get("totalListingsCount", False) is not False and content.get("pcrListings", False) is not False
    print(content.get("totalListingsCount", False) is not False)
    print(res)

    pass
