import xbot
import xbot_visual
from xbot import print, sleep
from . import package
from .package import variables as glv

from xbot_visual.web.browser import start_monitor_network, stop_monitor_network
from xbot_visual.web_service import rest_request

from . import utils
from .utils import retry_processing
from .utils_beta import find_by_xpath

import json
import random
import re


class DealHandler:

    fields = ["marketplaceId", "title", "campaignStatus", "internalDescription", "type", "startDate", "endDate", "fees", "sales", "unitsSold", "committedQuantity", "glanceViews"]
    displayFields = ["亚马逊商城", "促销名称", "状态", "内部描述", "促销类型", "开始日期","结束日期", "促销费用", "销售额", "商品已售出", "已确定参与", "浏览量"]
    fields_map = dict(zip(fields, displayFields))
    
    campaignStatusMap = {"RUNNING": "正在进行", "UPCOMING": "即将推出", "NEEDS ATTENTION": "需要注意", "ENDED": "已结束", "CANCELLED": "已取消", "DRAFT": "未定"}

    marketplaceId = ["APJ6JRA9NG5V4","A13V1IB3VIYZZH","A1RKKUPIHCS9HS","A1C3SOZRARQ6R3","A1805IZSGTT6HS","A2NODRKZP88ZB9","A1PA6795UKMFR9","A1F83G8C2ARO7P"]
    marketplaceName = ["意大利",  "法国",  "西班牙",  "波兰",  "荷兰",  "瑞典",  "德国",  "英国" ]

    marketplaceMap = dict(zip(marketplaceId, marketplaceName))


    class XPaths:
        create_new_deal = '''(//kat-button[contains(@class, "create")])[1]'''   # 创建新促销按钮
        status_none = '''(//*[@class="smui-dropdown-status-none"]/a)[1]'''  # 活动状态无按钮
        yy = '''(//ul/kat-button)[1]''' # 活动状态确认按钮
        page_size = '''.//kat-option[@part="dropdown-option2"]'''  # 每页50
        page_url = '''//*[@data-menu-id="lightning-deals"]'''
        pageNumber = '''//input[@name="pageNumber" and not(@max=0)]'''  # 页码元素
        go_btn = '''//form[@name="pageNumber"]/kat-button'''    # 翻页按钮


    class Sel:
        deal_每页结果 = 'deal-每页结果'

    def __init__(self, web_page):
        self.web_page = web_page


    def to_deal_page(self) -> None:
        url = '/merchandising-new'
        domain: str = utils.get_domain(self.web_page)
        self.web_page.navigate(domain + url, load_timeout=100)

        
    def request_by_web(self, url, method="GET"):
        """
        通过网页发送请求
        """
        kwargs = {
            "url": url,
            "method": method,
            "headers": "",
            "body": None,
            "save_to_file": False,
            "save_folder": None,
            "save_filename": None,
            "connect_timeout_seconds": "30",
            "send_by_web": True,
            "browser": self.web_page
        }
        response = rest_request(**kwargs)
        assert response.status_code == 200, response.content
        return response.content


    def set_params(self, campaignStatusFilter, country="", date_range="") -> None:
        """修改筛选项为所有"""
        sleep(3)    # 不等待可能会有元素异常
        utils.start_monitor_network(self.web_page)
          

        find_by_xpath(self.web_page, self.XPaths.status_none).click(simulative=False)
        find_by_xpath(self.web_page, self.XPaths.yy).click(simulative=False, delay_after=2)

        self.web_page.find_by_xpath('//span[contains(text(), "状态")]').click() 
        self.web_page.find_by_xpath('//*[@label="未定"]/../..//*[text()="无"]' ).click() 

        # 支持多个条件
        if campaignStatusFilter:
            for filter_item in campaignStatusFilter.strip().split(","):
                if not filter_item:
                    continue
                self.web_page.find_by_xpath(f'//kat-checkbox[@label="{filter_item.strip()}"]').click()  
                 
        self.web_page.find_by_xpath('//*[@label="未定"]/../../kat-button[@label="应用"]' ).click()

        # 设置国家
        if country:
            # 触发下拉框
            country_dropdown_xpath = '//*[contains(text(), "Amazon Stores")]'
            self.web_page.find_by_xpath(country_dropdown_xpath, timeout=2).click()

            # 点击全选, 再次点击取消全选
            country_all_button = '//*[@label="所有"]'
            self.web_page.find_by_xpath(country_all_button, timeout=2).click()

            # 遍历所有的国家判断是否相等, 然后点击
            country_option_xpath = '//*[@class="smui-dropdown-list-option"]'
            country = [item.strip() for item in country.split(",")]

            for item in self.web_page.find_all_by_xpath(country_option_xpath, timeout=2):
                if item.get_text() in country:
                    item.click()

            # 点击
            apply_xpath = '//*[contains(text(), "Amazon Stores")]/../..//*[@label="应用"]'
            self.web_page.find_by_xpath(apply_xpath).click()

        if date_range:
            start_date, end_date = date_range.split("~")

            # 触发日期选择下拉框
            date_trigger_xpath = '//*[@id="search-and-filters"]//*[contains(text(), "日期")]'
            self.web_page.find_by_xpath(date_trigger_xpath, timeout=2).click()

            
            # 选择开始日期
            start_date_trigger_xpath = '//kat-date-picker[@name="afterStartDate"]'
            self.web_page.find_by_xpath(start_date_trigger_xpath, timeout=2).click()



            # 选择结束日期
            end_date_trigger_xpath = '//kat-date-picker[@name="beforeStartDate"]'
            self.web_page.find_by_xpath(end_date_trigger_xpath, timeout=2).click()


            # 选择应用
            apply_xpath = '//*[@label="应用"]'
            self.web_page.find_by_xpath(apply_xpath, timeout=2).click()




        # # 等待响应
        monitor_url = "*/merchandising/api/v4/manage/data?pageNumber=1&pageSize*"     
        utils.wait_responses(self.web_page, monitor_url, resource_type="All")


    def get_data(self) -> list:
        """抓取数据"""
        pageNumber_ele = find_by_xpath(self.web_page, self.XPaths.pageNumber)
        max_page_num = int(pageNumber_ele.get_attribute("max"))
        print("max_page_num ..", max_page_num)
        
        utils.start_monitor_network(self.web_page)
        for page_num in range(1, max_page_num + 1):
            # if page_num != 1:
                # 翻页操作
            find_by_xpath(self.web_page, self.XPaths.pageNumber).set_attribute('value', page_num)
            find_by_xpath(self.web_page, self.XPaths.go_btn).click(simulative=False)

            # 等待响应
            page_url = "*/merchandising/api/v4/manage/data?pageNumber={}&pageSize={}&*".format(page_num, 15)
            utils.wait_responses(self.web_page, page_url, resource_type="All")

            sleep(1)

        monitor_url = "*/merchandising/api/v4/manage/data*"
        
        # 这里获取的是所有页数的响应数据
        responses = utils.wait_responses(self.web_page, monitor_url, resource_type='All')
        self.web_page.stop_monitor_network()
        assert bool(responses), "未监听到响应数据"
        return responses  
    

    def clear_data(self, responses, campaignStatusFilter) -> list:
        """数据清洗"""
        campaigns = []
        for response in responses:
            body = response['body']
            if not bool(body):
                print("响应数据为空 ...", response['url'])
                continue
            json_data = json.loads(body)
            page_campaigns = json_data['viewModel']['searchCampaignsQueryResult']['searchCampaigns']
            for campaign in page_campaigns:

                # 过滤状态
                campaignStatus = campaign['campaignStatus']
                campaignStatus = self.campaignStatusMap.get(campaignStatus, campaignStatus)
                
                if bool(campaignStatusFilter) and campaignStatus not in campaignStatusFilter:
                    continue

                tmp = {}
                for k, v in self.fields_map.items():
                    if k == "startDate" or k == "endDate":
                        timestamp = campaign[k]
                        if timestamp is None:
                            tmp[v] = None
                        else:    
                            _, time_text = xbot_visual.datetime.from_timestamp(timestamp=timestamp, timestamp_level="second", output_text=True)
                            tmp[v] = time_text
                    elif v == "促销费用":
                        res = re.search(r"(?<=chargedFee=Currency\(amount=)[\d.+]+", f"{campaign[k]}")
                        amount = float(res.group()) if res else 0                        
                        tmp[v] = amount
                    elif v == "状态":
                        tmp[v] = self.campaignStatusMap.get(campaign[k], campaign[k])

                    elif k == "marketplaceId":
                        tmp[v] = self.marketplaceMap.get(campaign[k], campaign[k])
                    else:
                        tmp[v] = campaign[k]
                

                unitsSold = campaign['unitsSold']
                glanceViews = campaign['glanceViews']
                sales = campaign['sales']

                # 计算 转化率 unitsSold / glanceViews
                if glanceViews is None or glanceViews == 0:
                    tmp['转化率'] = None
                else:
                    tmp['转化率'] = "{:.1f}%".format(unitsSold / glanceViews * 100)

                # 计算 费用/销售额  fees / sales
                if sales is None or sales == 0:
                    tmp['费用/销售额'] = None
                else:
                    tmp['费用/销售额'] = "{:.1f}%".format(amount / sales * 100)

                
                campaigns.append(list(tmp.values()))

        return campaigns
    
    @retry_processing(retry_time=2, err_output_args=[[], []])
    def run(self, campaignStatusFilter, country="") -> list:
        """入口函数"""

        header_fields = self.displayFields + ['转化率', '费用/销售额']

        # 进入指定页面
        self.to_deal_page()

        if self.web_page.get_url().endswith("/merchandising-new/landing"):
            return header_fields, []

        # 修改参数
        self.set_params(campaignStatusFilter, country)
        # 抓取数据
        responses = self.get_data()
        print(responses)
        # 数据清洗
        campaigns = self.clear_data(responses, campaignStatusFilter)
        
        return header_fields, campaigns


def main(args):
    web_page = xbot.web.get_active(mode='superbrowser')
    h = DealHandler(web_page)
    res = h.run(None)
    print(res)
    pass
