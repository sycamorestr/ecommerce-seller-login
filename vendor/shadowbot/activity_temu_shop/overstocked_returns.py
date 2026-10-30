# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re
import math 

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import Tools


def ADS_hidden(web_page):
    # 消除消息框
    AD_xpath = '//div[@data-testid="beast-core-portal-main"]'
    AD_sel = Tools.gen_selector(AD_xpath)
    if web_page.wait_appear(AD_sel, timeout=3):
        dis = """
        function hideAds(context, args) {
            document.querySelectorAll('[data-testid="beast-core-portal-main"]')
                    .forEach(el => el.style.display = args);
        }
        """
        web_page.execute_javascript(dis, "none")
        sleep(0.5)


def overstocked_returns(
    web_page : any, 
    onner_list : list,
    start_station_time : str, 
    end_station_time : str, 
    sku_inventroy : str,
    product_state : list,
    start_sales : str,
    end_sales : str,
    date_time : str,
    apply_reason : str,
    ):
    """滞留退货"""

    # 设置SKC_ID列表
    SKC_ID_list = []

    if onner_list:
        SKC_ID_list = onner_list

    if not onner_list:

        # 判断页面是否在目标页面
        url = web_page.get_url()

        #如果不在目标页面，则进行跳转
        if '/stock/fully-mgt/sale-manage/main' not in url:
            # 获取网站域名
            domain_url = Tools.get_domain_from_url(url)
            # 进行跳转
            web_page.navigate(f'{domain_url}/stock/fully-mgt/sale-manage/main')

        # 等待页面加载完毕
        Tools.wait_loading(web_page)

        # 消除信息
        ADS_hidden(web_page)
        
        for _ in range(2):
            # 将页面数据调整为40
            page_num_xpath = '//div[contains(@class,"index-module__pagination-wrapper")]//input[@data-testid="beast-core-select-htmlInput"]'
            web_page.find_by_xpath(page_num_xpath).click()
            try:
                web_page.find_by_xpath('//ul/li/span[text()="40"]', timeout=1).click()
                break
            except:
                pass

        # 点击展开
        open_xpath = '//div/span[text()="展开"]'
        try:
            web_page.find_by_xpath(open_xpath, timeout=3).click()
        except:
            pass

        if start_station_time and end_station_time:
            # 进行筛选
            # 加入站点时长
            join_station_xpath1 = '(//div[text()="加入站点时长"]/following-sibling::div//input[@placeholder="请输入"])[1]'
            join_station_xpath2 = '(//div[text()="加入站点时长"]/following-sibling::div//input[@placeholder="请输入"])[2]'

            # 进行填写
            web_page.find_by_xpath(join_station_xpath1).input(f'{start_station_time}')
            web_page.find_by_xpath(join_station_xpath2).input(f'{end_station_time}')

        if sku_inventroy:
            if '大于' in sku_inventroy:
                # sku剩余库存
                sku_inventroy_xpath = '//span[text()="SKU剩余库存"]/../../following-sibling::div//div[@data-testid="beast-core-select"]'
                web_page.find_by_xpath(sku_inventroy_xpath).click()
                # 选择大于等于
                web_page.find_by_xpath('//ul[contains(@class,"ST_dropdownPanel")]/li[2]').click()

            # 否则进行操作
            sku_inventroy_num = sku_inventroy.split('于')[1]

            sku_inventroy_num_xpath = '//span[text()="SKU剩余库存"]/../../following-sibling::div//input[@placeholder="请输入"]'
            web_page.find_by_xpath(sku_inventroy_num_xpath).input(f'{sku_inventroy_num}')

        if product_state:
            # 选品状态
            product_selection_state_xpath = '//div[text()="选品状态"]/following-sibling::div//input[@placeholder="请选择"]'
            web_page.find_by_xpath(product_selection_state_xpath).click()

            # 进行状态选择
            for state in product_state:

                # 依次进行勾选参数
                staet_xpath = f'//ul/li/span[text()="{state}"]'
                web_page.find_by_xpath(staet_xpath).click()

                if state == '全选':
                    break   # 点击全选后退出循环

        if date_time:
            # 进行销量日期选择
            sales_select_xpath = '//div[text()="销量"]/following-sibling::div//input[@data-testid="beast-core-select-htmlInput"]'
            web_page.find_by_xpath(sales_select_xpath).click()

            # 点击时间
            date_xpath = f'//ul/li/span[text()="{date_time}"]'
            web_page.find_by_xpath(date_xpath).click()

        if start_sales and end_sales:
            # 点击输入销量范围
            sales_num_xpath1 = '(//div[text()="销量"]/following-sibling::div//input[@placeholder="请输入"])[1]'
            sales_num_xpath2 = '(//div[text()="销量"]/following-sibling::div//input[@placeholder="请输入"])[2]'

            web_page.find_by_xpath(sales_num_xpath1).input(f'{start_sales}')
            web_page.find_by_xpath(sales_num_xpath2).input(f'{end_sales}')

        # 点击查询
        web_page.find_by_xpath('//span[text()="查询"]').click()

        # 等待数据加载
        Tools.wait_loading(web_page)
        
        # 若没有数据则退出
        no_data_xpath = '//div[contains(@class,"TB_emptyData")]'
        no_data_sel = Tools.gen_selector(no_data_xpath)
        if web_page.wait_appear(no_data_sel, timeout=1):
            return 

        # 获取数据总条数
        data_num_xpath = '//li[contains(@class,"PGT_totalText")]'
        data_num_text = web_page.find_by_xpath(data_num_xpath).get_text()
        data_num = re.search(r'(\d+)', data_num_text).group(1)

        if data_num == '0':
            return 

        # 进行计算循环次数
        page = math.ceil(int(data_num) / int(40))

        for i in range(page):

            # 进行SKC id抓取
            # 获取所有行
            trs = web_page.find_all_by_xpath('//tbody/tr')

            # 循环每行
            for tr in trs:
                
                # 获取每行的所有列信息
                tds = tr.find_all_by_xpath('./td')
                print(tds, len(tds))

                # 如果列大于 25 个
                if len(tds) > 25:
                    
                    # 获取商品的skcid
                    skc_id_text = tds[1].find_by_xpath('.//p[contains(text(),"SKC：")]').get_text()
                    skc_id = skc_id_text.split('：')[1]

                    # 将SKC_ID添加入列表中
                    SKC_ID_list.append(skc_id)

            if page > 1 and i != page - 1:

                # 是否还有下一页
                next_page_xpath = '//li[@data-testid="beast-core-pagination-next"]'
                web_page.find_by_xpath(next_page_xpath).click()

                # 等待数据加载
                Tools.wait_loading(web_page)
    
    # 跳转到退货申请页面
    saler_center_url = 'https://seller.kuajingmaihuo.com/wms/stock-mgt/return-apply'
    web_page.navigate(saler_center_url)

    # 等待数据加载完毕
    Tools.wait_loading(web_page)

    # 依次输入skc id
    for SKC_ID in SKC_ID_list:

        # 点击退货申请
        return_apply_xpath = '//span[text()="退货申请"]'
        web_page.find_by_xpath(return_apply_xpath).click()

        # 点击按照skc退
        return_by_skc_xpath = '//div[text()="按SKC退"]'
        web_page.find_by_xpath(return_by_skc_xpath).click()

        SKC_ID_input_xpath = '//label[text()="SKC ID"]/../../following-sibling::div//input'
        apply_reason_xpath = '//label[text()="申请原因"]/../../following-sibling::div//textarea'
        
        # 填写SKC ID 信息
        web_page.find_by_xpath(SKC_ID_input_xpath).input(SKC_ID)

        # 填写申请原因
        web_page.find_by_xpath(apply_reason_xpath).input(apply_reason)

        # 点击确认
        confirm_button_xpath = '//button/span[text()="确认"]'
        web_page.find_by_xpath(confirm_button_xpath).click()
    
    print(SKC_ID_list)
    return SKC_ID_list


def test():
    """测试模块"""
    if "xbot_extensions" in __file__:
        return 
    web_page = xbot.web.get_active(mode='ziniaobrowser')
    onner_list = ['61437877115']
    start_station_time = ''
    end_station_time = ''
    sku_inventroy = ''
    product_state = []
    start_sales = ''
    end_sales = ''
    date_time = ''
    apply_reason = '已滞销'

    overstocked_returns(web_page, onner_list, start_station_time, end_station_time, sku_inventroy, product_state, start_sales, end_sales, date_time, apply_reason)

    exit()



def main(args):

    # 测试模块
    test()
    
    # 功能模块
    web_page = args.get('web_page')
    onner_list = args.get('onner_list', [])
    start_station_time = args.get('start_station_time', '')
    end_station_time = args.get('end_station_time', '')
    sku_inventroy = args.get('sku_inventroy' '')
    product_state = args.get('product_state',[])
    date_time = args.get('date_time','')
    start_sales = args.get('start_sales','')
    end_sales = args.get('end_sales','')
    apply_reason = args.get('apply_reason', '已滞销')

    SKC_ID_list = overstocked_returns(
        web_page,
        onner_list, 
        start_station_time, 
        end_station_time, 
        sku_inventroy, 
        product_state, 
        start_sales, 
        end_sales, 
        date_time, 
        apply_reason
        )
    
    args['data'] = SKC_ID_list

