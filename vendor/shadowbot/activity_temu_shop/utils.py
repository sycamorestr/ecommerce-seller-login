# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import time
import re
import math

import xbot
from xbot import print, sleep, web
from xbot.selector import Selector
from .import package
from .package import variables as glv
from xbot_extensions.activity_jfbym import std_slider_captcha
from typing import Any, Union, List
from xbot_extensions.web_action.select_date import select_date
from xbot._core.retry import Retry

from urllib.parse import urlparse

class Tools:
    BASE_URL = "https://seller.kuajingmaihuo.com"
    @staticmethod
    def gen_selector(xpath):
    # 判断xpath是否存在
        data = {
            "id": "ifream-xpath",
            "name": "ifream-xpath",
            "type": "simple",
            "xpath": {"enable": "true", "segments": [xpath]},
        }
        return Selector(data)

    @staticmethod
    def wait_loading(web_page, appear_time=3, over_time=20):
        # 等待数据加载
        loading_xpath = '//div[contains(@class,"loading")]'
        loading_sel = Tools.gen_selector(loading_xpath)
        if web_page.wait_appear(loading_sel, timeout=appear_time):
            web_page.wait_disappear(loading_sel, timeout=over_time) 

    @staticmethod
    def get_web_page_product_name(web_page):
        # 返回浏览器名称
        product_name = getattr(
            web_page,
            "product_name",
            "cef" if web_page._controller == "CEFBrowser" else "chrome",
        )
        return product_name

    @staticmethod
    def get_domain_from_url(url):
        # 获取域名
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc  # 例如：www.example.com
        except Exception as e:
            return None
    
    @staticmethod
    # TODO：可能会出现没有授权确认，也没提示账号密码出现的情况
    def check_saler_center(web_page):
        # 判断是否出现 商家中心
        # https://agentseller.temu.com/main/authentication
        web_page.wait_load_completed()
        if "authentication" in web_page.get_url():
            # 触发商家中心
            # 在跳转到验证页面时，网页分自动打开卖家中心验证弹窗的情况与需要手动点击的情况
            sleep(5)    # 死等待5s，判断网页是否有自动弹出验证窗口，若有则激活验证窗口，若无，则激活当前页面，进行手动打开验证窗口操作
            # 激活当前窗口/页面
            web_page = xbot.web.get_active(mode=web_page.product_name)

            # 复选框
            core_box_xpath = '//label[.//*[@data-testid="beast-core-box"]]'

            # 确认授权并前往
            confirm_to_xpath = '//span[text()="确认授权并前往"]'
            is_readed_xpath = '//label[@data-testid="beast-core-checkbox"]//input/following-sibling::div'
            is_readed_check_box_xpath = '//label[@data-testid="beast-core-checkbox"]//input'

            core_box_sel = web_page.find_all_by_xpath(core_box_xpath, timeout=5)
            if len(core_box_sel) > 0:
                label_state = core_box_sel[0].get_attribute('data-checked')
                is_readed_sel = web_page.find_all_by_xpath(is_readed_check_box_xpath, timeout=5)
                if label_state == 'false':
                    # is_readed_sel[0].click()
                    is_readed_sel[0].check(mode="check")
                sleep(2)
            else:
                saler_center_sel = web_page.find_by_xpath('//*[contains(@class,"authentication_goto")]')
                if saler_center_sel.is_displayed():
                    saler_center_sel.click()
                sleep(5)    # 点击商家家中心后等待5s，防止没有激活到对应的浏览器页面
                # 激活新打开的浏览器页面
                web_page = xbot.web.get_active(mode=web_page.product_name)
                core_box_sel = web_page.find_all_by_xpath(core_box_xpath, timeout=5)
                is_readed_sel = web_page.find_all_by_xpath(is_readed_check_box_xpath, timeout=5)
                sleep(2)
                if len(core_box_sel) >0:
                    if core_box_sel[0].get_attribute('data-checked') == 'false':
                        # is_readed_sel[0].click()
                        is_readed_sel[0].check(mode="check")

            # 判断登录还是前往
            confirm_to_sel = Tools.gen_selector(confirm_to_xpath)
            if web_page.wait_appear(confirm_to_sel, timeout=2):
                web_page.find_by_xpath(confirm_to_xpath).click()
            else:
                web_page.find_by_xpath('//button/span[text()="授权登录"]').click()
            
            sleep(3)    # 等待3s，等验证窗口消失后再进行激活网页
            web_page = xbot.web.get_active(mode=web_page.product_name)
            # 判断是否有切换
            switch_xpath = '//span[.="确认切换"]'
            swicth_list_Sel = web_page.find_all_by_xpath(switch_xpath, timeout=5)
            switch_display = [_ for _ in swicth_list_Sel if _.get_bounding(to96dpi=False)[2] !=0 ]
            if len(switch_display) > 0:
                switch_display[0].click()

            # 处理完激活一下当前页面，判断是否为验证窗口页面
            web_page = xbot.web.get_active(mode=web_page.product_name)
            if "authentication" in web_page.get_url():
                web_page.close()

                # 重新激活到当前操作页面
                web_page = xbot.web.get_active(mode=web_page.product_name)
            web_page.wait_load_completed()
            sleep(3)
            return True

    @staticmethod
    def check_web(web_page: Any, keyword: str) -> Any:
        """检查网页 URL 是否包含指定关键字，不包含则导航到正确地址。"""
        try:
            url = web_page.get_url()
            if keyword not in url:
                web_page.navigate(f"{Tools.BASE_URL}/{keyword}")
            return web_page
        except Exception as e:
            print(f"check_web报错：{e}")
            return None
    
    @staticmethod
    def get_page_num(web_page, num=10, is_switch=True):
        """进行页码选择，获取页码"""

        if is_switch is True:
            # 进行页码选择
            page_frame_xpath = '//li[contains(text(),"共有 ")]/following-sibling::li/div'
            web_page.find_by_xpath(page_frame_xpath).click()

            # 切换页码显示num条数据""
            page_num_xpath = f'//ul[@role="listbox"]/li/span[text()="{num}"]'
            page_num = web_page.find_by_xpath(page_num_xpath).click()

        # 获取总数居
        total_data_text = web_page.find_all_by_xpath('//li[contains(text(),"共有 ")]')
        total_data_text = [_.get_text() for _ in total_data_text if _.get_bounding(to96dpi=False)[2]!=0][0]
        total_data = re.search(r'\d+', total_data_text, re.S).group(0)

        # 数据为0则退出
        if int(total_data) == 0:
            print('当前店铺暂无数据')
            return
        else:
            return total_data

        if is_switch is True:
            # 获取页码
            page = math.ceil(int(total_data) / int(num))
            return page

    @staticmethod
    def check_target_web(web_page: Any, keyword: str) -> Any:
        """判断页面是否在目标页面，不在则导航到正确地址"""
        for _ in range(3):
            try:
                url = web_page.get_url()
                if keyword not in url:
                    # 获取网站域名
                    domain_url = Tools.get_domain_from_url(url)
                    # 跳转页面
                    web_page.navigate(f'{domain_url}/{keyword}')
            except Exception as e:
                print(f'check_target_web报错:{e}')


    @staticmethod
    def handle_std_capture(web_page: Any) -> None:
        """处理标准滑块验证码。"""
        try:
            bg_elem = package.selector('bg_elem')
            dr_elem = package.selector('dr_elem')
            std_slider_captcha.handle_captcha(web_page, bg_elem, dr_elem)
        except Exception as e:
            print(f"处理验证码报错：{e}")
    
    @staticmethod
    def handle_info(web_page, wait_appear=2):
        """注入js，消除信息框"""
        AD_XPATH = '//div[@data-testid="beast-core-portal-main"]'
        ads = Tools.gen_selector(AD_XPATH)
        ads_appear = web_page.wait_appear(ads, timeout=wait_appear)
        if ads_appear:
            dis = """
            function hideAds(context, args) {
                document.querySelectorAll('[data-testid="beast-core-portal-main"]')
                        .forEach(el => el.style.display = args);
            }
            """
            web_page.execute_javascript(dis, "none")
        sleep(0.5)
        GD_XPATH = '//div[contains(@class,"satisfaction-score_container")]'
        gds = Tools.gen_selector(GD_XPATH)
        if web_page.wait_appear(gds, timeout=wait_appear):
            dis = """
            function hideAds(context, args) {
                document.querySelectorAll('div[class*="satisfaction-score_container"]')
                        .forEach(el => el.style.display = args);
            }
            """
            web_page.execute_javascript(dis, "none")
        sleep(0.5)

    @staticmethod
    def see_element(ele, location):
        """
        将指定列滚动到可视页面中心
        ::params ele, 网页元素的元素对象
        ::params location, 将这个元素滚动到页面的 start/center/end 部位
        """

        script = """
            function (element, input) {
                element.scrollIntoView({ behavior: 'smooth', block: input});
            }
        """
        ele.execute_javascript(script, location)

    @staticmethod
    def select_date(web_page, start_time, end_time):
        """日期选择"""
        web_page.find_by_xpath("//input[contains(@placeholder,'请选择') or contains(@placeholder,'开始时间')]").hover()
        web_page.find_by_xpath("//input[contains(@placeholder,'请选择') or contains(@placeholder,'开始时间')]").click()
        date_frame = web_page.find_by_xpath('//*[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]')
        select_date(web_page, date_frame, start_time, end_time)

    @staticmethod
    def click_dropdown(web_page, target_text: Union[str, List[str]], elem_list: List):
        """下拉复选框选择"""
        def handle_dropdown(target_text, elem_list):
            for elem in elem_list:
                check_box_elem = elem.find_by_xpath("./preceding-sibling::label")
                if elem.get_text() == target_text and check_box_elem.get_attribute('data-checked') == 'false':
                    elem.click()
                    break
        if isinstance(target_text, str):
            handle_dropdown(target_text, elem_list)
        elif isinstance(target_text, list):
            for text in target_text:
                handle_dropdown(text, elem_list)

    @staticmethod
    def down_select(web_page, target_text: str, elem_list: List):
        """下拉框选择"""
        for elem in elem_list:
            text = elem.get_text()
            if text == '全球（除美国,欧区）':
                text = '全球'
            if text == target_text:
                elem.click()
                break

    # 谷歌、紫鸟V5等店铺切换
    @staticmethod
    def switch_store(web_page, all_store_elem, store_name):
        """切换店铺"""
        is_switch = False
        try:
            store_list = web_page.find_all_by_xpath(all_store_elem, timeout=5)
            if len(store_list) == 0:
                raise Exception('不属于谷歌、紫鸟v5等浏览器')
            for i, store in enumerate(store_list):
                current_store_name_elem = store.find_by_xpath(".//div[contains(@class,'mallInfo')]/div[1]")
                current_store_name = current_store_name_elem.get_text().strip("半托管")
                current_store_name = re.sub(r'\s+',"",current_store_name)
                if current_store_name == store_name:
                    try:
                        current_store_name_elem.find_by_xpath("./..//preceding-sibling::div[text()='当前店铺']",timeout=2)
                        web_page.find_by_xpath("//div[@data-testid='beast-core-modal-body']/../following-sibling::div").click()
                    except:
                        current_store_name_elem.find_by_xpath("./..//*[text()='切换' or text()='进入']").click(simulative=False)
                    finally:
                        break
                if i == len(store_list) - 1:
                    raise ValueError(f"未找到该店铺 {store_name}")

            # 判断是否出现 商家中心
            # https://agentseller.temu.com/main/authentication
            if "authentication" in web_page.get_url():
                # 触发商家中心
                web_page.find_by_xpath('//div[contains(@class,"authentication_goto")]').click()
                web_page2 = xbot.web.get_active(mode='auto')
                confirm_to_xpath = '//span[text()="确认授权并前往"]'
                is_readed_xpath = '//label[@data-testid="beast-core-checkbox"]//input'

                confirm_to_sel = Tools.gen_selector(confirm_to_xpath)
                if web_page2.wait_appear(confirm_to_sel, timeout=5):
                    web_page2.find_by_xpath(confirm_to_xpath).click()
                else:
                    if len(web_page2.find_all_by_xpath(is_readed_xpath)) > 0:
                        web_page2.find_by_xpath(is_readed_xpath).click()
                    web_page2.find_by_xpath('//button/span[text()="授权登录"]').click()
            is_switch = True
        except:
            pass
        return is_switch

    # 紫鸟V6店铺切换
    @staticmethod
    def switch_ydk_store(web_page, all_store_elem, store_name):
        """切换店铺"""
        is_switch = False
        store_name = re.sub(r'\s+', '', store_name)
        try:
            store_list = web_page.find_all_by_xpath(all_store_elem, timeout=10)
            
            for i, store in enumerate(store_list):
                current_store_name_elem = store.find_by_xpath('.//div[@class="_1esvNqcN" or contains(@class,"site-main_mallInfo")]')
                current_store_name = current_store_name_elem.find_by_xpath('.//div[@class="_2zZc_kxY" or contains(@class,"site-main_mallName")]').get_text().strip("半托管")
                current_store_name = re.sub(r'\s+','',current_store_name)
                if current_store_name == store_name:
                    try:
                        current_store_name_elem.find_by_xpath(".//div[contains(@class,'site-main_tag') or text()='当前店铺']",timeout=2)
                        web_page.find_by_xpath("//div[contains(@class,'iconWrapper')]//*[local-name()='svg'][@data-testid='beast-core-modal-icon-close']").click()
                    except:
                        current_store_name_elem.find_by_xpath("(.//*[normalize-space()='切换' or normalize-space()='进入'])[last()]").click(simulative=False)
                    finally:
                        break
                if i == len(store_list) - 1:
                    raise ValueError(f"未找到该店铺 {store_name}")
                    
            # 判断是否出现 商家中心
            # https://agentseller.temu.com/main/authentication
            if "authentication" in web_page.get_url():
                # 触发商家中心
                web_page.find_by_xpath('//div[contains(@class,"authentication_goto")]').click()
                web_page2 = xbot.web.get_active(mode='auto')
                confirm_to_xpath = '//span[text()="确认授权并前往"]'
                is_readed_xpath = '//label[@data-testid="beast-core-checkbox"]//input'

                confirm_to_sel = Tools.gen_selector(confirm_to_xpath)
                if web_page2.wait_appear(confirm_to_sel, timeout=5):
                    web_page2.find_by_xpath(confirm_to_xpath).click()
                else:
                    if len(web_page2.find_all_by_xpath(is_readed_xpath)) > 0:
                        web_page2.find_by_xpath(is_readed_xpath).click()
                    web_page2.find_by_xpath('//button/span[text()="授权登录"]').click()
            is_switch = True
        except:
            pass
        return is_switch

    # 2026年9月22日新版
    @staticmethod
    def new_switch_store(web_page, all_store_elem, store_name):
        """切换店铺"""
        is_switch = False
        try:
            store_list = web_page.find_all_by_xpath(all_store_elem, timeout=10)
            for i, store in enumerate(store_list):
                current_store_name_elem = store.find_by_xpath('.//div[contains(@class,"account-info_mallName")]')
                current_store_name = current_store_name_elem.find_by_xpath('.//span[@data-testid="beast-core-ellipsis"]').get_text().strip("半托管")
                current_store_name = re.sub(r'\s+','',current_store_name)
                store_name = re.sub(r'\s+','',store_name)
                if current_store_name == store_name:
                    try:
                        current_store_name_elem.find_by_xpath(".//*[text()='当前登录']",timeout=2)
                        web_page.find_by_xpath('//div[contains(@class,"account-info_userInfo")]//div[contains(@class,"account-info_accountInfo")]').click()
                    except:
                        current_store_name_elem.find_by_xpath('.//span[@data-testid="beast-core-ellipsis"]').click(simulative=False)
                    finally:
                        break
                if i == len(store_list) - 1:
                    raise ValueError(f"未找到该店铺 {store_name}")
                    
            # 判断是否出现 商家中心
            # https://agentseller.temu.com/main/authentication
            if "authentication" in web_page.get_url():
                # 触发商家中心
                web_page.find_by_xpath('//div[contains(@class,"authentication_goto")]').click()
                web_page2 = xbot.web.get_active(mode='auto')
                confirm_to_xpath = '//span[text()="确认授权并前往"]'
                is_readed_xpath = '//label[@data-testid="beast-core-checkbox"]//input'

                confirm_to_sel = Tools.gen_selector(confirm_to_xpath)
                if web_page2.wait_appear(confirm_to_sel, timeout=5):
                    web_page2.find_by_xpath(confirm_to_xpath).click()
                else:
                    if len(web_page2.find_all_by_xpath(is_readed_xpath)) > 0:
                        web_page2.find_by_xpath(is_readed_xpath).click()
                    web_page2.find_by_xpath('//button/span[text()="授权登录"]').click()
            is_switch = True
        except:
            pass
        return is_switch

    @staticmethod
    def test_switch_store(web_page, all_store_elem, store_name):
        """切换店铺"""
        store_list = web_page.find_all_by_xpath(all_store_elem, timeout=10)
        print(store_list)
        for i, store in enumerate(store_list):
            current_store_name_elem = store.find_by_xpath('.//div[@class="_1esvNqcN" or contains(@class,"site-main_mallInfo")]')
            current_store_name = current_store_name_elem.find_by_xpath('.//div[@class="_2zZc_kxY" or contains(@class,"site-main_mallName")]').get_text().strip("半托管")
            current_store_name = re.sub(r'\s+','',current_store_name)
            print(current_store_name)
            print(store)
            if current_store_name == store_name:
                try:
                    current_store_name_elem.find_by_xpath(".//div[contains(@class,'site-main_tag') or text()='当前店铺']",timeout=2)
                    web_page.find_by_xpath("//div[contains(@class,'iconWrapper')]//*[local-name()='svg'][@data-testid='beast-core-modal-icon-close']").click()
                except:
                    current_store_name_elem.find_by_xpath("(.//*[normalize-space()='切换' or normalize-space()='进入'])[last()]").click(simulative=False)
                finally:
                    break
            if i == len(store_list) - 1:
                raise ValueError(f"未找到该店铺 {store_name}")
                
        # 判断是否出现 商家中心
        # https://agentseller.temu.com/main/authentication
        if "authentication" in web_page.get_url():
            # 触发商家中心
            web_page.find_by_xpath('//div[contains(@class,"authentication_goto")]').click()
            web_page2 = xbot.web.get_active(mode='auto')
            confirm_to_xpath = '//span[text()="确认授权并前往"]'
            is_readed_xpath = '//label[@data-testid="beast-core-checkbox"]//input'

            confirm_to_sel = Tools.gen_selector(confirm_to_xpath)
            if web_page2.wait_appear(confirm_to_sel, timeout=5):
                web_page2.find_by_xpath(confirm_to_xpath).click()
            else:
                web_page2.find_by_xpath(is_readed_xpath).click()
                web_page2.find_by_xpath('//button/span[text()="授权登录"]').click()
        is_switch = True    


def main(args):
    # web_page = web.get_active(mode='superbrowser')
    web_page = web.get_active(mode='chrome')

    # Tools.click_dropdown(web_page)
    # Tools.check_saler_center(web_page)
    Tools.test_switch_store(web_page, '//div[contains(@class,"site-main_mallSection")]', 'gzpas')