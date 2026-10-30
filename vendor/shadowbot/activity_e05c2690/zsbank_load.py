# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用流程"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv

def zs_bank_load(web_page, username:str, login_password:str, certificate_password:str):
    """招商银行登录，企业银行证书用户登录
    :param web_page: , 网页对象
    :param login_password: str, 登录密码
    :param certificate_password: str, 证书密码
    """
    url = "https://u.ebank.cmbchina.com/CmbBank_FB/UI/Login/FBPOPLogin.aspx"
    web_page.navigate(url,load_timeout=40)

    certificate_login_btn = web_page.find_by_xpath('//span[@id="spanKey"]')
    certificate_login_btn.click()
    sleep(2)

    try:
        service_status_item = web_page.find_by_xpath('//div[@id="UBankServiceStatus"]', timeout=3)
        service_status_text = service_status_item.get_text()
        print(f'当前状态为：{service_status_text}')
    except:
        pass

    username_input = web_page.find_by_xpath('//input[@id="U_BankUser_Ctrl"]')
    username_input.click()
    for i in range(1,4):
        username_input = web_page.find_by_xpath('//input[@id="U_BankUser_Ctrl"]')
        username_input.input(username)
        text = username_input.get_text()
        if text == username:
            break
        if i == 3:
            raise Exception("输入失败，请手动登录")

    login_password_input = web_page.find_by_xpath('//input[@id="U_BankPwd"]')
    login_password_input.click()
    win32.send_keys(login_password,hardware_driver_input=True)
    sleep(2)
    
    certificate_password_input = web_page.find_by_xpath('//input[@id="U_BankCertPwd"]')
    certificate_password_input.click()
    win32.send_keys(certificate_password,hardware_driver_input=True)
    sleep(2)

    login_btn = web_page.find_by_xpath('//button[@id="LoginBtn"]')
    login_btn.click()



def test_func():
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active('chrome')
    username = ''
    login_password = ''
    certificate_password = ''
    zs_bank_load(web_page, username, login_password, certificate_password)
    exit()

def main(args):
    test_func()
    web_page = args.get('web_page')
    username = args.get('username')
    login_password = args.get('login_password')
    certificate_password = args.get('certificate_password')
    zs_bank_load(web_page, username, login_password, certificate_password)

