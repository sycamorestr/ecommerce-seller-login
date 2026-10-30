
# 此模块主要处理 【库存和销量报告】 页面下 【月度仓储费】报告下载操作
# 网址：/reportcentral/STORAGE_FEE_CHARGES/1
# 

import xbot
import xbot_visual
from xbot import print, sleep
from .import package
from .package import variables as glv

from xbot_visual import datetime

import re
from . import utils
from . import download_utils
from .utils import print,get_domain
from .utils import handler_container
from .activities_utils import download_handler
from .utils_beta import find_by_xpath
from . import _amazon_api

class MonthlyStorageFeesHandler:
    """月度仓储费"""

    class XPaths:
        page_href = '''//a[@href="/reportcentral/ref=xx_fbareports_foot_xx"]'''     # 报告库页面入口元素
        child_page_href = '''(//a[@href="/reportcentral/STORAGE_FEE_CHARGES/1"])[1]'''     # 月度仓储费页面入口元素

        request_download_csv = '''//kat-button[@value="CSV"]'''
        request_download_txt = '''//kat-button[@value="TSV"]'''

        download_link_nav = '''//*[@id='root']//a[@id='reportpage_download_tab']'''    # 下载链接导航
        no_data_available = '''//kat-table-body/kat-table-row[1]/kat-table-cell[last()][not(*)]'''    # 第一行没有可用数据元素
        download_btn = '''//kat-table-body/kat-table-row[1]/kat-table-cell[last()]/kat-button''' # 第一行下载按钮        

    class Sel:
        sel = package.selector
        year = sel("月度仓储费-年")
        month = sel("月度仓储费-月")


    def __init__(self, web_page):
        self.web_page = web_page



    def to_storage_fee_charges_page(self):
        web_page = self.web_page
        isinstance(web_page, xbot.web.WebBrowser)
        domain = get_domain(web_page)
        url = f"{domain}/reportcentral/STORAGE_FEE_CHARGES/1"
        if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
        ):
            return
        # 如果不是，则导航到目标URL
        web_page.navigate(url, load_timeout=300)
        handler_container(web_page)
        #旧版元素没有，用新的方案
        # # # 进入库存和销量报告页面
        # url = "/reportcentral/ref=xx_fbareports_foot_xx"
        # utils.to_page(web_page, url, self.XPaths.page_href, self.XPaths.child_page_href)

        # 进入月度仓储费下载页面
        # url = "/reportcentral/STORAGE_FEE_CHARGES/1"
        # utils.to_page(web_page, url, self.XPaths.child_page_href, self.XPaths.request_download_csv, is_to_home=True)


    def set_download_params(self, year_month):
        web_page = self.web_page
        year, month = year_month.split("-")
        web_page.find(self.Sel.year).find_by_xpath(".//kat-option[@value='{}']".format(year)).click(simulative=False)
        web_page.find(self.Sel.month).find_by_xpath(".//kat-option[@value='{}']".format(int(month)-1)).click(simulative=False)


    def wait_request_completed(self, report_type, wait_time):
        """等待请求完成"""
        web_page = self.web_page
        isinstance(web_page, xbot.web.WebBrowser)
        if report_type.upper() == "CSV":
            find_by_xpath(web_page, self.XPaths.request_download_csv).click(simulative=False)
        else:
            find_by_xpath(web_page, self.XPaths.request_download_txt).click(simulative=False)
        
        sleep(5)    # 等待请求发送出去，或者改成等待请求中元素出现？
        xpath_map = {
            "no_data_available" : self.XPaths.no_data_available,
            "download_btn" : self.XPaths.download_btn
        }
        name, ele = None, None
        # 等待报告生成，带刷新机制
        for retry in range(50):
            try:
                name, ele = utils.find_any_one_by_xpath(web_page, xpath_map, timeout=2)
                if name is not None:
                    break
            except Exception as e:
                # 点击下载链接导航刷新
                try:
                    web_page.find_by_xpath(self.XPaths.download_link_nav).click()
                    sleep(3)
                except:
                    pass
        
        return name, ele


    def check_params(self, year_month, wait_time):
        """参数校验"""
        try:
            wait_time = int(wait_time)
            if bool(year_month):
                year_month = datetime.to_string(datetime="{}-01".format(year_month), format="%Y-%m")
                datetime_instance, _ = datetime.add(datetime="", timeway="decrease", duration="2", unit="year", output_text=False)
                start_date = datetime.to_string(datetime=datetime_instance, format="%Y-%m")
                end_date = datetime.to_string(datetime="", format="%Y-%m")
                assert start_date <= year_month <= end_date, "只支持前3年当月到今年当月的日期区间"
            else:
                datetime_instance, _ = datetime.add(datetime="", timeway="decrease", duration="1", unit="month", output_text=False)
                year_month = datetime.to_string(datetime=datetime_instance, format="%Y-%m")
            return year_month
        except Exception as e:
            raise ValueError(str(e))    
        
        

    @utils.retry_processing(err_output_args=[""])
    def run(self, save_dir, save_name, report_type="CSV", year_month=None, wait_time=300):
        """月度仓储费报表下载入口函数"""
        web_page = self.web_page
        run_status = False

        # 参数校验
        year_month = self.check_params(year_month, wait_time)
        # # 切换站点
        # _amazon_api.switch_site(web_page)
        # 进入指定页面
        self.to_storage_fee_charges_page()
        # 设置下载参数
        self.set_download_params(year_month)
        # 等待请求完成
        name, ele = self.wait_request_completed(report_type, wait_time)
        if name == "no_data_available":
            raise ValueError("没有可用数据")    
        if name is None:
            raise Exception("长时间等待，文件状态加载中")
            
        # 点击下载按钮
        ele.click()
        
        # 下载文件
        return download_handler(web_page, save_dir, save_name,wait_time=wait_time)


def main(args):
    date = "2023-0801"
    res = xbot_visual.datetime.to_string(datetime=date, format="%Y/%m/%d")
    print(res)
    pass
