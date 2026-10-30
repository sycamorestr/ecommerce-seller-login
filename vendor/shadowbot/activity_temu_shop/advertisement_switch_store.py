# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import Tools


def switch_store(web_page, target_store_name):
    """广告平台-切换店铺"""
    
    # 获取店铺名称, 判断店铺是否为目标店铺
    shop_name_xpath = '//div[@id="top-bar"]//span[.="返回卖家中心"]/../../../div[last()]//div[not(div)]'
    try:
        if web_page.find_by_xpath(shop_name_xpath, timeout=2).get_text() == target_store_name:
            print(f'{target_store_name} 店铺切换成功')
            return      # 若店铺为目标店铺则退出，不进行切换
    except:
        pass

    # 切换店铺逻辑

    # 没有切换按钮
    if len(web_page.find_all_by_xpath("//*[text()='切换']", timeout=2)) == 0:
        web_page.find_by_xpath(shop_name_xpath).click()
    
    # 一个切换按钮点击展开店铺
    if len(web_page.find_all_by_xpath("//*[text()='切换']", timeout=2)) == 1:
        web_page.find_by_xpath("//*[text()='切换']").click()

    # 多个切换按钮，查找目标店铺
    # 获取所有的店铺
    all_store_xpath = '//*[.="切换店铺"]/../div[2]/div/div/div//span[not(.="半托管")]'
    all_store_sel = web_page.find_all_by_xpath(all_store_xpath)

    # 循环所有的店铺进行判断
    for store_sel in all_store_sel:
        if store_sel.get_text() == target_store_name:
            store_sel.click()
            break
    else:
        raise Exception(f'未找到该店铺 {target_store_name}')

    # https://ads.temu.com/login.html
    if 'login' in web_page.get_url():
        # 同意授权svg
        svg_xpath = '//span[contains(text(),"我已阅读并同意")]/preceding-sibling::label//*[name()="svg"]'

        # 授权后点击的按钮
        button_xpath = '//span[contains(text(),"我已阅读并同意")]/../following-sibling::div/div[@role="button"]'

        # 循环判断是否还有弹窗出现
        while True:
            # 进行svg和button的点击
            try:
                web_page.find_by_xpath(svg_xpath, timeout=1).click()
                web_page.find_by_xpath(button_xpath, timeout=1).click()
                sleep(1)
            except:
                pass

            not_main_xpath = '//div[text()="请切换主账号签署协议"]'
            not_main_sel = Tools.gen_selector(not_main_xpath)
            if web_page.wait_appear(not_main_sel, timeout=3):
                raise Exception('请切换主账号签署协议')
            
            # 获取网页信息，若为首页则退出
            if 'login.html' not in web_page.get_url():
                break
    
    # 进行校验，判断店铺是否切换成功
    try:
        if web_page.find_by_xpath(shop_name_xpath, timeout=2).get_text() != target_store_name:
            raise Exception(f'{target_store_name} 店铺切换失败')
        else:
            print(f'{target_store_name} 店铺切换成功')
            return
    except:
        pass
    

def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return 
    
    web_page = xbot.web.get_active(mode='superbrowser')
    target_store_name = 'HOTU HOME LIFE'
    switch_store(web_page, target_store_name)

    exit()

def main(args):
    # 测试功能
    # test()

    web_page = args.get('web_page')
    target_store_name = args.get('store_name')

    switch_store(web_page, target_store_name)