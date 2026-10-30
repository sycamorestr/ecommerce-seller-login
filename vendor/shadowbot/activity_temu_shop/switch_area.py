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
import threading


def switch(web_page: xbot.web.WebBrowser, area: str):
    """切换地区, 不同域名的界面操作步骤不同"""

    # 设置子线程停止标志
    is_completed = False

    def wait_saler_center(
        url: str,
        interval: float = 0.3
    ):
        """
        循环判断当前页面是否为卖家中心页面，如果是，则进行验证

        参数：
            url: 卖家中心验证url标识
            interval: 检查间隔
        """

        nonlocal is_completed

        while not is_completed:
            target_url = web_page.get_url()
            if url in target_url:
                Tools.check_saler_center(web_page)
                return True
            sleep(interval) # 间隔等待
        return False

    confirm_thread = threading.Thread(
        target=wait_saler_center,
        kwargs={
            "url": 'authentication',
        },
        daemon=True
    )
    # 启动线程
    confirm_thread.start()

    # 对全球站点进行转换
    if area == '全球（除美国,欧区）':
        area = '全球'
    
    # https://seller.kuajingmaihuo.com/settle/site-main
    # 在登录后出现页面出现
    if "seller.kuajingmaihuo.com/settle/site-main" in web_page.get_url():

        # 勾选同意
        xpath = '//*[@data-testid="beast-core-checkbox"]'
        if web_page.find_by_xpath(xpath).get_attribute("data-checked") != "true":
            web_page.find_by_xpath(xpath).click()

        xpath = f'//*[normalize-space(text())="{area.strip()}"]'
        web_page.find_by_xpath(xpath).click()

        web_page = web.get_active(mode=web_page.product_name)
        # 判断是否出现是否切换
        if len(web_page.find_all_by_xpath('//span[contains(text(),"确认切换")]', timeout=5)) > 0:
            web_page.find_by_xpath('//span[contains(text(),"确认切换")]').click()
        
        # 设置完成标志并等待线程结束（带超时，避免子线程在 check_saler_center 里耗时过久导致主流程一直等）
        is_completed = True
        confirm_thread.join(timeout=5)

        return 

    # https://seller.kuajingmaihuo.com 切换区域
    if "kuajingmaihuo" in web_page.get_url():
        # 触发弹窗
        xpath = '//*[text()="Seller Central"]'
        web_page.find_by_xpath(xpath).click()
        # 等待站点框出现（加超时，避免无元素时长时间阻塞）
        site_xpath = f'(//button[.//*[contains(text(),"{area}")]])[1]'
        sel = Tools.gen_selector(site_xpath)
        if not web_page.wait_appear(sel, timeout=5):
            is_completed = True
            confirm_thread.join(timeout=5)
            return  # 站点框未出现，直接返回

        # 勾选同意
        xpath = '//*[@data-testid="beast-core-checkbox"]'
        xpath_sel = web_page.find_all_by_xpath(xpath)
        if len(xpath_sel) > 0:
            xpath_dis = [_ for _ in xpath_sel if _.get_bounding(to96dpi=False)[2] !=0 ][0]
            if xpath_dis.get_attribute("data-checked") != "true":
                xpath_dis.click()

        web_page.find_by_xpath(site_xpath).click()

        web_page = web.get_active(mode=web_page.product_name)
        # 判断是否出现是否切换
        if len(web_page.find_all_by_xpath('//span[contains(text(),"确认切换")]', timeout=5)) > 0:
            web_page.find_by_xpath('//span[contains(text(),"确认切换")]').click()
        
        sleep(2)
        web_page = web.get_active("auto")
        web_page.wait_load_completed()

        area_text = web_page.find_by_xpath('//div[contains(@class,"index-module__container")]//a[contains(@class,"active")]').get_text()
        if area_text == area:
            # 设置完成标志并等待线程结束（带超时，避免子线程在 check_saler_center 里耗时过久导致主流程一直等）
            is_completed = True
            confirm_thread.join(timeout=5)
            return
        else:
            raise f"切换区域失败，目标区域{area}，当前切换后区域为{area_text}"

    # https://agentseller-us.temu.com
    if "temu.com" in web_page.get_url():
        sleep(2)
        # 触发下拉框
        # //div[text()='欧区' or text()='美国' or text()='全球（除美国,欧区）']
        old_frame_xpath = "//input[@data-testid='beast-core-select-htmlInput' and (@value='欧区' or @value='美国' or @value='全球（除美国,欧区）' or (@value='全球'))]"
        old_frame_sel = Tools.gen_selector(old_frame_xpath)
        check_flag = False
        try:
            web_page.find_by_xpath("//input[@data-testid='beast-core-select-htmlInput' and (@value='欧区' or @value='美国' or @value='全球（除美国,欧区）' or (@value='全球'))]", timeout=3)
            check_flag = True
        except:
            check_flag = False
        if check_flag:
            web_page.find_by_xpath("//input[@data-testid='beast-core-select-htmlInput' and (@value='欧区' or @value='美国' or @value='全球（除美国,欧区）' or (@value='全球'))]").click()
            elem_list = web_page.find_all_by_xpath("//ul[contains(@class,'dropdownPanel')]/li")
            Tools.down_select(web_page, area, elem_list)
        else:
            new_area_xpath = [
                f'//div[@id="Symbol(shell_scroll_container)"]//a[text()="{area}"]',
                f'//div[@id="mmsos-layout-content"]//div[text()="{area}"]',
            ]
            for area_xpath in new_area_xpath:
                try:
                    web_page.find_by_xpath(area_xpath, timeout=1).click()
                    break
                except:
                    continue
            else:
                raise Exception(f'{area} 站点切换失败')
    
        # 判断是否出现是否切换
        if len(web_page.find_all_by_xpath('//span[contains(text(),"确认切换")]', timeout=5)) > 0:
            web_page.find_by_xpath('//span[contains(text(),"确认切换")]').click()

        # 设置完成标志并等待线程结束（带超时，避免子线程在 check_saler_center 里耗时过久导致主流程一直等）
        is_completed = True
        confirm_thread.join(timeout=5)
        return


def test():
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active(mode='chrome')
    st = '美国'
    switch(web_page, st)
    exit()


def main(args):
    test()
    
    web_page = args.get("web_page")
    area = args.get("area", '全球(除美国、欧区)')
    # web_page = web.get_active(mode='chrome')
    switch(web_page, area)
