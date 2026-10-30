# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv


def get_shop_list(web_page):
    """获取店铺列表"""
    # web_page.find_by_xpath("//div[@class='agentseller-userinfo']", timeout=2).click()
    # 如果已经点击切换, 就会找到多个切换按钮
    switch_num = web_page.find_all_by_xpath("//*[text()=' 切换' or text()='切换']",timeout=2)
    switch_num_list = [_ for _ in switch_num if _.get_bounding(to96dpi=False)[2] != 0]
    if len(switch_num_list) == 0:
        try:
            web_page.find_by_xpath("//div[contains(@class,'account-info_accountInfo')] | //div[@class='agentseller-userinfo']", timeout=2).click()
        except:
            web_page.find_by_xpath('(//div[contains(@class,"Space_alignCenter")]/div[2])[1]').click()
    
    # 第一个切换
    if len(web_page.find_all_by_xpath("//*[text()='切换']", timeout=1)) == 1:
        web_page.find_by_xpath("//*[text()='切换']").click()

    # 第二个切换
    if len(web_page.find_all_by_xpath("//*[text()=' 切换']", timeout=1)) == 1:
        web_page.find_by_xpath("//*[text()=' 切换']").click()

    # 获取店铺列表信息
    shop_list = """
        //div[contains(@class,"account-info_renderMallList")]//span[@data-testid="beast-core-ellipsis"]/span
        |
        //*[normalize-space(text())='切换']/preceding-sibling::div[1]
        |
        //*[contains(@class,"account-info_switchSection")]//div[contains(@class,"account-info_mallName")]
        |
        //*[@class="rocket-modal-header"][.//div[text()="切换店铺"]]/following-sibling::div//span[contains(@class,"item_name")]
    """
    shop_list_sel = web_page.find_all_by_xpath(shop_list)
    shop_list_name = [_.get_text().replace("半托管", "").strip() for _ in shop_list_sel]

    try:
        # 关闭店铺列表
        close_xpath = """
            //div[contains(@class,"account-info_userInfo")]//div[contains(@class,"account-info_accountInfo")]
            |
            //div[contains(@data-testid,"innerWrapper")]//*[local-name()="svg"][contains(@data-testid,"close")]
            |
            //*[@class="rocket-modal-header"][.//div[text()="切换店铺"]]/..//*[contains(@class,"close-x")]
        """
        web_page.find_by_xpath(close_xpath).click()
    except:
        pass

    return shop_list_name


def test():
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active('chrome')
    name = get_shop_list(web_page)
    print(name)
    exit()

def main(args):
    test()
    web_page = args.get('web_page')
    shop_list = get_shop_list(web_page)
    args['shop_list'] = shop_list
