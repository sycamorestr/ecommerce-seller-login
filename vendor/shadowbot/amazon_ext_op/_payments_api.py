from ._payments_core import ReportsHandler, PaymentsHandler



def reports_download(web_page, site_name, account_type, report_type, report_tag, date_range, save_dir, save_name, wait_time):
    """报告库文件按下载"""

    reports_handler = ReportsHandler(web_page)
    return reports_handler.run(site_name, account_type, report_type, report_tag, date_range, save_dir, save_name, wait_time)
    

def payment_request(web_page, site_name, minimum_amount,is_comma_decimal):
    """自动提现"""
    payments_handler = PaymentsHandler(web_page)
    return payments_handler.payment_request(site_name, minimum_amount,is_comma_decimal)

#新：自动提现拆分
def process_standard_payment(web_page, site_name, minimum_amount,account_tail):
    """标准订单"""
    payments_handler = PaymentsHandler(web_page)
    return payments_handler.process_standard_payment(site_name, minimum_amount,account_tail)

#新：自动提现拆分-自定义类型
def process_custom_payment(web_page, site_name, minimum_amount, account_tail, payment_types):
    """自定义类型提现，payment_types 为中文类型名列表（如：["标准订单","发票支付订单","Visa 信用卡"]），返回每个类型的结果字典"""
    payments_handler = PaymentsHandler(web_page)
    return payments_handler.process_custom_payment(site_name, minimum_amount, account_tail, payment_types)

def process_invoice_payment(web_page, site_name, minimum_amount,account_tail):
    """发票支付订单"""
    payments_handler = PaymentsHandler(web_page)
    return payments_handler.process_invoice_payment(site_name, minimum_amount,account_tail)


def proceeds_screenshot(web_page, site_name, save_dir, save_name, cycle, account_type, screenshot_range):
    """结算一览截图"""
    payments_handler = PaymentsHandler(web_page)
    return payments_handler.proceeds_screenshot(site_name, save_dir, save_name, cycle, account_type, screenshot_range)


def get_account_data(web_page, site_name, account_type, cycle, switch_zh):
    """抓取结算一览账户数据"""
    payments_handler = PaymentsHandler(web_page)
    return payments_handler.get_account_data(site_name, account_type, cycle, switch_zh)

