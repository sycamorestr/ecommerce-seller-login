# 此模块主要处理 【库存和销量报告】 页面下 【买家退货】报告下载操作
# 网址：/reportcentral/CUSTOMER_RETURNS/1
# 

import xbot
import xbot_visual
from xbot import print, sleep
from .import package
from .package import variables as glv

 
from . import utils 
from . import download_utils
from . import _amazon_api

from .utils import print
from .utils_beta import find_by_xpath

class CustomerReturnsHandler:

    class XPath:
        page_href = '''//a[@data-menu-id="fulfillment-report" or @data-menu-id="ssof-inventory-manager-new"]'''     # 报告库页面入口元素
        child_page_href = '''(//a[@href="/reportcentral/CUSTOMER_RETURNS/1"])[1]'''     # 买家退货页面入口元素

        request_download_csv = '''//kat-button[@value="CSV"]'''
        request_download_txt = '''//kat-button[@value="TSV"]'''

        download_link_nav = '''//*[@id='root']//a[@id='reportpage_download_tab']'''    # 下载链接导航
        no_data_available = '''//kat-table-body/kat-table-row[1]/kat-table-cell[last()][not(*)]'''    # 第一行没有可用数据元素
        download_btn = '''//kat-table-body/kat-table-row[1]/kat-table-cell[last()]/kat-button''' # 第一行下载按钮

    class Sel:
        sel = package.selector
        daily_time_picker = sel("买家退货-时间类型下拉框")
        start_time_input = sel("买家退货-开始日期-输入框")
        end_time_input = sel("买家退货-结束日期-输入框")
        dates_listbox = sel("买家退货-可选日期父元素")

    def __init__(self, web_page):
        self.web_page = web_page
        


    def to_customer_returns_page(self):
        """进入买家退货下载页面"""
        web_page = self.web_page
        isinstance(web_page, xbot.web.WebBrowser)

        # # # 进入库存和销量报告页面:元素找不到，先注释掉
        # url = "/reportcentral/ref=xx_fbareports_foot_xx"
        # utils.to_page(web_page, url, self.XPath.page_href, self.XPath.child_page_href)
        # print(url)
        # 进入买家退货下载页面
        url = "/reportcentral/CUSTOMER_RETURNS/1"
        utils.to_page(web_page, url, self.XPath.child_page_href, self.XPath.request_download_csv, is_to_home=False)
        print(url)
    

    
    def set_download_params(self, start_date,end_date):
        """
        设置下载参数
        """
        web_page = self.web_page
        isinstance(web_page, xbot.web.WebBrowser)
        listbox = web_page.find(self.Sel.dates_listbox).find_by_xpath('.//slot[@role="listbox"]')
        # 日期
        if bool(start_date) and bool(end_date):

            find_by_xpath(listbox, "./kat-option[@value='-1']").click(simulative=False)

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
        isinstance(web_page, xbot.web.WebBrowser)
        if report_type.upper() == "CSV":
            find_by_xpath(web_page, self.XPath.request_download_csv).click(simulative=False)
        else:
            find_by_xpath(web_page, self.XPath.request_download_txt).click(simulative=False)
        
        # 判断是否请求失败
        request_report_error_xpath = '//*[@class="request-report-error"]'
        request_report_error = web_page.find_all_by_xpath(request_report_error_xpath, timeout=5)
        if len(request_report_error) > 0:
            print('当前报表请求失败，请查看是否达到每日下载次数上限 或 遇到网络波动')
            return False, False

        sleep(5)    # 等待请求发送出去，或者改成等待请求中元素出现？
        xpath_map = {
            "no_data_available" : self.XPath.no_data_available,
            "download_btn" : self.XPath.download_btn
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
                    web_page.find_by_xpath(self.XPath.download_link_nav).click()
                    sleep(3)
                except:
                    pass
        
        return name, ele

    def check_params(self, save_name, start_date,end_date, wait_time):
        """参数校验"""
        try:
            
             # 文件名校验
            if bool(save_name) and "." not in save_name:
                raise ValueError("请填写完整文件名（需要加上文件后缀名）")

            # 日期校验
            if bool(start_date) and bool(end_date):
                try:
                    start_date_str = xbot_visual.datetime.to_string(datetime=start_date, format="%Y/%m/%d")
                    end_date_str = xbot_visual.datetime.to_string(datetime=end_date, format="%Y/%m/%d")
                except Exception as e:
                # 捕获可能的日期格式化错误
                    raise ValueError(f"日期格式无效或无法转换: {e}")

            # 3. 比较日期
                assert end_date_str >= start_date_str, "开始日期不能大于结束日期，请重新选择日期范围"

        # 4. (新增) 检查是否只提供了其中一个日期
            elif bool(start_date) or bool(end_date):
                raise ValueError("开始日期和结束日期必须同时提供，或同时为空")
            wait_time = int(wait_time)
        except Exception as exception:
            raise ValueError(str(exception))
        
    
    @utils.retry_processing(err_output_args=[""])
    def run(self, save_dir, save_name, start_date,end_date,report_type="CSV",  wait_time=300):
        """买家退货报表下载入口函数"""
        web_page = self.web_page
        run_status = False

        # 参数校验
        self.check_params(save_name, start_date,end_date, wait_time)

        # 进入指定页面
        self.to_customer_returns_page()

        # 设置页面参数
        self.set_download_params(start_date,end_date)

        # 等待请求完成
        name, ele = self.wait_request_completed(report_type, wait_time)
        if name == "no_data_available":
            raise ValueError("没有可用数据")
        if name is None:
            raise Exception("长时间等待，文件状态加载中")
        if name is False:
            return

        # 下载文件（使用支持紫鸟弹窗处理的下载方法）
        return download_utils.download_handler(web_page, ele, save_dir, save_name, wait_time)

def main(args):
    web_page = xbot.web.get_active(mode='superbrowser')
    handle = CustomerReturnsHandler(web_page)
    handle.run(r'C:\Users\thinkpad\Desktop\测试', '测试下载,csv', '2025-12-12', '2025-12-13')

        

