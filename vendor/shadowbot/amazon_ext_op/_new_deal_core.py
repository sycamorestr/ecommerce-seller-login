import xbot
import xbot_visual
from xbot import print, sleep
from . import package
from .package import variables as glv

from xbot_visual.web.browser import start_monitor_network, stop_monitor_network
from xbot_visual.web_service import rest_request



from . import utils
from .utils import print, retry_processing
import json
import random
import re


class NewDealHandler:

    fields = ["marketplaceId", "title", "campaignStatus", "internalDescription", "type", "startDate", "endDate", "fees", "sales", "unitsSold", "committedQuantity", "glanceViews"]
    displayFields = ["亚马逊商城", "促销名称", "状态", "内部描述", "促销类型", "开始日期","结束日期", "促销费用", "销售额", "商品已售出", "已确定参与", "浏览量"]
    fields_map = dict(zip(fields, displayFields))
    
    campaignStatusMap = {"RUNNING": "正在进行", "UPCOMING": "即将推出", "NEEDS ATTENTION": "需要注意", "ENDED": "已结束", "CANCELLED": "已取消", "DRAFT": "未定"}


    class XPaths:

        page_url = '''//*[@data-menu-id="lightning-deals"]'''
        create_new_deal = '''(//kat-button[contains(@class, "create")])[1]'''   # 创建新促销按钮




    class Sel:
        deal_每页结果 = 'deal-每页结果'

    def __init__(self, web_page: xbot.web.WebBrowser):
        self.web_page = web_page


    def to_deal_page(self) -> None:
        url = '/merchandising'
        utils.to_page(self.web_page, url, url_ele_xpath=self.XPaths.page_url, suss_ele_xpath=self.XPaths.status_none)



    def set_params(self) -> None:
        """修改筛选项为所有"""
        pass


    def get_data(self) -> list:
        """抓取数据"""
        pass
    

    def clear_data(self, responses: list, campaignStatusFilter: str) -> list:
        """数据清洗"""
        pass
    
    @retry_processing(retry_time=0, err_output_args=[[]])
    def run(self, campaignStatusFilter: str) -> list:
        """入口函数"""
        # 进入指定页面
        # self.to_deal_page()
        # 修改参数
        # self.set_params()
        # 抓取数据
        # responses = self.get_data()
        # 数据清洗
        # campaigns = self.clear_data(responses, campaignStatusFilter)
        # return campaigns
        pass


def main(args):
    web_page = xbot.web.get_active(mode='superbrowser')
    h = NewDealHandler(web_page)
    res = h.run()
    print(res)
    pass
