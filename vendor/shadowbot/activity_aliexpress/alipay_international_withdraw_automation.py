# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot import web
import re
from .utils import gen_selector
from datetime import datetime,date
from decimal import Decimal

def alipay_global_withdraw(web_page:xbot.web.WebBrowser, internation_alipay_accunt:str,  limited_amount:str, international_alipay_password:str ,payee_information:str):
    """
    国际支付宝提款
    :param web_page: xbot.web.WebBrowser,  网页对象
    :param order_status: str, 订单状态文本
    """
    try:
        # 获取可用金额
        available_xpath = '//div[contains(@class, "ant-col")]/div[contains(@class, "f30")]'
        avaliable_count = web_page.find_by_xpath(available_xpath).get_text()
        pattern = r'\d{1,3}(?:,\d{3})*\.?\d*'
        avaliable_count = re.search(pattern,avaliable_count)
        avaliable_count = avaliable_count.group().replace(',','')
        xbot.logging.info(f"可用余额为：{avaliable_count}")
        if float(avaliable_count) < int(limited_amount):
            raise Exception ("可用余额小于指定金额的限制，不能进行提款")

        # 点击转账
        withdraw_click = '//button[contains(@class, "mr8")]'
        web_page.find_by_xpath(withdraw_click).click(delay_after=2)

        # 等待转账页面加载成功
        wait_zhuangzhang_xpath = '//div[contains(@class, "ant-card-head-title")]'
        web_page.wait_appear(gen_selector(wait_zhuangzhang_xpath),timeout=30)
        # 强制等待3秒
        sleep(3)
        
        # 等待支付宝国际账户
        xpath = '//div/section/*[local-name()="h5"][normalize-space(.)="转至支付宝国际（Alipay Business）账号"]'
        # 判断是否存在国际支付宝账户
        xpath_sel = web_page.find_all_by_xpath(xpath)
        # 判断是否存在第二个更新是否存在
        if xpath_sel:  # 只有当找到元素时才执行
            visible_elements = [_ for _ in xpath_sel if _.get_bounding(to96dpi=False)[3] != 0]
            if visible_elements:
               # 如果有可见的元素
                xpath_display = visible_elements[0]
                web_page.find_by_xpath(xpath).click(delay_after=2)
                sleep(2)  # 普通等待
            else:
                # 选择账户类型
                account_stype = '//form//div[contains(@class, "ant-select-lg")][contains(@class, "collectSelect")]/div[contains(@class, "ant-select-selector")]'
                web_page.find_by_xpath(account_stype).click(delay_after=2)
                web_page.find_by_xpath(xpath).click(delay_after=2)

        # 选择处理货币类型
        currency_stype = '//div/form/div[1]//div[contains(@class, "ant-select-lg")]//span[contains(@class, "ant-select-selection-item")]'
        web_page.find_by_xpath(currency_stype).click(delay_after=2)
        # 人民币
        CNY_xpath = '//div[1][contains(@class, "ant-select-item-option-selected")]/div[contains(@class, "ant-select-item")]'
        web_page.wait_appear(gen_selector(CNY_xpath),timeout=20)
        sleep(1)
        web_page.find_by_xpath(CNY_xpath).click(delay_after=2)

        # 输入国际支付宝账号
        internation_alipay_accunt_xpath = '//form//input[@id="accountNo"]'
        web_page.find_by_xpath(internation_alipay_accunt_xpath).input(internation_alipay_accunt,simulative=True)

        # 点击下一步
        next_step_xpath = '//form//button[normalize-space(.)="下一步"]'
        web_page.find_by_xpath(next_step_xpath).click(delay_after=2)
        
        # 等待转账金额出现
        transfer_amount_xpath ='//form//label[normalize-space(.)="可转账金额"]'
        web_page.wait_appear(gen_selector(transfer_amount_xpath),timeout=20)

        # 获取转账具体金额
        transfer_amount = Decimal(avaliable_count) - Decimal(str(limited_amount))
        xbot.logging.info(f"具体转账金额未：{transfer_amount}")
        transfer_amount_xpath = '//form//input[@role="spinbutton"]'
        web_page.find_by_xpath(transfer_amount_xpath).input(float(transfer_amount), simulative=True)

        # 获取当前日期,并格式化
        current_date = date.today()
        formatted_date = current_date.strftime('%Y-%m-%d')
        date_xpath = '//form//input[@id="remarks"]'
        web_page.find_by_xpath(date_xpath).input(formatted_date,simulative=True)

        # 点击下一步
        next_step_xpath = '//form//button[normalize-space(.)="下一步"]'
        web_page.find_by_xpath(next_step_xpath).click(delay_after=2)

        # 等待确认转账信息也页面
        wait_page = '//form//input[@type="password"]'
        web_page.wait_appear(gen_selector(wait_page),timeout=20)

        # 获取收款人信息
        person_message_xptah = '(//table//tr/td[contains(@class, "descriptions-item-content")])[5]'
        person_message = web_page.find_by_xpath(person_message_xptah).get_text()
        print("账户信息:", person_message)

        # 清理账户信息 - 移除所有特殊符号和空格
        cleaned_person_message = re.sub(r'[^\w]', '', person_message)  # 只保留字母数字
        print("清理后的账户信息:", cleaned_person_message)

        # 清理输入的收款人信息
        cleaned_payee_information = re.sub(r'[^\w]', '', payee_information)
        print("清理后的输入收款人信息:", cleaned_payee_information)

        # 收款人账号信息
        person_username_message_xptah = '(//table//tr/td[contains(@class, "descriptions-item-content")])[6]'
        person_uername_message = web_page.find_by_xpath(person_username_message_xptah).get_text()
        print("收款人完整信息:", person_uername_message)

        # 正确提取邮箱 - 匹配到中文前停止
        pattern2 = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        person_uername_message_emails = re.findall(pattern2, person_uername_message)

        # 检查信息是否能够对应 - 使用清理后的信息进行比较
        if (cleaned_person_message == cleaned_payee_information and 
            person_uername_message_emails[0] == internation_alipay_accunt):
            # 输入国际支付宝密码
            input_password_xpath = '//form//input[@type="password"]'
            web_page.find_by_xpath(input_password_xpath).input(international_alipay_password, simulative=True)

            # 确定转账
            enter_xpath = '//form//button[normalize-space(.)="确 认"]'
            web_page.find_by_xpath(enter_xpath).click()
            
            error_msg_xpath = '//div[normalize-space(.)="支付密码错误"][@class="ant-message-notice-content"]'
            if web_page.is_element_displayed(gen_selector(error_msg_xpath)):
                raise Exception("输入密码错误")
            xbot.logging.info("信息验证通过，执行转账操作")
            
        else:
            error_msg = "信息验证失败，不执行转账"
            print(error_msg)
            print(f"账户信息匹配: {cleaned_person_message == cleaned_payee_information}")
            print(f"邮箱匹配: {person_uername_message_emails[0] == internation_alipay_accunt}")
            
    except Exception as e:
        error_msg = f"国际支付宝提款过程中发生错误: {str(e)}"
        xbot.logging.error(error_msg)


def test_alipay_global_withdraw():
    """
    测试订单导出功能
    """
    if "xbot_extensions" in __file__:
        return

    web_page = web.get_active(mode='edge')
    internation_alipay_accunt = '309368134@qq.com'
    limited_amount = '1000'
    payee_information = 'Hong Kong Wenyi Technology Co.,Limited'
    international_alipay_password = ''
    
    # 修正：使用正确的参数顺序
    result = alipay_global_withdraw(
        web_page, 
        internation_alipay_accunt, 
        limited_amount, 
        international_alipay_password, 
        payee_information
    )
    web_page.close()
    exit()

def main(args):
    # 调用测试函数功能
    test_alipay_global_withdraw()
    web_page = args.get('web_page')
    internation_alipay_accunt = args.get('internation_alipay_accunt')
    limited_amount = args.get('limited_amount')
    payee_information = args.get('payee_information')
    international_alipay_password = args.get('international_alipay_password')
    
    # 调用主函数功能
    result = alipay_global_withdraw(
        web_page, 
        internation_alipay_accunt, 
        limited_amount, 
        international_alipay_password,
        payee_information
    )