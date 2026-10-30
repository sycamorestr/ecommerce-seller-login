# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import Tools

def rejuct_adjust_prices(web_page, reason):
    """包含两种情况:
            一:单个拒绝需要填理由
            二:多个拒绝不需要理由
        每次拒绝后都需要刷新显示
    """
    target_url = 'https://agentseller.temu.com/main/adjust-price-manage/order-price'
    try:
        url = web_page.get_url()
        if url != target_url:
            web_page.navigate(target_url)
    except Exception as e:
        print(f"check_web报错：{e}")
        return None
    # 等待待卖家确认出现
    confirm_sel = Tools.gen_selector("//*[contains(text(),'待卖家确认')]")
    web_page.wait_appear(confirm_sel)
    # Tools.check_web(web_page, 'main/adjust-price-manage/order-price')
    web_page.find_by_xpath("//*[contains(text(),'待卖家确认')]").click()
    while 1:
        web_page.find_by_xpath("//li[text()='每页']/div").click()
        web_page.find_by_xpath("//ul[@role='listbox']/li[last()]").click()
        try:
            web_page.find_by_xpath("//div[text()='暂无数据']", timeout=2)
            print("该店铺已完成需要调价的商品")
            return
        except:
            try:
                web_page.find_by_xpath("//tbody[contains(@data-testid,'middle-tbody')]/tr[1]//*[text()='拒绝']", timeout=2).click()
                try:
                    web_page.find_by_xpath("//*[text()='拒绝原因']//ancestor::p//following-sibling::div//textarea", timeout=2).input(reason)
                    web_page.find_by_xpath("//button/span[text()='拒绝']").click()
                except:
                    [item.click() for item in web_page.find_all_by_xpath("//*[contains(text(),'多个待确认调价单')]/..//tbody/tr//*[text()='我不接受']", timeout=2)]
                    web_page.find_by_xpath("//button/span[text()='确认']").click()
            except:
                web_page.find_by_xpath("//tbody[contains(@data-testid,'middle-tbody')]/tr[1]//*[text()='不调整']").click()
                try:
                    web_page.find_by_xpath("//*[contains(@placeholder, '请输入不调整原因')]", timeout=2).input(reason)
                    web_page.find_by_xpath("//button/span[text()='确认']").click()
                except:
                    [item.input(reason) for item in web_page.find_all_by_xpath("//*[contains(@placeholder, '请输入原因')]", timeout=2)]
                    web_page.find_by_xpath("//button/span[text()='确认']").click()
            sleep(2)

def main(args):
    
    web_page = args.get("web_page")
    reason = args.get("reason", "商品没有利润空间，已申报营销活动")
    # web_page = web.get_active(mode='chrome')
    rejuct_adjust_prices(web_page, reason)

