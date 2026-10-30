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


# 滚动表格元素
def see_element(web_page, xpath):
    """将指定列滚动到可视页面底部"""
    script = """
        function (element, input) {
            element.scrollIntoView({ behavior: 'smooth', block: 'end'});
        }
    """
    web_page.find_by_xpath(xpath).execute_javascript(script)


def copy_new_goods(web_page, two_info_list, station, create_or_save):
    """复制商品上新"""

    if not two_info_list:
        return 

    for _ in range(3):
        # 判断当前操作页面是否为目标页面
        url = web_page.get_url()
        if '/goods/list' not in url:
            # 获取网页域名
            domain_url = Tools.get_domain_from_url(url)
            # 进行网页跳转
            web_page.navigate(f'{domain_url}/goods/list')
        else:
            break   # 跳转到正确页面退出循环
    
    # 获取网站名称
    product_name = Tools.get_web_page_product_name(web_page)

    # 等待数据加载完毕
    Tools.wait_loading(web_page, 60)

    # 注入js消除遮挡
    AD_XPATH = '//div[@data-testid="beast-core-portal-main"]'
    ads = Tools.gen_selector(AD_XPATH)
    ads_appear = web_page.wait_appear(ads, timeout=1)
    if ads_appear:
        dis = """
        function hideAds(context, args) {
            document.querySelectorAll('[data-testid="beast-core-portal-main"]')
                    .forEach(el => el.style.display = args);
        }
        """
        web_page.execute_javascript(dis, "none")
    sleep(0.5)

    for info_list in two_info_list:
        skc_id = info_list[0]
        declare_value = info_list[1]
        inventory = info_list[2]

        web_page = xbot.web.get_active(mode='auto')

        # 通过skc id查找商品
        SKC_input_frame_xpath = '//div[text()="商品ID查询"]/following-sibling::div//input[@placeholder="多个查询请空格或逗号依次输入"]'
        web_page.find_by_xpath(SKC_input_frame_xpath).input(skc_id)

        # 点击进行查询
        query_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[text()="查询"]'
        web_page.find_by_xpath(query_xpath).click()

        # 等待网页加载完毕
        Tools.wait_loading(web_page, over_time=60)

        # 等待数据加载完毕
        loading_xpath = '//div[contains(@class,"TB_loading")]'
        loading_sel = Tools.gen_selector(loading_xpath)
        if web_page.wait_appear(loading_sel, timeout=3):
            web_page.wait_disappear(loading_sel, timeout=60) 

        # 获取行信息
        target_tr_xpath = '((//tbody[@data-testid="beast-core-table-middle-tbody"])/tr)[1]'
        # see_element(web_page, target_tr_xpath)
        target_tr_ele = web_page.find_by_xpath(target_tr_xpath)

        # 获取该行的td信息
        tds = target_tr_ele.find_all_by_xpath('./td')

        if len(tds) > 14:
            # 判断是否有复制到其他站点信息
            if len(tds[-1].find_all_by_xpath('.//span[text()="复制到其他站点"]'))>0:
                tds[-1].find_by_xpath('.//span[text()="复制到其他站点"]').click()
                
                # 输入站点名称
                station_input_xpath = '//div[text()="将该商品复制到："]/following-sibling::div//input[@placeholder="请选择"]'
                web_page.find_by_xpath(station_input_xpath).input(station)        
                # 进行回车
                xbot.win32.send_keys('{enter}')

                # 点击确定
                confirm_xpath = '//button[@data-testid="beast-core-modal-ok-button"]/span[text()="确认"]'
                web_page.find_by_xpath(confirm_xpath).click()

                # 激活新打开的页面
                web_page2 = xbot.web.get_active(mode='auto')

                # 等待页面加载完毕
                Tools.wait_loading(web_page, over_time=60)

                # 判断遮挡物是否存在，存在则注入js进行消除
                rubbish_xpath = '//div[@data-testid="beast-core-portal-main"]'
                rubbish_sel = Tools.gen_selector(rubbish_xpath)
                if web_page2.wait_appear(rubbish_sel, timeout=2):
                    # 注入js代码进行消除
                    dis = """
                    function hideAds(context, args) {
                        document.querySelectorAll('[data-testid="beast-core-portal-main"]')
                                .forEach(el => el.style.display = args);
                    }
                    """
                    web_page.execute_javascript(dis, "none")

                #获取表格中的所有行
                inner_trs = web_page2.find_all_by_xpath('//label[text()="SKU 信息"]/../../..//tbody/tr')

                # 循环每行对价格进行修改
                for inner_tr in inner_trs:
                    # 获取所有列
                    inner_tds = inner_tr.find_all_by_xpath('./td')

                    if len(inner_tds) == 9:
                        # 找到价格输入框，进行价格修改
                        goods_value = inner_tds[3].find_by_xpath('.//input').input(declare_value)
                    else:

                        # 找到价格输入框，进行价格修改
                        goods_value = inner_tds[2].find_by_xpath('.//input').input(declare_value)
                
                # 进行存储管理
                inner_trs[-1].find_by_xpath('./td[4]//span/following-sibling::*').click()

                # 等待页面稳定
                inventory_frame_xpath = '//div[@data-testid="beast-core-modal"]'
                inventory_frame_sel = Tools.gen_selector(inventory_frame_xpath)
                if web_page.wait_appear(inventory_frame_sel, timeout=5):
                    sleep(5)

                #选择站点仓库
                station_store = web_page2.find_by_xpath('(//th[text()="覆盖站点"]/../../tbody)[1]//input').click()

                # 点击全选
                web_page2.find_by_xpath('//ul[@role="listbox"]//div[text()="全选"]').click()

                # 进行库存输入
                web_page2.find_by_xpath('//div[text()="当前库存"]/following-sibling::div//input').input(inventory)

                # 点击批量填写
                web_page2.find_by_xpath('//div[text()="当前库存"]/../..//span[text()="批量填写"]').click()

                # 进行确认
                web_page2.find_by_xpath('//div[contains(@class,"MDL_bottom")]//span[text()="确认"]').click()

                # 等待库存填写框消失
                web_page2.wait_disappear(inventory_frame_sel)

                if create_or_save == '创建':
                    web_page2.find_by_xpath('//span[text()="创建"]').click()
                else:
                    web_page2.find_by_xpath('//span[text()="保存草稿"]').click()

                # 点击确定
                OK_button_xpath = '//div[contains(@class,"MDL_footer")]//span[text()="确认"]'
                web_page.find_by_xpath(OK_button_xpath).click()

                # 等待成功信息出现
                success_info_xpath = '//div[contains(@class,"product-create_tips")]'
                success_info_sel = Tools.gen_selector(success_info_xpath)
                if web_page2.wait_appear(success_info_sel):
                    # 成功则关闭当前网页
                    web_page2.close(ignore_beforeunload=True)
            else:
                break


def test():
    "测试模块"
    if 'xbot_extensions' in __file__:
        return 
    web_page = xbot.web.get_active(mode='chrome')
    two_info_list = [['48016447387', '150', '50'], ['66336313795', '149', '30']]
    station = '美国站'
    create_or_save = '保存草稿'
    copy_new_goods(web_page, two_info_list, station, create_or_save)
    
    exit()

def main(args):

    # 测试模块
    # test()

    # 功能模块
    web_page = args.get('web_page')
    two_info_list = args.get('two_info_list')
    station = args.get('station', '美国站')
    create_or_save = args.get('create_or_save', '保存草稿')

    copy_new_goods(web_page, two_info_list, station, create_or_save)