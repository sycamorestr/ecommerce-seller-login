# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser,WebElement
from pathlib import Path
from .utils import get_domain
from .utils import handler_container
from .activities_utils import gen_selector,download_handler
from ._amazon_api import switch_language
from xbot import excel


class Xpath:
    # 货件编号输入框
    ShipmentNumInput = '//*[@id="tab-view"]/kat-box//kat-input'
    # 货件编号搜索按钮
    ShipmentSearchBtn = '//*[@id="tab-view"]/kat-box//button[contains(@id, "search")]'
    # 货件处理进度表状态列
    ShipmentStatusCol = '//*[@id="ien-link-container"]//a'
    # 进口详情中进口记录下拉框
    ImportRecordSelect = '//*[@id="katModal"]//kat-dropdown'
    # 进口详情中输入框
    ImportRecordInput = '//*[@id="katModal"]//kat-textarea'
    # 进口详情中进口参考编号输入框
    IenMrnInput = '//*[@id="katModal"]//kat-textarea[1]'
    # 进口详情中经济营运者注册和识别号输入框
    EoriInput = '//*[@id="katModal"]//kat-textarea[2]'
    # 进口详情中保存按钮
    ImportRecordSave = '//*[@id="katModal"]//kat-button[2]'
    # 进口详情中取消按钮
    ImportRecordCancel = '//*[@id="katModal"]//kat-button[1]'
    # ImportRecordSave ='//*[local-name()="kat-button"][@label="保存"]/xbotShadowRoot/button[normalize-space(.)="保存"]'
    # ImportRecordCancel ='//span//*[local-name()="kat-button"][@label="取消"]/xbotShadowRoot/button[normalize-space(.)="取消"]'
def input_parameter_valid(web_page:WebBrowser):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.ShipmentSearchBtn), timeout=30):
        raise Exception(f"进入货件处理进度页面失败，未找到货件编号搜索按钮： {Xpath.ShipmentSearchBtn}")


def fill_import_details(web_page: WebBrowser, file_path: str):
    # 货件处理进度IEN、MRN和EORI填写
    work_book = excel.open(file_name=file_path, kind='auto_check')
    work_sheet = work_book.get_active_sheet()
    total_rows = work_sheet.get_row_count()
    # 遍历输入文件中每行
    for row in range(2, total_rows+1):
        row_content_list = work_sheet.get_row(row_num=row, using_text=True) # 获取输入文件中行内容
        web_page.find_by_xpath(Xpath.ShipmentNumInput).clipboard_input(row_content_list[0]) # 输入货件单号
        web_page.find_by_xpath(Xpath.ShipmentSearchBtn).click() # 查询货件单号
        deal_flag = False # 是否处理进口详情不全标识
        complete_flag = False # 进口详情完整标识

        web_page = xbot.web.get_active(mode=web_page.product_name)
        # 处理进口详情不全的货件单号
        for item in web_page.find_all_by_xpath(Xpath.ShipmentStatusCol,timeout=5):
            if item.get_text() == '导入详细信息不完整':
                item.click() # 点击进入进口详情弹窗页面
                # 点击进口记录，并选择该货件有进口记录选项
                sleep(2)
                web_page.find_by_xpath(Xpath.ImportRecordSelect).click()
                for option in web_page.find_all("fill_goods_ien_进口记录选项"):
                    if option.get_text() in('该货件有进口记录','是'):
                        option.click()
                        break
                # 判断是填写IEN，还是填写MRN和EORI
                input_textarea_num = len(web_page.find_all_by_xpath(Xpath.ImportRecordInput))
                if input_textarea_num == 1:
                    # 如果进口详情中输入框数量为1，填写IEN；第一个输入框填写IEN
                    web_page.find_by_xpath(Xpath.IenMrnInput).clipboard_input(text=row_content_list[1]) # 填写IEN
                elif input_textarea_num == 2:
                    # 如果进口详情中输入框数量为2，填写MRN和EORI；第一个输入框填写MRN，第二个输入框填写EORI
                    web_page.find_by_xpath(Xpath.IenMrnInput).clipboard_input(text=row_content_list[2]) # 填写MRN
                    web_page.find_by_xpath(Xpath.EoriInput).clipboard_input(text=row_content_list[3]) # 填写EORI
                # web_page.find_by_xpath(Xpath.ImportRecordSelect).click(anchor=('bottomRight', 50, 0)) # 点击进口详情中空白处
                web_page.find_by_xpath(Xpath.ImportRecordSave).click() # 点击保存按钮
                deal_flag = True
            elif item.get_text() == '导入详细信息已完成':
                complete_flag = True
        if deal_flag:
            # 如果填写进口详情不全，在输入文件表中E列记录'已填写进口详情不全'
            work_sheet.set_cell(row_num=row, col_name='E', value='已填写进口详情不全')
        else:
            if complete_flag:
                # 如果是进口详情完整，在输入文件表中E列记录'进口详情完整'
                work_sheet.set_cell(row_num=row, col_name='E', value='进口详情完整')
            else:
                # 如果没有填写进口详情不全，在输入文件表中E列记录'暂无填写窗口'
                work_sheet.set_cell(row_num=row, col_name='E', value='暂无填写窗口')
    work_book.save()
    work_book.close()


def fill_goods_ien(web_page: WebBrowser, file_path: str):
    # 填写货件处理进度IEN
    # 输入参数转换

    # 输入参数校验
    input_parameter_valid(web_page)

    # 进入货件处理进度页面
    domain = get_domain(web_page)
    url = f"{domain}/gp/ssof/shipping-queue.html"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 填写进口详情
    fill_import_details(web_page, file_path)


def test_fill_goods_ien():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="chrome")
    file_path = r"C:\Users\Administrator\Desktop\IEN&MRN填写-EHJ.xlsx" # 输入文件路径

    fill_goods_ien(web_page, file_path)
    exit()


def main(args):
    # 测试代码入口
    test_fill_goods_ien()

    # 业务代码入口
    web_page = args.get("web_page")
    file_path = args.get("file_path")
    fill_goods_ien(web_page, file_path)
