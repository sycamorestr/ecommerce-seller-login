# 此模块主要处理 【库存报告】 页面下的报告下载操作
# 网址：/listing/reports/ref=xx_invreport_foot_xx
# 

import xbot
from xbot import print, sleep
from . import package
from .package import variables as glv

from enum import Enum
import re
import os

from . import utils
from . import download_utils
from . import _amazon_api

from .utils import print,get_domain
from .utils import handler_container
from .utils_beta import find_by_xpath
from .create_element import create_selector_shadow, create_frame, create_selector


class ReportType(Enum):
    HighVolumeListingsReport = "321"                                        # 大批量商品报告
    大批量商品报告 = "321"
    ReferralFeeDiscountsReport = "17700"                                    # 销售佣金折扣报告
    销售佣金折扣报告 = "17700"
    InventoryReport = "107"                                                 # 库存报告
    库存报告 = "107"
    ActiveListingsReport = "300"                                            # 在售商品报告
    在售商品报告 = "300"
    AmazonfulfilledInventoryReport = "301"                                  # 每月库存历史记录
    亚马逊配送的库存报告 = "301"
    OpenListingsReportLite = "302"                                          # 卖家自配送可售商品报告精简版
    卖家自配送可售商品报告精简版 = "302"
    OpenListingsReportLitre = "303"                                         # 卖家自配送可售商品报告精简升级版
    卖家自配送可售商品报告精简升级版 = "303"
    CategoryListingsReport = "335"    
    分类商品报告 = "335"
    OpenListingsReport = "304"                                              # 卖家自配送可售商品报告
    卖家自配送可售商品报告 = "304"
    InactiveListingsReport = "31700"                                        # 非在售商品报告
    非在售商品报告 = "31700"
    AllListingsReport = "47700"                                             # 所有商品报告
    所有商品报告 = "47700"
    CancelledListingsReport = "309"                                         # 已取消的商品报告
    已取消商品报告 = "309"
    ReferralFeePreviewReport = "315"                                        # 佣金预览报告
    佣金预览报告 = "315"


class InventoryReportsHandler:
    class XPath:
        page_href = '//a[@data-menu-id="inventory-report"]'                 # 报告库页面入口元素
        report_request_btn = '//*[@data-testid="request-report-testid"]'    # 请求报告按钮
        report_variant_click = '//div[@class="report-content"]/kat-dropdown/xbotShadowRoot/div'             # 选择报告类型
        report_type = '//div[@class="report-content"]/kat-dropdown/xbotShadowRoot/div/div[@part]/div/div//div/slot[@role="listbox"]/kat-option[@value="{}"]'                       # 报告类型
        report_download = '//tbody/tr[1]/td[4]//kat-button'                   # 下载按钮
        batch_number = '//tbody/tr[1]/td[2]'                                # 批次编号

    def __init__(self, web_page: xbot.web.WebBrowser):
        self.web_page = web_page

    def to_inventory_reports_page(self):
        """进入库存报告下载页面"""
        # 进入库存和销量报告页面
        # url = "/listing/reports/ref=xx_invreport_foot_xx"
        # utils.to_page(self.web_page, url, self.XPath.page_href, self.XPath.report_request_btn)
        web_page = self.web_page
        isinstance(web_page, xbot.web.WebBrowser)
        domain = get_domain(web_page)
        url = f"{domain}/listing/reports/ref=xx_invreport_foot_xx"
        if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
        ):
            return
        # 如果不是，则导航到目标URL
        web_page.navigate(url, load_timeout=300)
        handler_container(web_page)

    def set_download_params(self, report_type: str):
        """
        设置下载参数
        """
        report_variant_click_sel =  create_selector(self.XPath.report_variant_click,name='22')
        self.web_page.find(report_variant_click_sel, timeout=3).click()
        report_xpath = self.XPath.report_type.format(ReportType[report_type].value)
        report_type_sel = create_selector(report_xpath)
        self.web_page.find(report_type_sel, timeout=3).click()

    def wait_request_completed(self):
        """发送请求并等待请求完成"""

        # 获取唯一请求批次编号
        batch_id_pre = self.web_page.find_by_xpath(self.XPath.batch_number, timeout=3).get_text()
        assert bool(batch_id_pre), "获取请求批次编号失败"

        self.web_page.find(create_selector_shadow(self.XPath.report_request_btn)).click()
        self.web_page.wait_load_completed(timeout=30)
        
        for _ in range(40):
            batch_id_aft = self.web_page.find_by_xpath(self.XPath.batch_number, timeout=3).get_text()
            assert bool(batch_id_aft), "获取请求批次编号失败"
            if batch_id_pre != batch_id_aft:
                break
            sleep(1)
        else:
            raise Exception('等待页面刷新数据超时')
        # 等待45分钟
        try:
            self.web_page.find_by_xpath(self.XPath.report_download, timeout=60 * 60 * 45)
        except Exception as e:
            raise ValueError("请求报告长时间未生成 - " + str(e))

        return batch_id_aft

    def check_params(self, report_type, save_dir, save_name):
        """参数校验"""
        if report_type not in ReportType.__members__:
            raise ValueError("错误的报告类型【{}】, 请重新输入".format(report_type))
        if not bool(save_dir) or not os.path.exists(save_dir):
            raise ValueError("保存文件夹不存在，请先创建 - {}".format(save_dir))

            # 文件名校验
        if bool(save_name) and "." not in save_name:
            raise ValueError("请填写完整文件名（需要加上文件后缀名）")

    @utils.retry_processing(retry_time=1, err_output_args=[""])
    def run(self, site_name, save_dir, save_name, report_type, wait_time=300):
        """入口函数"""

        # 参数校验
        self.check_params(report_type, save_dir, save_name)

        # 切换站点
        _amazon_api.switch_site(self.web_page, site_name)

        # 进入指定页面
        self.to_inventory_reports_page()

        # 设置页面参数
        self.set_download_params(report_type)

        # 等待请求完成
        batch_id = self.wait_request_completed()

        # 下载文件
        return utils.download_file(self.web_page, self.XPath.report_download.format(batch_id), save_dir, save_name, wait_time=300)


def main(args):
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    # report_variant_click_sel =  create_selector('//div[@class="report-content"]/kat-dropdown/xbotShadowRoot/div')
    # print(report_variant_click_sel)
    # web_page.find(report_variant_click_sel, timeout=3).click()
    # xpath = '//div[@class="report-content"]/kat-dropdown/xbotShadowRoot/div/div[@part]/div/div//div/slot[@role="listbox"]/kat-option[@value="{}"]'
    # report_variant_click_sel =  create_selector(xpath.format(321))
    # web_page.find(report_variant_click_sel, timeout=3).click()

    handler = InventoryReportsHandler(web_page)
    handler.run("美国", r"C:\Users\30231\Desktop", '商品报告.xlsx','所有商品报告')