
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

import json
import re

from . import utils
from .utils import print, retry_processing
from . import _amazon_api

class CouponsHandler:
    """
    优惠券操作
    网址：/sellercoupons
    """

    fields = ["title", "status", "startDate", "endDate", "budget", "discount", "budgetUtilization", "clips", "redemptions", "sales"]
    displayFields = ["优惠券名称", "状态", "开始日期", "结束日期", "预算", "折扣","预算使用率", "领取", "已兑换", "Sales"]
    statusMessagesMap = {"Canceled":"已取消","Submitted":"已提交","Canceling":"已提交以便取消","Running":"有效","Expired":"已过期","Failed":"失败"}

    fields_map = dict(zip(fields, displayFields))

    def __init__(self, web_page):
        self.web_page = web_page
      

    def get_coupons(self):
        """抓取数据"""
        domain = 'https://sellercentral.amazon.com'
        web_page: xbot.web.WebBrowser = self.web_page

        domain = utils.get_domain(web_page)
        # https://sellercentral.amazon.com/coupons/ref=xx_scoupn_favb_xx
        
        coupons_url = "{}/coupons".format(domain)
        monitor_coupons_url = "{}/coupons/api/getCouponPromotions*".format(domain)

        web_page.navigate(coupons_url, load_timeout=0)
        web_page.wait_load_completed(timeout=50)
        # if web_page.get_url() != monitor_coupons_url:
        #     return False, "没有开启优惠券", []

        web_page.start_monitor_network(url=monitor_coupons_url, use_wildcard=True, resource_type="XHR")
        web_page.reload()

        while True:
            web_page.find("pagination-next").click()
            if "end" in web_page.find("pagination-next").get_attribute("class"):
                break
        
        responses = web_page.get_responses()
        web_page.stop_monitor_network()

        assert bool(responses), "加载优惠券失败，可能原因 - 1.网络延迟，2.没用优惠券数据"
        # xbot.logging.info(responses)
        return responses


    def clean_data(self, responses, has_header) -> None:
        data = []
        for response in responses:
            body = response['body']
            # print("body", body)
            if body == "":
                continue
            coupons = json.loads(body).get("promotionSearchResultList")    
            for coupon in coupons:
                # print(json.dumps(coupon))
                title = coupon.get("title")          
                status = coupon.get('status')          
                startDate = coupon.get("startDate")          
                endDate = coupon.get('endDate')          
                budget = coupon.get('budget')          
                discountValue = coupon.get('discountValue', 0)  / 100        
                budgetUtilization = coupon.get('couponMetrics').get('budgetUtilization')
                clipCount = coupon.get('couponMetrics').get('clipCount')  
                redemptionCount = coupon.get('couponMetrics').get('redemptionCount')       
                sales = coupon.get('couponMetrics').get('sales')       
                 
            tmp = [title, status, startDate, endDate, budget, discountValue, budgetUtilization, clipCount, redemptionCount, sales]
            data.append(tmp)

            if has_header:
                coupons.insert(0, self.displayFields)
        return data
    # @utils.retry_processing(retry_time=3, err_output_args=[[]])
    def run(self, site_name, has_header=False):
        """入口函数"""
        # 切换站点
        _amazon_api.switch_site(self.web_page, site_name)
        # 抓取数据
        responses = self.get_coupons()
        # 清洗数据
        coupons = self.clean_data(responses, has_header)

        header_fields = self.displayFields
        return header_fields, coupons
        


def main(args):
    web_page = xbot.web.get_active(mode="superbrowser")
    res = CouponsHandler(web_page).run("")
    print(res)
    pass
