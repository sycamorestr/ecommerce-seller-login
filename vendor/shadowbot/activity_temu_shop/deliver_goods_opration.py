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

def excute_operation(web_page:xbot.web.WebBrowser, orders_num, ready_type):
    if ready_type == "普通备货建议":
        xpath = '//*[@data-testid="beast-core-tab-itemLabel-wrapper"]//div[text()="普通备货建议"]'
        web_page.find_by_xpath(xpath ).click()
        diliver_button = web_page.find_by_xpath("//*[text()='快速筛选']//following-sibling::div//*[contains(text(),'今日可发货')]")
        if len(diliver_button.parent().children()) <= 2:
            diliver_button.click()
    else:
        xpath = '//*[@data-testid="beast-core-tab-itemLabel-wrapper"]//div[text()="紧急备货建议"]'
        web_page.find_by_xpath(xpath ).click()
        web_page.find_by_xpath(f"//div[contains(@data-testid,'tab-itemLabel')]//div[text()='{ready_type}']").click()
    try:
        web_page.find_by_xpath("//div[text()='暂无数据']", timeout=2)
        print("该店铺暂无商品需要操作")
        return
    except:
        input_elem = web_page.find_by_xpath("//div[text()='备货单号']//following-sibling::div//input")
        if isinstance(orders_num, list):
            data = ",".join(orders_num)
            input_elem.input(data)
        elif orders_num == '全部' or orders_num == None or orders_num == '':
            pass
        else:
            input_elem.input(orders_num)
        web_page.find_by_xpath("//li[text()='每页']//div[@data-testid='beast-core-select']").click()
        web_page.find_by_xpath("//span[text()='100']").click()
        web_page.find_by_xpath("//span[text()='查询']").click()
        sleep(3)
        select_all = web_page.find_by_xpath("//*[text()='备货单号']/..//preceding-sibling::th//label")
        if select_all.get_attribute("data-checked") == 'false':
            select_all.click()
        try:
            web_page.find_by_xpath("//*[text()='批量加入发货台' and not(../@disabled)]", timeout=3).click()

            try:
                web_page.find_by_xpath("//span[text()='继续发货']", timeout=3).click()
            except:
                pass
        
            web_page.find_by_xpath("//*[text()='确认']").click()
        except:
            return False

def deliver_opration(web_page, retry_time, orders_num, ready_type):
    Tools.check_web(web_page, '/stock/fully-mgt/')
    for retry_count in range(retry_time):
        add_res = excute_operation(web_page, orders_num, ready_type)
        if not add_res:
            return "本次加入发货台中含有不可添加的商品或无商品，请检查"
        try:
            failure_list = web_page.find_all_by_xpath("//*[contains(text(),'以下备货单加入发货台失败')]//following-sibling::div//*[contains(text(),'请稍后重试')]",timeout=2)
            if len(failure_list) > 0:
                web_page.reload()
            else:
                orders = web_page.find_all_by_xpath("//div[@data-testid='beast-core-modal-inner']//tbody//td[1]")
                failure = web_page.find_all_by_xpath("//div[@data-testid='beast-core-modal-inner']//tbody//td[2]")
                order_failure_dict = {order.text.strip(): fail.text.strip() for order, fail in zip(orders, failure)}
                return order_failure_dict
        except:
            return
    if retry_count == retry_time-1:
        return "达到最大重试次数了， 依旧有商品添加失败"

def main(args):
    
    web_page = args.get("web_page")
    retry_time = args.get("retry_time", 3)
    # web_page = web.get_active(mode='chrome')
    orders_num = args.get("orders_num", '')
    ready_type = args.get("ready_type", "紧急备货建议")

    result = deliver_opration(web_page, retry_time, orders_num, ready_type)
    args['result'] = result
