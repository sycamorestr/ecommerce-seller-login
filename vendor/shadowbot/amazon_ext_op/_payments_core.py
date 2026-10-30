# 此模块主要处理  付款 页面下的相关操作
# 网址：/payments
#

import xbot
import xbot_visual
from xbot import print, sleep, web, win32
from . import package
from .package import variables as glv
from xbot.web import WebBrowser
from xbot._core.retry import Retry 
import re
import os
import time
import json
from datetime import datetime
import random
from . import utils
from . import utils_beta
from . import _amazon_api
from .utils import print, to_page, wait_responses, start_monitor_network, find_any_one_by_xpath, handler_container
from .utils_beta import find_by_xpath
from .activities_utils import download_handler
from xbot.selector import Selector


def handle_captcha(web_page:xbot.web.WebBrowser):
    """处理亚马逊数英验证码"""
    # 构造验证码 xpath selector
    captcha_data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//iframe[@id="aa-challenge-whole-page-iframe"]', '//img[@alt="captcha"]']}}
    captcha_selector = Selector(captcha_data)
    captcha_input_data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//iframe[@id="aa-challenge-whole-page-iframe"]', '//input[@id="aa_captcha_input"]']}}
    captcha_input_selector = Selector(captcha_input_data)
    submit_data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//iframe[@id="aa-challenge-whole-page-iframe"]', '//input[@name="submit_button"]']}}
    submit_selector = Selector(submit_data)

    for i in range(5):

        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=captcha_selector):
            xbot.logging.info("处理亚马逊数英验证码开始")    
            try:
                web_element = web_page.find(captcha_selector)
                result = xbot_visual.web_service.cloud_captch(
                    captcha_engine="jfbym",
                    captcha_type="10111",
                    image_source="web",
                    web_page=web_page,
                    web_element=web_element,
                    win_element=None,
                    image_url=None,
                    image_path=None,
                    timeout="20",
                )
                web_page.find_by_xpath(captcha_input_selector).input(result)
                web_page.find_by_xpath(submit_selector).click()
            except Exception as e:
                xbot.logging.error(f"验证码处理异常: {e}")
            sleep(3)  # 控制频率，避免封号
        else:
            break  # 如果验证码元素已消失，跳出
    else:
        xbot.logging.info("处理亚马逊数英验证码结束")

    

class ReportsHandler:
    """
    报告库页面操作：下载报表
    网址：/payments/reports-repository
    """
    class XPaths:
        """XPaths"""

        parent = '''//article[contains(@class, "page-search-request-section")]'''  # 主框元素，由于亚马逊偶尔会出现一些隐藏元素，影响定位。用这个父元素限定一下范围

        report_status = '''(//kat-table-row[1]//div[@class="status-indicator-box"]/kat-statusindicator)[1]'''  # 第一行请求状态
        first_btn = '''(//kat-table-row[1]//kat-table-cell/div[@class="report-action"]/kat-button)[1]'''  # 第一行 刷新|下载 按钮

        account_type_dropdown = '''//*[@class="page-section-content justify-content-center"]//*[@class="account-type-selection selection-filter"]/kat-dropdown'''
        report_tag = parent + '''//*[@id="report-tag-input"]'''  # 报告标签输入框
        request_report_btn = parent + '''//*[@id="filter-generate-button"]'''  # 请求报告按钮
        monthly_radio = parent + '''//input[@value="MONTHLY" and @name="dateRangeType" and @type="radio"]'''  # 月份单选框
        custom_radio = parent + '''//input[@value="CUSTOM" and @name="dateRangeType" and @type="radio"]'''  # 自定义日期范围单选框

        credit_card_info = '''//*[@id="go-to-credit-card-info"]'''  # 出现这个元素表示信用卡失效

        ad = '''//*[@id="react-joyride-portal"]'''
        ad2 = '''//*[@id="react-joyride-step-0"]'''
        ad3 = '//button[@aria-label="Close"]'
        ad4 = '//div[@id="hmd2f-container"]'

        # 
        modify = '//kat-table-row[1]//kat-modal[@class="report-modify-dialogue"]'       # 计划于x时间内生成的修改按钮

    class Sel:
        """元素库"""
        sel = package.selector
        report_type = sel("报告库-报告类型-下拉框")
        account_type = sel("报告库-账户类型-下拉框")
        start_date = sel("报告库-开始日期-输入框")
        end_date = sel("报告库-结束日期-输入框")
        check_mark = sel("报告库-第一行准备就绪")

    def __init__(self, web_page):
        self.web_page = web_page

    def get_domain(self):
        """获取domain"""
        url = self.web_page.get_url()
        res = re.search("https?://sellercentral.+?amazon.+?(?=/)", url)
        if not res: raise Exception("请先进入亚马逊商家后台")
        return res.group()

    def to_reports_repository_page(self):
        """进入报告库页面"""
        url = "/payments/reports-repository?ref_=xx_rrepo_ttab_dash"
        to_page(self.web_page,
                url,
                suss_ele_xpath=self.XPaths.request_report_btn,
                is_to_home=False)
        
        # if has_credit_card_info: raise ValueError("信用卡失效")

    def set_download(self, account_type, report_type, report_tag, date_range):
        """设置下载参数"""
        web_page = self.web_page
        assert isinstance(web_page, xbot.web.WebBrowser)

        if not account_type:
            account_type = '标准订单'

        # 账户类型
        if account_type and find_by_xpath(web_page, self.XPaths.account_type_dropdown).get_attribute("disabled") != "true":
            account_type_map = {
                 '标准订单': 'PAYABLE',
                '发票支付订单': 'INVOICING',
                '全部（联合报告）': 'ALL',
                'Visa 信用卡': 'CC_VISA',
                '万事达信用卡及其他': 'PAYABLE',
                '美国运通卡': 'CC_AMERICAN_EXPRESS',
                'Elo': 'CC_ELO',
                'Diners Club': 'CC_DINERS_CLUB',
                'Visa 借记卡': 'DC_VISA',
                'MasterCard 借记卡': 'DC_MASTERCARD',
                'Boleto': 'BOLETO'
            }
            account_en_map = {
                "全部（联合报告）": "All (Unified Reports)",
                "标准订单": "Standard Orders",
                "发票支付订单": "Invoiced Orders",
                "Visa 信用卡": "Visa Credit",
                '万事达信用卡及其他':"Mastercard Credit & Other",
                '美国运通卡': "Amex",
                'Elo': 'Elo',
                'DinersClub': 'Diners Club',
                'Visa借记卡': 'Visa Debit',
                'MasterCard借记卡': 'Mastercard Debit',
                'Boleto': 'Boleto'
            }
            account_en = account_en_map.get(account_type)
            account_types = account_type_map.get(account_type)
            account_type_xpath = f'.//kat-option[(normalize-space(.)="{account_types}" or normalize-space(.)="{account_types}" or @value="{account_types}") and .//*[text()="{account_type}" or text()="{account_en}"]]'
            parent_ele = find_by_xpath(web_page, self.XPaths.parent)
            account_ele = utils.find_by_parent(web_page, self.Sel.account_type, parent_ele)
            account_ele.click(simulative=False)
            try:
                account_ele.find_by_xpath(account_type_xpath, timeout=5).click(simulative=False)
            except Exception as e:
                raise f'{account_type} 不在当前站点可用账户类型选项中:{e}'
        elif account_type != "标准订单":
            raise Exception('账户类型错误')
        
        # 报告类型
        report_type_map = {
            "汇总": "SELLER_SUMMARY_DATE_RANGE",
            "交易": "SELLER_TRANSACTION_DATE_RANGE",
            "延迟交易": "SELLER_HOLD_DATE_RANGE"
        }
        report_type = report_type_map.get(report_type)
        report_type_xpath = f'.//kat-option[@value="{report_type}"]'

        parent_ele = find_by_xpath(web_page, self.XPaths.parent)
        report_ele = utils.find_by_parent(web_page, self.Sel.report_type, parent_ele)
        report_ele.click(simulative=False)
        report_ele.find_by_xpath(report_type_xpath, timeout=5).click(simulative=False)

        # 报告标签
        if report_tag:
            find_by_xpath(web_page,
                          self.XPaths.report_tag).input(report_tag)

        # 日期
        if bool(date_range):
            start_date, end_date = date_range.split("_")

            # find_by_xpath(web_page, self.XPaths.custom_radio).click()
            # web_page.find(self.Sel.start_date).input(start_date)
            # web_page.find(self.Sel.end_date).input(end_date)
            # find_by_xpath(web_page, self.XPaths.custom_radio).click()

            find_by_xpath(web_page, self.XPaths.custom_radio).click()

            # 将日期改成页面需要的格式
            start_date_ele = utils.find_by_parent(web_page,
                                                  self.Sel.start_date,
                                                  parent_ele)
            end_date_ele = utils.find_by_parent(web_page, self.Sel.end_date,
                                                parent_ele)

            placeholder = start_date_ele.get_attribute("placeholder")
            placeholder = placeholder.replace("YYYY", "%Y").replace(
                "MM", "%m").replace("M", "%m").replace("DD", "%d")
            start_date = xbot_visual.datetime.to_string(datetime=start_date,
                                                        format=placeholder)
            end_date = xbot_visual.datetime.to_string(datetime=end_date,
                                                      format=placeholder)
            start_date_ele.click()
            start_date_ele.input(start_date, delay_after=0)
            end_date_ele.click()
            end_date_ele.input(end_date, delay_after=0)
            find_by_xpath(web_page, self.XPaths.custom_radio).click()
            if start_date_ele.get_value(
            ) != start_date or end_date_ele.get_value() != end_date:
                raise Exception("日期框输入失败")

        else:
            find_by_xpath(web_page, self.XPaths.monthly_radio).click()

    def _wait_request_completed(self, wait_time):
        """等待请求完成"""
        web_page = self.web_page
        wait_time = int(wait_time)

        monitor_url = "*payments/reports/api/request-report*"

        def get_status():
            """获取请求状态，是否可用"""
            status_ele = find_by_xpath(web_page,
                                       self.XPaths.report_status,
                                       timeout=20)
            status = status_ele.get_attribute("variant")
            status_desc = status_ele.get_attribute("label")
            if status not in ["success", "loading", "", "pending", None]: 
                raise ValueError(f"请求报告状态 - {status_desc}，无法下载")
            if status == "success":
                try:
                    web_page.find(self.Sel.check_mark)
                    return True
                except:
                    pass

            return False

        utils.start_monitor_network(web_page)
        find_by_xpath(web_page, self.XPaths.request_report_btn).click()
        responses = utils.wait_responses(web_page,
                                         monitor_url,
                                         resource_type="All",
                                         timeout=10)

        if not bool(responses): raise Exception("请求报告发送失败")

        start_time = time.time()
        sleep(5)
        while True:
            if get_status(): break

            find_by_xpath(web_page, self.XPaths.first_btn).click()

            if get_status(): break

            time_left = wait_time - (time.time() - start_time)

            if time_left <= 0: raise Exception("长时间等待文件生成失败")

            if time_left <= 10:
                sleep(time_left)

            else:
                sleep(random.randint(5, 10))

    def wait_request_completed(self, wait_time):   
        """等待请求完成"""
        
        def get_status():
            """获取请求状态，是否可用"""
            status_ele = find_by_xpath(self.web_page,
                                       self.XPaths.report_status,
                                       timeout=20)
            status = status_ele.get_attribute("variant")
            # xbot.logging.info(f"请求完成状态: {status}")
            status_desc = status_ele.get_attribute("label")
            if status not in ["success", "loading", "", None, "pending"]:
                raise ValueError(f"请求报告状态 - {status_desc}，无法下载")
            if status == "success":
                try:
                    self.web_page.find(self.Sel.check_mark, timeout=5)
                except:
                    pass
                return True

            return False
        
        find_by_xpath(self.web_page, self.XPaths.request_report_btn).click()
        sleep(1)
        find_by_xpath(self.web_page, self.XPaths.first_btn, timeout=10)
        num = 0
        for _ in Retry(timeout=wait_time, interval=5, ignore_exception=True):
            if get_status():
                return
            try:
                find_by_xpath(self.web_page, self.XPaths.first_btn, timeout=3).click()
            except:
                if num == 3:
                    break
                # 判断任务是否当前无法下载
                modify_button = self.web_page.find_all_by_xpath(self.XPaths.modify, timeout=3)
                if len(modify_button) > 0:
                # 如果没有刷新按钮，则重新加载页面
                    self.web_page.reload()
                    num += 1

        raise Exception("长时间等待文件生成失败")
    
    def wait_request_completed_boyin(self):
        #点击请求报告
        web_page = self.web_page
        # web_page.find("res_report").click()
        
        #验证是否可下载
        for retry in range(100):
            try:
                web_page.find("report_lib_download_mark",timeout=2)
                break
            except:
                web_page.find("report_lib_download").click()
                continue
        # web_page.find("report_lib_download").click()  
        
    def close_ad(self):
        """关闭弹窗"""
        xpaths = "|".join([self.XPaths.ad, self.XPaths.ad2, self.XPaths.ad3, self.XPaths.ad4])
        eles = self.web_page.find_all_by_xpath(xpaths, timeout=5)
        script = '''
            function (ele, input) {
                ele.style.display = "none";
            }
        '''
        for ele in eles:
            ele.execute_javascript(script)

    def check_params(self, save_dir, save_name, date_range, report_type):
        """参数校验"""

        # 文件夹校验
        if not bool(save_dir) or not os.path.exists(save_dir):
            raise ValueError("文件夹不存在，请先创建文件夹 - {}".format(save_dir))

        # 文件名校验
        if bool(save_name) and "." not in save_name:
            raise ValueError("请填写完整文件名（需要加上文件后缀名）")

        # 日期校验
        if bool(date_range):
            try:
                assert "_" in date_range, "请按照指定格式填写日期范围"
                date_range_list = date_range.split("_")
                for i in range(len(date_range_list)):
                    date_range_list[i] = xbot_visual.datetime.to_string(
                        datetime=date_range_list[i], format="%Y/%m/%d")
                start_date, end_date = date_range_list

                assert end_date >= start_date, "开始日期不能大于结束日期，请重新选择日期范围"
            except Exception as exception:
                raise ValueError("日期范围错误：" + str(exception))

        #   报告类型处理
        report_type_map = {
            "汇总": "SELLER_SUMMARY_DATE_RANGE",
            "交易": "SELLER_TRANSACTION_DATE_RANGE",
            "延迟交易": "SELLER_HOLD_DATE_RANGE"
        }
        report_type = report_type_map.get(report_type, None)
        if report_type is None:
            raise ValueError("报告类型仅支持：汇总、交易、延迟交易")

    @utils.retry_processing(err_output_args=[""], retry_time=0)
    def run(self, site_name, account_type, report_type, report_tag, date_range, save_dir,
            save_name, wait_time):
        """下载报告库文件，入口函数"""

        web_page = self.web_page
        wait_time = float(wait_time)

        # 参数校验
        self.check_params(save_dir, save_name, date_range, report_type)
        # 切换站点
        _amazon_api.switch_site(web_page, site_name)
        # 进入下载报表页面
        status = self.to_reports_repository_page()
        # 关闭弹窗
        self.close_ad()
        # 设置下载参数
        self.set_download(account_type, report_type, report_tag, date_range)
        # 等待请求完成
        # self.wait_request_completed(wait_time)
        self.wait_request_completed(wait_time)
        # sleep(2)
        
        # 点击下载按钮
        web_page.find("report_lib_download").click()
        sleep(1)
        
        # 使用 download_handler 处理下载和紫鸟弹窗
        download_file_path = download_handler(web_page, str(save_dir), save_name)
        
        return download_file_path


class PaymentsHandler:
    """
    结算一览页面操作：请求付款, 付款页面截图
    网址：/payments/dashboard/index.html
    """
    class XPaths:
        '''//*[@id="sc-content-container"]'''
        '''//a[@href="/gp/seller/configuration/ccInfo.html"]/*[@id="go-to-credit-card-info"] '''
        home = '''//*[@id="sc-content-container"]'''  # 付款页面链首页元素
        
        payments_account = '''//a[contains(@data-menu-id, "payments-account")]'''  # 付款页面链接元素
        alert_container = '''//div[contains(@class, "dashboard-alert-container")]'''  # 这个元素出现，则表示没有付款数据，通过hidden判断
        content_container = '''//div[contains(@class, "dashboard-content-container")]'''  #  这个元素出现，则表示有付款数据，通过hidden判断
        CardInfo = '''(//*[@id="go-to-credit-card-info"])[1]'''  # 出现这个表示支付方式无效

        payment_request_btn1 = '''(//div[@class="custom-child-available-balance"]/kat-button[@type="submit"])[1]'''  # 结算一览_标准订单请求付款
        payment_request_btn21 = '''((//div[@class="custom-child-available-balance"])[2]/kat-button[@type="submit"])[1]'''  # 结算一览_发票支付订单请求付款
        balance = '''(//kat-card//div[contains(@class, "currency-amount")]/span)[1]'''  # 结算一览_标准订单当前余额
        invoice_payment_balance = '''(//kat-card//div[contains(@class, "currency-amount")]/span)[2]'''  # 结算一览_发票支付订单当前余额
        payment_request_btn2 = '''(//div[@class="disburse-now-button"]/kat-button[@type="submit"])[1]'''  # 申请转账_请求付款
        get_balance = "//div[contains(@class,'amount-balance')]/div"  # 申请转账_当前余额
        transfer_message = '''//kat-alert'''  # 申请转账_转账提示信息

        currency_total_amount = '''//div[@class="currency-total-amount"]'''  # 结算一览_所有账户总余额
        pay_card_end = '//*[local-name()="kat-table-cell"][contains(@class, "transfer-account")]/div[contains(@class,"account-tail")]' # 银行账号尾号元素
        custom_payment_btn = '''(//div[contains(@class,'custom-child-available-balance')])[count(//div[contains(@class,'linkable-multi-row-card-row')][.//span[contains(@class,'marketplace-name-text') and normalize-space(text())='{}']]/preceding-sibling::div[contains(@class,'linkable-multi-row-card-row')]) + 1]//kat-button'''  # 结算一览_自定义类型请求付款按钮（{}为类型名占位）
        custom_balance = '''(//div[contains(@class,'available-currency-amount')])[count(//div[contains(@class,'linkable-multi-row-card-row')][.//span[contains(@class,'marketplace-name-text') and normalize-space(text())='{}']]/preceding-sibling::div[contains(@class,'linkable-multi-row-card-row')]) + 1]'''  # 结算一览_自定义类型当前余额（{}为类型名占位）

    def __init__(self, web_page):
        self.web_page = web_page

    def get_domain(self):
        """获取domain"""
        url = self.web_page.get_url()
        res = re.search("https?://sellercentral.+?amazon.+?(?=/)", url)
        if not res:
            raise Exception("请先进入亚马逊商家后台")
        return res.group()

    def to_account_summary_page(self):
        """进入账户一览页面"""
        web_page = self.web_page
        assert isinstance(web_page, xbot.web.WebBrowser)
        path = "/payments/dashboard/index.html/ref=xx_payments_foot_xx"
        domain = web_page.execute_javascript("() => origin")
        url = "{}{}".format(domain, path)
        web_page.navigate(url, load_timeout=30)
        handler_container(web_page)
        _amazon_api.login(web_page)

        # utils.to_page(web_page, url, self.XPaths.payments_account, self.XPaths.home)
        utils_beta.to_page(web_page, path, "|".join([self.XPaths.CardInfo, self.XPaths.content_container]))

    def get_displayed_transfer_message_elem(self):
        """获取可见的请求付款状态元素"""
        transfer_message_elems = self.web_page.find_all_by_xpath(
            self.XPaths.transfer_message)
        for transfer_message_elem in transfer_message_elems:
            if transfer_message_elem.is_displayed():
                return transfer_message_elem

        raise Exception("未找到请求付款状态元素")

    def payment_request(self, site_name, minimum_amount,is_comma_decimal=False):
        """请求付款入口函数"""
        web_page: WebBrowser = self.web_page

        minimum_amount = float(minimum_amount)
        minimum_amount = 0 if minimum_amount < 0 else minimum_amount

        # 切换站点, 如果不填站点, 就不自动切换站点
        if site_name:
            for _, set_last_error in Retry(times=3):
                try:
                    _amazon_api.switch_site(web_page, site_name)
                    sleep(1)
                    handle_captcha(web_page)
                    break
                except Exception as e:
                    set_last_error(e)
        
        @utils.retry_processing(err_output_args=["标准订单金额：0"], retry_time=1)
        def payment_request_standard():
            # print(111)
            # 跳转页面
            self.to_account_summary_page()
            sleep(1)
            handle_captcha(web_page)

            name, ele = find_any_one_by_xpath(
                web_page, {
                    "CardInfo": self.XPaths.CardInfo,
                    "content_container": self.XPaths.content_container,
                },
                timeout=30)

            if name == "CardInfo":
                raise ValueError("支付方式无效")

            content_container_ele = ele
            is_hidden = content_container_ele.get_attribute("hidden")

            # 判断是否有付款数据
            if is_hidden is True or is_hidden == "true" or is_hidden == "True":
                raise ValueError("没有付款数据")

            # 判断金额是否达到提现要求
            balance = find_by_xpath(web_page, self.XPaths.balance, timeout=50).get_text().strip()
            if is_comma_decimal:
                balance = balance.replace('.', '').replace(',', '.')
            tmp_balance = float(re.sub(r"[^\d\.\-+]", "", balance))
            if tmp_balance <= 0:
                raise ValueError(f"余额小于等于0，当前标准订单金额：{tmp_balance}")

            if tmp_balance < minimum_amount:
                raise ValueError(f"余额小于最小提现金额，当前标准订单金额：{tmp_balance}")

            # 点击请求付款按钮1
            try:
                web_ele = find_by_xpath(web_page, self.XPaths.payment_request_btn1)
                web_ele.click(simulative = False)
                # # 现在出现点击 请求付款按钮 后，需要重新登录的情况
                # _amazon_api.login(web_page)
                web_page.wait_load_completed(timeout=60)
                handle_captcha(web_page)
                # 等待网页地址变化，不再是 结算一览 页面
                for _ in Retry(timeout=50, ignore_exception=True):
                    if "payments/dashboard" not in web_page.get_url(): 
                        break
            except Exception as e:
                if "未找到元素" in str(e): raise Exception("【请求付款】按钮不存在")
                raise
            
            # 现在出现点击 请求付款按钮 后，需要重新登录的情况
            try:
                _amazon_api.login(web_page)
            except Exception as e:
                xbot.logging.warning(f"提现后登录检查异常: {e}")
            
            ele = find_by_xpath(web_page, self.XPaths.payment_request_btn2)
            is_disabled = ele.get_attribute("disabled") == "true"
            # print(is_disabled)
            # 判断请求付款按钮2是否可点击
            if is_disabled:
                # 请求付款按钮2 不可点击，返回提示信息和余额
                transfer_message = self.get_displayed_transfer_message_elem().get_text()
                return "标准订单金额：" + str(tmp_balance) + "|" + transfer_message

            ele.click(simulative=False)

            # 点击付款按钮后，可能会再次出现登录页面
            try:
                _amazon_api.login(web_page)
            except Exception as e:
                xbot.logging.warning(f"提现后登录检查异常: {e}")
            
            sleep(5)
            transfer_message_elem = self.get_displayed_transfer_message_elem()
            if transfer_message_elem.get_attribute("variant") != "success":
                # 转账失败，返回余额和提示信息
                return "标准订单金额：" + str(tmp_balance) + "|" + transfer_message_elem.get_text()
            # 转账成功
            return "标准订单金额：" + str(tmp_balance)
        
        
        @utils.retry_processing(err_output_args=["发票支付订单金额：0"], retry_time=1)
        def payment_request_invoice_payment():
            # print(222)
            # 跳转页面
            self.to_account_summary_page()
            sleep(1)
            handle_captcha(web_page)

            if len(web_page.find_all_by_xpath(self.XPaths.invoice_payment_balance, timeout=2)) == 0:
                return "发票支付订单金额：0"

            name, ele = find_any_one_by_xpath(
                web_page, {
                    "CardInfo": self.XPaths.CardInfo,
                    "content_container": self.XPaths.content_container,
                },
                timeout=30)

            if name == "CardInfo":
                raise ValueError("支付方式无效")

            content_container_ele = ele
            is_hidden = content_container_ele.get_attribute("hidden")

            # 判断是否有付款数据
            if is_hidden is True or is_hidden == "true" or is_hidden == "True":
                raise ValueError("没有付款数据")

            # 判断结算一览_发票支付订单当前余额是否达到提现要求
            invoice_payment_balance = find_by_xpath(web_page, self.XPaths.invoice_payment_balance, timeout=50).get_text().strip()
            if is_comma_decimal:
                invoice_payment_balance = invoice_payment_balance.replace('.', '').replace(',', '.')
            tmp_balance = float(re.sub(r"[^\d\.\-+]", "", invoice_payment_balance)) # 从结算一览_发票支付订单当前余额字符串中提取有效的数值（包括整数、小数、正负号）并转换为浮点数
            if tmp_balance <= 0:
                raise ValueError(f"余额小于等于0，当前标准订单金额：{tmp_balance}")

            if tmp_balance < minimum_amount:
                raise ValueError(f"余额小于最小提现金额，当前标准订单金额：{tmp_balance}")

            # 点击结算一览_发票支付订单请求付款按钮
            try:
                web_ele = find_by_xpath(web_page, self.XPaths.payment_request_btn21)
                web_ele.click(simulative = False)
                # # 现在出现点击 请求付款按钮 后，需要重新登录的情况
                # _amazon_api.login(web_page)
                web_page.wait_load_completed(timeout=60)
                handle_captcha(web_page)
                # 等待网页地址变化，不再是 结算一览 页面
                for _ in Retry(timeout=50, ignore_exception=True):
                    if "payments/dashboard" not in web_page.get_url(): 
                        break
            except Exception as e:
                if "未找到元素" in str(e): raise Exception("【请求付款】按钮不存在")
                raise
            
            # 现在出现点击 请求付款按钮 后，需要重新登录的情况
            try:
                _amazon_api.login(web_page)
            except Exception as e:
                xbot.logging.warning(f"提现后登录检查异常: {e}")
            
            ele = find_by_xpath(web_page, self.XPaths.payment_request_btn2)
            is_disabled = ele.get_attribute("disabled") == "true"
            # print(is_disabled)
            # 判断申请转账_请求付款按钮是否可点击
            if is_disabled:
                # 申请转账_请求付款按钮 不可点击，返回提示信息和余额
                transfer_message = self.get_displayed_transfer_message_elem().get_text()
                return "发票支付订单金额：" + str(tmp_balance) + "|" + transfer_message

            ele.click(simulative=False)
            sleep(5)
            transfer_message_elem = self.get_displayed_transfer_message_elem()
            if transfer_message_elem.get_attribute("variant") != "success":
                # 转账失败，返回余额和提示信息
                return "发票支付订单金额：" + str(tmp_balance) + "|" + transfer_message_elem.get_text()
            # 转账成功
            return "发票支付订单金额：" + str(tmp_balance)
        # 请求付款标准订单金额
        standard_current_balance = payment_request_standard()
        # 请求付款发票支付订单金额, 如果没有付款发票就不提现
        invoice_payment_current_balance = payment_request_invoice_payment()

        std_success, std_msg, std_result = standard_current_balance
        inv_success, inv_msg, inv_result = invoice_payment_current_balance

        # 提取金额和错误信息（失败但余额已知时，结果格式为"金额|错误信息"）
        if '|' in std_result:
            amount_str, extra_msg = std_result.split('|', 1)
            std_amount = float(amount_str.split('：')[1])
            std_msg = extra_msg if not std_msg else f"{std_msg};{extra_msg}"
            std_success = False
        else:
            std_amount = float(std_result.split('：')[1])
        
        if '|' in inv_result:
            amount_str, extra_msg = inv_result.split('|', 1)
            inv_amount = float(amount_str.split('：')[1])
            inv_msg = extra_msg if not inv_msg else f"{inv_msg};{extra_msg}"
            inv_success = False
        else:
            inv_amount = float(inv_result.split('：')[1])

        # 记录错误日志
        if not std_success:
            xbot.logging.error(f"标准订单请求付款失败: {std_msg}")
        if not inv_success:
            xbot.logging.error(f"发票支付订单请求付款失败: {inv_msg}")

        # 汇总错误信息（只拼接非空的）
        error_msgs = [msg for msg in [std_msg, inv_msg] if msg]
        merged_msg = ';'.join(error_msgs)

        total_amount = std_amount + inv_amount
        total_balance = f"总金额：{total_amount}"

        result_merge = (std_success,
                        merged_msg,
                        f"{std_result};{inv_result};{total_balance}",
                        std_amount,
                        inv_amount,
                        total_amount
                        )

        return result_merge

    def proceeds_screenshot(self, site_name, save_dir, save_name, cycle="0", account_type="", screenshot_range=""):
        """结算一览截图入口函数"""
        run_status = False
        currency_total_amount = 0
        cycle = int(cycle)

        try:
            # 参数校验
            assert save_dir != "" and os.path.exists(
                save_dir), f"文件夹不存在 - {save_dir}"
            web_page: xbot.web.WebBrowser = self.web_page

            _amazon_api.switch_site(web_page, site_name)

            self.to_account_summary_page()

            # //kat-label[@text="结算周期"]/following-sibling::*[1]

            name, ele = find_any_one_by_xpath(
                web_page, {
                    "CardInfo": self.XPaths.CardInfo,
                    "content_container": self.XPaths.content_container,
                },
                timeout=30)

            if name == "CardInfo":
                return run_status, "支付方式无效", currency_total_amount

            content_container_ele = find_by_xpath(
                web_page, self.XPaths.content_container)
            is_hidden = content_container_ele.get_attribute("hidden")

            # print(is_hidden)

            # 判断是否有付款数据
            if is_hidden is True or is_hidden == "true" or is_hidden == "True":
                return run_status, "没有付款数据", "", currency_total_amount

            currency_total_amount = find_by_xpath(
                web_page, self.XPaths.currency_total_amount).get_text()

            # 元素置顶，避免有其他元素遮挡
            code = '''
            function (ele, _) {
                ele.style.position = 'relative';
                ele.style.zIndex = '999999';
                ele.scrollIntoView();
                //ele.style.transform = 'scale(0.9)';
                     
            }
            '''
            content_container_ele.execute_javascript(code)
            sleep(1)
            # content_container_ele.screenshot(save_dir, filename=save_name)

            # 设置账户类型
            if account_type:
                account_type_xpath = '//*[@value="PAYABLE" or @value="INVOICING"]'
                web_page.find_by_xpath(account_type_xpath).click()
                if account_type == "标准订单":
                    print("选择标准订单")
                    web_page.find("结算一览-标准订单").click(move_mouse=True)
                if account_type == "发票支付订单":
                    web_page.find("结算一览-发票支付订单").click()
                    
            # 设置结算周期，新增字段， 兼容历史版本
            if cycle: 
                ele = web_page.find("付款面板-结算周期框")
                ele.click()
                eles = ele.find_all_by_xpath('.//*[@role="listbox"]/*')
                target_ele = eles[cycle] if len(eles) > cycle else eles[-1]
                cycle = target_ele.get_text()
                new_text = cycle.split(" ")[0]
                target_ele.click()

                if not save_name:
                    # xbot.logging.info(target_ele.get_text())
                    save_name = f"{site_name}-{target_ele.get_text().replace('/','-').replace(' ','')}.png"

            web_page.wait_load_completed(100)
            screenshot_file_name = os.path.join(save_dir, save_name)
            
            # 使用不同的截图区域
            screenshot_xpath = '//*[@id="a-page"]'
            # web_page.find_by_xpath(screenshot_xpath).screenshot(save_dir, filename=save_name)
            if screenshot_range == "仅大图":
                web_page.find_by_xpath(screenshot_xpath).screenshot(save_dir, filename=save_name)
            else:
                web_page.screenshot(save_dir, file_name=save_name, height=2500)
                # xbot.win32.screenshot.save_screen_to_file(screenshot_file_name, save_name.split(".")[-1],)
            
            run_status = True

            return run_status, "", screenshot_file_name, currency_total_amount
        except Exception as e:
            return run_status, str(e), "", currency_total_amount

    def get_account_data(self, site_name, account_type, cycle=0, switch_zh='是'):
        """结算一览数据获取入口函数"""
        run_status = False
        data = {}
        cycle = int(cycle)
        try:
            web_page = self.web_page
            if switch_zh == '是':
                _amazon_api.switch_language(web_page, "zh_CN")
            _amazon_api.switch_site(web_page, site_name)
            self.to_account_summary_page()
            content_container_ele = find_by_xpath(
                web_page, self.XPaths.content_container)
            is_hidden = content_container_ele.get_attribute("hidden")

            # print(is_hidden)
            # 判断是否有付款数据
            if is_hidden is True or is_hidden == "true" or is_hidden == "True":
                return run_status, "没有付款数据", []

            currency_total_amount = find_by_xpath(
                web_page, self.XPaths.currency_total_amount).get_text()

            # 元素置顶，避免有其他元素遮挡
            code = '''
            function (ele, _) {
                ele.style.position = 'relative';
                ele.style.zIndex = '999999';
                ele.scrollIntoView();
                //ele.style.transform = 'scale(0.9)';
                     
            }
            '''
            content_container_ele.execute_javascript(code)
            sleep(1)
            # content_container_ele.screenshot(save_dir, filename=save_name)

            # 进行账户类型选择
            # 设置账户类型
            if account_type:
                account_type_xpath = '//*[@value="PAYABLE" or @value="INVOICING"]'
                web_page.find_by_xpath(account_type_xpath).click()
                if account_type == "标准订单":
                    print("选择标准订单")
                    web_page.find("结算一览-标准订单").click(move_mouse=True)
                if account_type == "发票支付订单":
                    web_page.find("结算一览-发票支付订单").click()

            ele = web_page.find("付款面板-结算周期框")
            ele.click()
            eles = ele.find_all_by_xpath('.//*[@role="listbox"]/*')
            target_ele = eles[cycle] if len(eles) > cycle else eles[-1]
            cycle = target_ele.get_text()
            data["cycle"] = cycle
            new_text = cycle.split(" ")[0]
            target_ele.click()
            xpath = '//*[@class="multi-line-child-content"]/*[starts-with(text(), "{}")]'.format(
                new_text)
            # print(xpath)
            find_by_xpath(web_page, xpath)
            sleep(2)

            # 根据站点判断使用哪个字段列表
            # 荷兰、英国站点：期初余额没有单独金额，需要获取子项（结转金额、付款至亚马逊），共6个金额值
            # 其他站点：有"退款"字段，共6个金额值
            site_name_lower = str(site_name).lower() if site_name else ""
            special_sites = ["荷兰", "nl", "netherlands", "英国", "uk", "united kingdom", "gb"]
            is_special_site = any(site in site_name_lower for site in [s.lower() for s in special_sites])
            
            # 根据站点选择字段列表
            if is_special_site:
                # 荷兰、英国站点：期初余额没有单独金额，需要获取子项
                # 字段顺序：净收入、结转金额（期初余额子项）、付款至亚马逊（期初余额子项）、销售额、支出、账户级别的预留金额
                fields = [
                    "Net Proceeds", "Carried Forward Amount", "Payment to Amazon", 
                    "Sales", "Expenses", "Account Level Reserve"
                ]
                # 支持中文和英文
                dispaly_fields_cn = ["净收入", "结转金额", "付款至亚马逊", "销售额", "支出", "账户级别的预留金额"]
                dispaly_fields_en = ["Net Proceeds", "Carried Forward Amount", "Payment to Amazon", "Sales", "Expenses", "Account Level Reserve"]
            else:
                # 其他站点：有"退款"字段
                fields = [
                    "Net Proceeds", "Beginning Balance", "Sales", "Refunds",
                    "Expenses", "Account Level Reserve"
                ]
                # 支持中文和英文
                dispaly_fields_cn = ["净收入", "期初余额", "销售额", "退款", "支出", "账户级别的预留金额"]
                dispaly_fields_en = ["Net Proceeds", "Beginning Balance", "Sales", "Refunds", "Expenses", "Account Level Reserve"]
            
            # 先尝试使用中文字段，如果找不到再尝试英文字段
            dispaly_fields = None
            try:
                xpath = '//*[@class="print-primary-breakdown" and ./*[text()="{}"]]/*[last()]'.format(
                    dispaly_fields_cn[0])
                web_page.find_by_xpath(xpath, timeout=1)
                dispaly_fields = dispaly_fields_cn
            except:
                # 如果中文字段找不到，尝试英文字段
                try:
                    xpath = '//*[@class="print-primary-breakdown" and ./*[text()="{}"]]/*[last()]'.format(
                        dispaly_fields_en[0])
                    find_by_xpath(web_page, xpath, timeout=1)
                    dispaly_fields = dispaly_fields_en
                except:
                    raise Exception("无法找到字段元素，请检查页面语言设置")
            
            # 对于特殊站点，需要特殊处理子项字段
            if is_special_site:
                # 特殊站点：期初余额的子项需要使用不同的XPath
                for f1, f2 in zip(fields, dispaly_fields):
                    try:
                        if f2 in ["结转金额", "Carried Forward Amount", "付款至亚马逊", "Payment to Amazon"]:
                            # 子项字段需要使用更具体的XPath
                            # 根据HTML结构：h4标签和breakdown-amount在同一个top-level-breakdown-details容器中
                            # 先尝试精确匹配
                            xpath = '//h4[text()="{}"]/ancestor::div[contains(@class, "top-level-breakdown-details")]//div[contains(@class, "breakdown-amount")]'.format(f2)
                            element = find_by_xpath(web_page, xpath, timeout=0)
                            if element is None:
                                # 如果精确匹配找不到，尝试包含匹配
                                xpath = '//h4[contains(text(), "{}")]/ancestor::div[contains(@class, "top-level-breakdown-details")]//div[contains(@class, "breakdown-amount")]'.format(f2)
                                element = find_by_xpath(web_page, xpath, timeout=0)
                            if element is None:
                                # 如果还是找不到，尝试更宽松的匹配
                                xpath = '//h4[contains(text(), "{}")]/following-sibling::div[contains(@class, "breakdown-amount")][1]'.format(f2)
                                element = find_by_xpath(web_page, xpath, timeout=0)
                            if element is None:
                                raise Exception(f"未找到元素: {f2}")
                            value = element.get_text()
                        else:
                            # 普通字段使用原来的XPath
                            xpath = '//*[@class="print-primary-breakdown" and ./*[text()="{}"]]/*[last()]'.format(f2)
                            element = find_by_xpath(web_page, xpath, timeout=0)
                            if element is None:
                                raise Exception(f"未找到元素: {f2}")
                            value = element.get_text()
                        data[f1] = value
                    except Exception as e:
                        if "未找到元素" not in str(e):
                            raise
                        # 如果找不到元素，跳过该字段
                        print(f"警告：未找到字段 {f2}，跳过")
            else:
                # 其他站点：使用原来的逻辑
                for f1, f2 in zip(fields, dispaly_fields):
                    xpath = '//*[@class="print-primary-breakdown" and ./*[text()="{}"]]/*[last()]'.format(
                        f2)
                    try:
                        element = find_by_xpath(web_page, xpath, timeout=0)
                        if element is None:
                            raise Exception(f"未找到元素: {f2}")
                        value = element.get_text()
                        data[f1] = value
                    except Exception as e:
                        if "未找到元素" not in str(e):
                            raise
                        # 如果找不到元素，跳过该字段
                        print(f"警告：未找到字段 {f2}，跳过")

            return True, "", data
        except Exception as e:
            print(e)
            return run_status, str(e), {}
    
    #新增自动提现拆分两个单独的模块
    @utils.retry_processing(err_output_args=["标准订单金额：0"], retry_time=1)
    def process_standard_payment(self, site_name, minimum_amount,account_tail):
        web_page = self.web_page
        if site_name:
            for _, set_last_error in Retry(times=3):
                try:
                    _amazon_api.switch_site(web_page, site_name)
                    sleep(1)
                    handle_captcha(web_page)
                    break
                except Exception as e:
                    set_last_error(e)
        
        minimum_amount_float = float(minimum_amount)
        minimum_amount_float = 0 if minimum_amount_float < 0 else minimum_amount_float

        # 跳转页面
        self.to_account_summary_page()
        sleep(1)
        handle_captcha(web_page)

        name, ele = find_any_one_by_xpath(
            web_page, {
                "CardInfo": self.XPaths.CardInfo,
                "content_container": self.XPaths.content_container,
            },
            timeout=30)

        if name == "CardInfo":
            raise ValueError("支付方式无效")

        # 检查是否有付款数据
        content_container_ele = ele
        is_hidden = content_container_ele.get_attribute("hidden")
        if is_hidden is True or is_hidden == "true" or is_hidden == "True":
            raise ValueError("没有付款数据")

        # 检查余额
        balance = find_by_xpath(web_page, self.XPaths.balance, timeout=50).get_text().strip()
        tmp_balance = float(re.sub(r"[^\d\.\-+]", "", balance))
        if tmp_balance <= 0:
            raise ValueError(f"余额小于等于0，当前标准订单金额：{tmp_balance}")
        if tmp_balance < minimum_amount_float:
            raise ValueError(f"余额小于最小提现金额，当前标准订单金额：{tmp_balance}")

        # 7. 点击【请求付款】
        try:
            web_ele = find_by_xpath(web_page, self.XPaths.payment_request_btn1)
            web_ele.click(simulative=False)
            web_page.wait_load_completed(timeout=60)
            handle_captcha(web_page)
            # 等待网页地址变化
            for _ in Retry(timeout=50, ignore_exception=True):
                if "payments/dashboard" not in web_page.get_url():
                    break
        except Exception as e:
            if "未找到元素" in str(e): raise Exception("【请求付款】按钮不存在")
            raise
        
        # 处理登录跳转（login 失败不影响提现结果）
        try:
            _amazon_api.login(web_page)
        except Exception as e:
            xbot.logging.warning(f"提现后登录检查异常: {e}")

        # 新增：银行卡尾号校验
        if account_tail:  # 仅在传入了 account_tail 时才校验
            try:
                # 查找页面上的银行卡尾号元素
                page_account_tail_elem = find_by_xpath(web_page, self.XPaths.bank_account_tail, timeout=5)
                page_account_tail_text = page_account_tail_elem.get_text().strip()
                
                # 检查传入的尾号是否含在页面元素的文本中
                if account_tail not in page_account_tail_text:
                    raise ValueError(f"银行卡尾号校验失败！期望尾号: {account_tail}, 页面实际尾号: {page_account_tail_text}")
                else:
                    print(f"银行卡尾号校验成功: {account_tail}")

            except Exception as e:
                raise ValueError(e)
        
        # 判断是否能点击
        ele = find_by_xpath(web_page, self.XPaths.payment_request_btn2)
        is_disabled = ele.get_attribute("disabled") == "true"
        
        if is_disabled:
            transfer_message = self.get_displayed_transfer_message_elem().get_text()
            raise ValueError(transfer_message)

        ele.click(simulative=False)
        sleep(5)
        
        transfer_message = self.get_displayed_transfer_message_elem()
        if transfer_message.get_attribute("variant") != "success":
            transfer_message_text = transfer_message.get_text() 
            raise ValueError(transfer_message_text)

        return "标准订单金额：" + str(tmp_balance)

    # 新：单独处理发票订单

    @utils.retry_processing(err_output_args=["发票支付订单金额：0"], retry_time=1)
    def process_invoice_payment(self, site_name, minimum_amount,account_tail):

        web_page = self.web_page

        if site_name:
            for _, set_last_error in Retry(times=3):
                try:
                    _amazon_api.switch_site(web_page, site_name)
                    sleep(1)
                    handle_captcha(web_page)
                    break
                except Exception as e:
                    set_last_error(e)

        minimum_amount_float = float(minimum_amount)
        minimum_amount_float = 0 if minimum_amount_float < 0 else minimum_amount_float

        self.to_account_summary_page()
        sleep(1)
        handle_captcha(web_page)
        
        # 检查发票余额元素是否存在
        if len(web_page.find_all_by_xpath(self.XPaths.invoice_payment_balance, timeout=2)) == 0:
            return "发票支付订单金额：0"

        name, ele = find_any_one_by_xpath(
            web_page, {
                "CardInfo": self.XPaths.CardInfo,
                "content_container": self.XPaths.content_container,
            },
            timeout=30)

        if name == "CardInfo":
            raise ValueError("支付方式无效")

        # 检查是否有付款数据
        content_container_ele = ele
        is_hidden = content_container_ele.get_attribute("hidden")
        if is_hidden is True or is_hidden == "true" or is_hidden == "True":
            raise ValueError("没有付款数据")

        # 检查余额
        invoice_payment_balance = find_by_xpath(web_page, self.XPaths.invoice_payment_balance, timeout=50).get_text().strip()
        tmp_balance = float(re.sub(r"[^\d\.\-+]", "", invoice_payment_balance))
        
        if tmp_balance <= 0:
            raise ValueError(f"余额小于等于0，当前标准订单金额：{tmp_balance}")
        if tmp_balance < minimum_amount_float: 
            raise ValueError(f"余额小于最小提现金额，当前标准订单金额：{tmp_balance}")

        # 点击【请求付款】按钮 (发票)
        try:
            web_ele = find_by_xpath(web_page, self.XPaths.payment_request_btn21)
            web_ele.click(simulative=False)
            web_page.wait_load_completed(timeout=60)
            handle_captcha(web_page)
            # 等待网页地址变化
            for _ in Retry(timeout=50, ignore_exception=True):
                if "payments/dashboard" not in web_page.get_url():
                    break
        except Exception as e:
            if "未找到元素" in str(e): raise Exception("【请求付款】按钮不存在")
            raise

        try:
            _amazon_api.login(web_page)
        except Exception as e:
            xbot.logging.warning(f"提现后登录检查异常: {e}")

        # 新增：银行卡尾号校验
        if account_tail:  # 仅在传入了 account_tail 时才校验
            try:
                # 查找页面上的银行卡尾号元素
                page_account_tail_elem = find_by_xpath(web_page, self.XPaths.bank_account_tail, timeout=5)
                page_account_tail_text = page_account_tail_elem.get_text().strip()
                
                # 检查传入的尾号是否含在页面元素的文本中
                if account_tail not in page_account_tail_text:
                    raise ValueError(f"银行卡尾号校验失败！期望尾号: {account_tail}, 页面实际尾号: {page_account_tail_text}")
                else:
                    print(f"银行卡尾号校验成功: {account_tail}")

            except Exception as e:
                raise ValueError(e)
        
        # 判断是否能点击
        ele = find_by_xpath(web_page, self.XPaths.payment_request_btn2)
        is_disabled = ele.get_attribute("disabled") == "true"
        
        if is_disabled:
            transfer_message = self.get_displayed_transfer_message_elem().get_text()
            raise ValueError(transfer_message)

        ele.click(simulative=False)
        sleep(5)
        
        transfer_message = self.get_displayed_transfer_message_elem()
        if transfer_message.get_attribute("variant") != "success":
            transfer_message_text = transfer_message.get_text() # 修正：从消息元素获取文本
            raise ValueError(transfer_message_text)
            
        return "发票支付订单金额：" + str(tmp_balance)

    # 新：自定义类型提现（类型列表循环，返回每个类型结果字典）
    @utils.retry_processing(err_output_args=[{}], retry_time=1)
    def process_custom_payment(self, site_name, minimum_amount, account_tail, payment_types):
        web_page = self.web_page
        print(f'提现类型列表：{payment_types}')
        if site_name:
            for _, set_last_error in Retry(times=3):
                try:
                    _amazon_api.switch_site(web_page, site_name)
                    sleep(1)
                    handle_captcha(web_page)
                    break
                except Exception as e:
                    set_last_error(e)

        minimum_amount_float = float(minimum_amount)
        minimum_amount_float = 0 if minimum_amount_float < 0 else minimum_amount_float

        if not isinstance(payment_types, list):
            payment_types = [payment_types]

        result = {}
        for payment_type in payment_types:
            try:
                amount_text = self._process_custom_payment_one(web_page, minimum_amount_float, account_tail, payment_type)
                result[payment_type] = {"运行结果": True, "错误信息": "", "提现金额": amount_text}
            except Exception as e:
                result[payment_type] = {"运行结果": False, "错误信息": str(e), "提现金额": "0"}
        return result

    def _process_custom_payment_one(self, web_page, minimum_amount_float, account_tail, payment_type):
        """处理单个自定义类型的提现，成功返回金额文本，失败抛异常"""
        self.to_account_summary_page()
        sleep(1)
        handle_captcha(web_page)

        # 校验类型卡片是否存在，不存在则返回失败，避免 count=0 误定位到第一张卡片
        type_card_xpath = '//div[contains(@class,"linkable-multi-row-card-row")][.//span[contains(@class,"marketplace-name-text") and normalize-space(text())="{}"]]'.format(payment_type)
        if len(web_page.find_all_by_xpath(type_card_xpath, timeout=3)) == 0:
            raise ValueError("未找到提现类型卡片：{}".format(payment_type))

        balance_xpath = self.XPaths.custom_balance.format(payment_type)
        btn1_xpath = self.XPaths.custom_payment_btn.format(payment_type)

        name, ele = find_any_one_by_xpath(
            web_page, {
                "CardInfo": self.XPaths.CardInfo,
                "content_container": self.XPaths.content_container,
            },
            timeout=30)

        if name == "CardInfo":
            raise ValueError("支付方式无效")

        # 检查是否有付款数据
        content_container_ele = ele
        is_hidden = content_container_ele.get_attribute("hidden")
        if is_hidden is True or is_hidden == "true" or is_hidden == "True":
            raise ValueError("没有付款数据")

        # 检查余额
        balance = find_by_xpath(web_page, balance_xpath, timeout=50).get_text().strip()
        tmp_balance = float(re.sub(r"[^\d\.\-+]", "", balance))
        if tmp_balance <= 0:
            raise ValueError(f"{payment_type}余额小于等于0，当前金额：{tmp_balance}")
        if tmp_balance < minimum_amount_float:
            raise ValueError(f"{payment_type}余额小于最小提现金额，当前金额：{tmp_balance}")

        # 点击【请求付款】
        try:
            web_ele = find_by_xpath(web_page, btn1_xpath)
            web_ele.click(simulative=False)
            web_page.wait_load_completed(timeout=60)
            handle_captcha(web_page)
            # 等待网页地址变化
            for _ in Retry(timeout=50, ignore_exception=True):
                if "payments/dashboard" not in web_page.get_url():
                    break
        except Exception as e:
            if "未找到元素" in str(e): raise Exception("【请求付款】按钮不存在")
            raise

        # 处理登录跳转（login 失败不影响提现结果）
        try:
            _amazon_api.login(web_page)
        except Exception as e:
            xbot.logging.warning(f"提现后登录检查异常: {e}")

        # 银行卡尾号校验
        if account_tail:  # 仅在传入了 account_tail 时才校验
            try:
                page_account_tail_elem = find_by_xpath(web_page, self.XPaths.pay_card_end, timeout=5)
                page_account_tail_text = page_account_tail_elem.get_text().strip()
                if account_tail not in page_account_tail_text:
                    raise ValueError(f"银行卡尾号校验失败！期望尾号: {account_tail}, 页面实际尾号: {page_account_tail_text}")
                else:
                    print(f"银行卡尾号校验成功: {account_tail}")
            except Exception as e:
                raise ValueError(e)

        # 判断是否能点击
        ele = find_by_xpath(web_page, self.XPaths.payment_request_btn2)
        is_disabled = ele.get_attribute("disabled") == "true"

        if is_disabled:
            transfer_message = self.get_displayed_transfer_message_elem().get_text()
            raise ValueError(transfer_message)

        ele.click(simulative=False)
        sleep(5)

        transfer_message = self.get_displayed_transfer_message_elem()
        if transfer_message.get_attribute("variant") != "success":
            transfer_message_text = transfer_message.get_text()
            raise ValueError(transfer_message_text)

        return "{}金额：{}".format(payment_type, str(tmp_balance))



def main(args):
    web_page = xbot.web.get_active(mode="ziniaobrowser")
