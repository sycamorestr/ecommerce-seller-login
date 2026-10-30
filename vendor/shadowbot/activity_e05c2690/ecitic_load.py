# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import xbot
from xbot import print, sleep,web,win32
from .import package
from .package import variables as glv
from .orangebank_slider_captcha import deal_deal_handle_captcha
from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_click_select_captcha, std_slider_captcha

# 获取网页对象类型
def get_active_by_web_page(web_page):
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return xbot.web.get_active(mode=product_name)

def ecitic_bank_login(web_page, ai_engine:str,load_type:str, username:str, password:str, ym_token:str,drag_distance:int, use_hardware_driver_input: bool):
    """中信银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param load_type: str,登录类型
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    :param drag_distance: int, 额外滑动距离 
    """
    if not use_hardware_driver_input:
        use_hardware_driver_input = False
    
    use_hardware_driver_input = True if not use_hardware_driver_input else False

    if load_type=='个人网上银行':
    
        url = "https://i.bank.ecitic.com/perbank6/signIn.do"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)
        
        if web_page.is_element_displayed("中信银行-个人版密码控件检测"):
            result=web_page.find('中信银行-个人版密码控件检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}') 
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        # mode = get_active_by_web_page(web_page)
        # web_page = web.get_active(mode=mode, silent_running=True)   # 开启静默模式
        username_input = web_page.find("中信银行-个人版账号输入框")
        web_page.find("中信银行-个人版账号输入框").click()
        for i in range(1,4):
            username_input.input(username, simulative=True, cdp_input=True)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("中信银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=use_hardware_driver_input)
        # web_page = web.get_active(mode=mode)    # 关闭静默模式
        
        # 点击复选框
        sleep(1)
        web_page.find('中信银行-个人版复选框按钮').check()
        # 点击登录
        web_page.find('中信银行-个人版登录按钮').click()     
        # 等待
        sleep(2)
        # 判断验证码是否可见
        if web_page.is_element_displayed("中信银行-个人版验证码背景图"):
            
            deal_deal_handle_captcha(web_page = web_page,
                                    background_ele = '中信银行-个人版验证码背景图',
                                    drag_ele = '中信银行-个人版验证码滑块',
                                    gap_ele = '中信银行-个人版验证码缺口图',
                                    refresh_ele = '中信银行-个人版验证码刷新按钮',
                                    retry_count = 5,
                                    ym_token = ym_token,
                                    drag_distance = drag_distance)
        
        sleep(3)
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("中信银行-个人版登录后提示"):
            load_message = web_page.find("中信银行-个人版登录后提示内容")
            text = load_message.get_text()
            raise Exception(text)

    if load_type=='企业网上银行':
        url = "https://corp.bank.ecitic.com/cotb/login.html"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)

        if web_page.is_element_displayed("中信银行-企业版登录时候的弹窗"):
            web_page.find('中信银行-企业版登录前弹窗关闭按钮').click()

        if web_page.is_element_displayed("中信银行-企业版下载网银伴侣"):
            result=web_page.find('中信银行-企业版下载网银伴侣').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}') 
        
        # 点击切换到账号密码输入
        web_page.find('中信银行-企业版密码登录选项').click()

        if web_page.is_element_displayed("中信银行-企业版登录时候的弹窗"):
            web_page.find('中信银行-企业版登录前弹窗关闭按钮').click()

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("中信银行-企业版账号输入框")
        web_page.find("中信银行-企业版账号输入框").click()
        for i in range(1,4):
            username_input.input(username, simulative=True, cdp_input=True)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

    
        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("中信银行-企业版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=use_hardware_driver_input, force_ime_eng=True)

        # 判断有没有验证码的情况
        if web_page.is_element_displayed("中信银行-企业版验证码背景图"):
            
            web_page.find("中信银行-企业版验证码输入框").click() 
            # 识别验证码
            captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                            ele = package.selector("中信银行-企业版验证码背景图"),
                                                            captcha_type = '10103',
                                                            token = ym_token, is_trim=True, timeout=20)
            print('验证码识别结果为:',captcha_result)
            captcha_input = web_page.find("中信银行-企业版验证码输入框")    
            web_page.find("中信银行-企业版验证码输入框").click()   
            for i in range(1,4):
                captcha_input.input(captcha_result)
                text = captcha_input.get_text()
                if text == captcha_result:
                    break
                if i == 3:
                    raise Exception("验证码输入失败，请手动登录")

            # 点击登录
        web_page.find('中信银行-企业版验证码登录按钮').click()
        sleep(3)
        if web_page.is_element_displayed('中信银行_滑块背景图'):
            # deal_deal_handle_captcha(web_page=web_page, background_ele=package.selector('中信银行_滑块背景图'), slider_ele=package.selector('中信银行_拖拽元素'), retry_count=1, refresh_elem=package.selector('中信银行_刷新元素'))
            deal_deal_handle_captcha(web_page = web_page,
                                    background_ele = '中信银行_滑块背景图',
                                    drag_ele = '中信银行_拖拽元素',
                                    gap_ele = '中信银行-缺口元素',
                                    refresh_ele = '中信银行_刷新元素',
                                    retry_count = 5,
                                    ym_token = ym_token,
                                    drag_distance = drag_distance)
        sleep(3)
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("中信银行-企业版登录之后的提示"):
            load_message = web_page.find("中信银行-企业版登录之后的提示内容")
            text = load_message.get_text()
            raise Exception(text)
        
        

def main(args):
    web_page = args.get('web_page',web.get_active(mode='chrome'))
    # web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get("load_type", "个人网上银行")
    username = args.get("username", "@qq.com")
    password = args.get("password", "1212")
    ym_token = args.get("ym_token", "")
    drag_distance = args.get("drag_distance")
    use_hardware_driver_input = args.get("use_hardware_driver_input", False)
    ecitic_bank_login(web_page,ai_engine,load_type,username,password,ym_token,drag_distance=drag_distance,use_hardware_driver_input=use_hardware_driver_input)
