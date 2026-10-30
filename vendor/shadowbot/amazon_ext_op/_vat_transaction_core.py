
# 此模块主要处理 【库存和销量报告】 页面下 【亚马逊增值税交易报告】报告下载操作
# 网址：/reportcentral/VAT_TRANSACTION/1
# 

import xbot
import xbot_visual
from xbot import print, sleep
from xbot.web import WebBrowser
from .import package
from .package import variables as glv


from . import utils
from . import download_utils

from . import _amazon_api

from .utils import print,get_domain
from .utils import handler_container
from .utils_beta import find_by_xpath



class VatTransactionHandler:

    class XPath:
        page_href = '''//a[@data-menu-id="fulfillment-report"]'''     # 报告库页面入口元素
        child_page_href = '''(//a[@href="/reportcentral/VAT_TRANSACTION/1"])[1]'''     # 亚马逊增值税交易报告页面入口元素

        request_download_csv = '''//kat-button[@value="CSV"]'''
        request_download_txt = '''//kat-button[@value="TSV"]'''

        no_data_available = '''//kat-table-body/kat-table-row[1]/kat-table-cell[last()][not(*)]'''    # 第一行没有可用数据元素
        download_btn = '''//kat-table-body/kat-table-row[1]/kat-table-cell[last()]/kat-button''' # 第一行下载按钮

    class Sel:
        sel = package.selector
        daily_time_picker = sel("买家退货-时间类型下拉框")
        start_time_input = sel("买家退货-开始日期-输入框")
        end_time_input = sel("买家退货-结束日期-输入框")
        dates_listbox = sel("买家退货-可选日期父元素")


    def __init__(self, web_page: WebBrowser):
        self.web_page = web_page

    

    def to_vat_transaction_page(self):
        """进入亚马逊增值税交易报告下载页面"""
        web_page = self.web_page
        isinstance(web_page, xbot.web.WebBrowser)

        # # # 进入库存和销量报告页面
        # url = "/reportcentral/ref=xx_fbareports_foot_xx"
        # utils.to_page(web_page, url, self.XPath.page_href, self.XPath.child_page_href)

        # 进入亚马逊增值税交易报告下载页面
        # url = "/reportcentral/VAT_TRANSACTION/1"
        # utils.to_page(web_page, url, self.XPath.child_page_href, self.XPath.request_download_csv, is_to_home=False)
        domain = get_domain(web_page)
        url = f"{domain}/reportcentral/VAT_TRANSACTION/1"
        if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
        ):
            return
        # 如果不是，则导航到目标URL
        web_page.navigate(url, load_timeout=300)
        handler_container(web_page)
    
    def set_download_params(self, date_range: str):
        """
        设置下载参数
        """
        web_page = self.web_page
        listbox = web_page.find(self.Sel.dates_listbox)
        # 日期
        if bool(date_range):
            date_range_list = date_range.split("_")
            for i in range(len(date_range_list)):
                date_range_list[i] = xbot_visual.datetime.to_string(datetime=date_range_list[i], format="%Y/%m/%d")
            start_date, end_date = date_range_list
            find_by_xpath(listbox, ".//kat-option[@value='-1']").click(simulative=False)

            # 由于不同站点的日期输入格式可能不一样，需要校验一下
            start_time_ele = web_page.find(self.Sel.start_time_input) # .input(start_date)
            placeholder = start_time_ele.get_attribute("placeholder")
            placeholder = placeholder.replace("YYYY", "%Y").replace("MM", "%m").replace("M", "%m").replace("DD", "%d")
            start_date = xbot_visual.datetime.to_string(datetime=start_date, format=placeholder)
            end_date = xbot_visual.datetime.to_string(datetime=end_date, format=placeholder)
            
            # 填写日期
            web_page.find(self.Sel.start_time_input).input(start_date)
            web_page.find(self.Sel.end_time_input).input(end_date)
            web_page.find(self.Sel.start_time_input).click()
           
        else:
            # 点击最近30天
            find_by_xpath(listbox, "./kat-option[@value='30']").click(simulative=False)

    def wait_request_completed(self, report_type, wait_time):
        """等待请求完成"""
        web_page = self.web_page
        if report_type.upper() == "CSV":
            find_by_xpath(web_page, self.XPath.request_download_csv).click(simulative=False)
        else:
            find_by_xpath(web_page, self.XPath.request_download_txt).click(simulative=False)
        
        sleep(5)    # 等待请求发送出去，或者改成等待请求中元素出现？
        xpath_map = {
            "no_data_available" : self.XPath.no_data_available,
            "download_btn" : self.XPath.download_btn
        }
        name, ele = None, None
        try:
            name, ele =  utils.find_any_one_by_xpath(web_page, xpath_map, timeout=wait_time)
        except Exception as e:
            pass
        
        return name, ele            



    def check_params(self, save_name, date_range, wait_time):
        """参数校验"""
        try:
            
             # 文件名校验
            if bool(save_name) and "." not in save_name:
                raise ValueError("请填写完整文件名（需要加上文件后缀名）")

            # 日期校验
            if bool(date_range):
                assert "_" in date_range, "请按照指定格式填写日期范围"
                date_range_list = date_range.split("_")
                for i in range(len(date_range_list)):
                    date_range_list[i] = xbot_visual.datetime.to_string(datetime=date_range_list[i], format="%Y/%m/%d")
                start_date, end_date = date_range_list

                assert end_date >= start_date, "开始日期不能大于结束日期，请重新选择日期范围"
                date_range = date_range_list
            
            wait_time = int(wait_time)
        except Exception as exception:
            raise ValueError(str(exception))


    def run(self, site_name, save_dir, save_name, report_type="CSV", date_range=None, wait_time=300):
        """亚马逊增值税交易报告入口函数"""
        web_page = self.web_page
        run_status = False
        # 参数校验
        self.check_params(save_name, date_range, wait_time)

        # 切换站点
        _amazon_api.switch_site(web_page, site_name)
        # 进入指定页面
        self.to_vat_transaction_page()
        # 设置页面参数
        self.set_download_params(date_range)
        # 等待请求完成
        name, ele = self.wait_request_completed(report_type, wait_time)
        if name == "no_data_available":
            raise ValueError("没有可用数据")    
        if name is None:
            raise Exception("长时间等待，文件状态加载中")            

        # 下载文件
        return download_utils.download_file(web_page, ele, save_dir, save_name, wait_time)

        

