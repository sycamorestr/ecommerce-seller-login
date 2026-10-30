# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import re
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from . import _amazon_api
from .utils import print, find_any_one_by_xpath, handler_container
from .activities_utils import download_handler
from .create_element import create_selector_shadow


def to_account_summary_page(web_page):
        """进入账户一览页面"""
        assert isinstance(web_page, xbot.web.WebBrowser)
        path = "/payments/dashboard/index.html/ref=xx_payments_foot_xx"
        if path in web_page.get_url():
            return
        domain = web_page.execute_javascript("() => origin")
        url = "{}{}".format(domain, path)
        web_page.navigate(url, load_timeout=30)
        handler_container(web_page)
        _amazon_api.login(web_page)

def proceeds_screenshot(web_page, site_name, save_dir, save_name, cycle="0", account_type="", screenshot_range=""):
    """结算一览PDF下载"""
    # ============ XPath 定义（函数内） ============
    _xpaths = {
        "CardInfo": '''(//*[@id="go-to-credit-card-info"])[1]''',
        "content_container": '''//div[contains(@class, "dashboard-content-container")]''',
        "currency_total_amount": '''//div[@class="currency-total-amount"]''',
    }
    cycle = int(cycle)

    value_dic = {
        '标准订单': 'PAYABLE',
        '发票支付订单': 'INVOICING',
        '全部（联合报告）': 'ALL',
        'Visa信用卡': 'CC_VISA',
        '万事达信用卡及其他': 'PAYABLE',
        '美国运通卡': 'CC_AMERICAN_EXPRESS',
        'Elo': 'CC_ELO',
        'DinersClub': 'CC_DINERS_CLUB',
        'Visa借记卡': 'DC_VISA',
        'MasterCard借记卡': 'DC_MASTERCARD',
        'Boleto': 'BOLETO'
    }

    try:
        # 参数校验
        assert save_dir != "" and os.path.exists(
            save_dir), f"文件夹不存在 - {save_dir}"
        web_page: xbot.web.WebBrowser = web_page

        _amazon_api.switch_site(web_page, site_name)

        to_account_summary_page(web_page)

        # //kat-label[@text="结算周期"]/following-sibling::*[1]

        name, ele = find_any_one_by_xpath(
            web_page, {
                "CardInfo": _xpaths["CardInfo"],
                "content_container": _xpaths["content_container"],
            },
            timeout=30)

    

        content_container_ele = web_page.find_by_xpath(_xpaths["content_container"])
        is_hidden = content_container_ele.get_attribute("hidden")

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
            account_dropdown_xpath = '//div[@class="account-type-selection"]//kat-dropdown'
            web_page.find_by_xpath(account_dropdown_xpath).click()
            account_type_xpath  = '//div[@class="account-type-selection"]//kat-dropdown/xbotShadowRoot//kat-option[@value="{}"]'
            account_type = re.sub(r'\s+', '', account_type)
            account_value = value_dic[account_type]
            account_xpath = create_selector_shadow(account_type_xpath.format(account_value))
            web_page.find(account_xpath).click()
                
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
                save_name = f"{site_name}-{target_ele.get_text().replace('/','-').replace(' ','')}.PDF"
        web_page.wait_load_completed(100)
        
        # 进行打印操作
        web_page.find('打印按钮').click()
        sleep(3)
        xbot.win32.send_keys('{ENTER}')
        file_path = download_handler(web_page, save_dir, save_name)
        return file_path
    except Exception as e:
        print(e)
        return 


def test():
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active('ziniaobrowser')
    save_dir = r'D:'
    site_name = '美国'
    save_name = ''
    cycle='1'
    account_type='发票支付订单'
    proceeds_screenshot(web_page,site_name,save_dir,save_name,cycle,account_type)

    exit()

def main(args):
    test()
    web_page = args.get("web_page")
    site_name = args.get('site_name')
    save_dir = args.get('save_dir')
    save_name = args.get('save_name', '')
    cycle = args.get('cycle') or 0
    account_type = args.get('account_type') or '标准订单'
    file_path = proceeds_screenshot(web_page, site_name, save_dir, save_name, cycle, account_type)
    args['file_path'] = file_path
