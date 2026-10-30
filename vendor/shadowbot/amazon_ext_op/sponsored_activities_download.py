# 广告数据一览
# 网址： https://advertising.amazon.com/campaign-manager    # amazon.com 和地区有关
# 

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

from . import _amazon_api

from . import utils
from . import download_utils
from .utils import print, get_ad_domain
from .activities_utils import download_handler
from xbot_extensions.web_action.select_date import select_date
from typing import Optional
from xbot.web import WebBrowser


class XPath:
    # 删除所有筛选按钮
    RemoveAll = '//button[contains(@id, "removeAll")]'
    # 筛选条件按钮
    FilterBy = '//button[contains(@data-e2e-id,"addFilterSelector:optionSelector")]'
    # 国家/地区选项按钮
    CountryOption = '//button[@value="country"]'
    # 进行中（状态）选项按钮
    StateOption = '//button[@value="state"]'
    # 广告活动日期（打开日期选择器按钮）
    CampaignDate = '//button[contains(@data-takt-id, "dateRangeFilter:openContainer")]'
    # 点击量 按钮
    Click_xpath = '//button[contains(@id,"option-clicks")]'
    # 点击量输入框
    Click_frame = '//input[contains(@data-e2e-id,"clicks:input")]'
    #
    DateApply = '//button[contains(@data-takt-id, "dateRangeFilter:dateRange-save")]'
    # 导出按钮
    Export = '//button[contains(@data-takt-id, "export")]'
    # 应用按钮
    Apply_button = '//button[contains(@id, "apply")]'




def wait_for_element_by_xpath(web_page: WebBrowser, xpath: str, timeout: int = 300):
    try:
        return web_page.find_by_xpath(xpath, timeout=timeout)
    except Exception as e:
        return False


def wait_page_elements_ready(web_page: WebBrowser, timeout: int = 60):
    """
    等待页面元素加载完成
    
    参数:
        web_page: 浏览器对象
        timeout: 超时时间（秒）
    
    返回:
        bool: 如果页面元素加载完成返回 True
    """
    from time import time
    start_time = time()
    
    # 等待页面基本加载完成
    web_page.wait_load_completed(timeout=30)
    
    # 等待关键元素出现（筛选按钮和导出按钮）
    key_elements = [
        XPath.FilterBy,
        XPath.Export
    ]
    
    for xpath in key_elements:
        if time() - start_time > timeout:
            raise Exception(f"等待页面元素加载超时：{timeout}秒，未找到元素：{xpath}")
        
        try:
            web_page.find_by_xpath(xpath, timeout=min(10, timeout - (time() - start_time)))
        except Exception as e:
            raise Exception(f"等待页面元素加载失败，未找到元素：{xpath}，错误：{e}")
    
    return True


def wait_data_refresh_completed(web_page: WebBrowser, timeout: int = 60):
    """
    等待数据刷新完成（筛选条件应用后）
    
    参数:
        web_page: 浏览器对象
        timeout: 超时时间（秒）
    
    返回:
        bool: 如果数据刷新完成返回 True
    """
    from time import time
    start_time = time()
    
    # 方法1: 等待页面加载完成
    web_page.wait_load_completed(timeout=30)
    
    # 方法2: 等待加载指示器消失（如果存在）
    loading_indicators = [
        '//*[contains(@class, "loading")]',
        '//*[contains(@class, "spinner")]',
        '//*[contains(@aria-label, "Loading")]',
        '//*[@role="progressbar"]'
    ]
    
    # 检查是否有加载指示器，如果有则等待其消失
    for indicator_xpath in loading_indicators:
        try:
            loading_elements = web_page.find_all_by_xpath(indicator_xpath, timeout=2)
            if loading_elements:
                # 等待加载指示器消失
                for _ in range(int(timeout)):
                    if time() - start_time > timeout:
                        break
                    try:
                        current_elements = web_page.find_all_by_xpath(indicator_xpath, timeout=1)
                        if not current_elements or all(not elem.is_displayed() for elem in current_elements):
                            break
                    except:
                        break
                    sleep(0.5)
        except:
            pass
    
    # 方法3: 等待关键元素稳定（导出按钮可见且可点击）
    try:
        export_btn = web_page.find_by_xpath(XPath.Export, timeout=10)
        # 确保按钮可见且可点击
        if not export_btn.is_displayed():
            raise Exception("导出按钮不可见")
    except Exception as e:
        if time() - start_time < timeout:
            # 如果还没超时，再等待一下
            sleep(2)
            try:
                web_page.find_by_xpath(XPath.Export, timeout=5)
            except:
                raise Exception(f"等待数据刷新完成失败，未找到导出按钮，错误：{e}")
        else:
            raise Exception(f"等待数据刷新完成超时：{timeout}秒，错误：{e}")
    
    # 额外等待一小段时间，确保数据完全加载
    sleep(1)
    
    return True


def select_campaign_status(web_page: WebBrowser, target_status_cn: str):
    """
    选择广告活动状态（单选按钮）
    
    参数:
        web_page: 浏览器对象
        target_status_cn: 状态的中文名称（如 "已启用"、"已暂停" 等）
    """
    # 状态映射字典
    status_map = {
        "全部": "ENABLED_PAUSED_ARCHIVED",
        "仅剩存档未完成": "ENABLED_PAUSED",
        "启用和暂停": "ENABLED_PAUSED",
        "已启用": "ENABLED",
        "已暂停": "PAUSED",
        "已存档": "ARCHIVED",
    }
    
    # 检查状态名称是否有效
    if target_status_cn not in status_map:
        raise Exception(f"无效的状态名称: {target_status_cn}。支持的状态: {', '.join(status_map.keys())}")
    
    # 获取映射的 value
    mapped_value = status_map[target_status_cn]
    
    # 使用 XPath 定位单选按钮的父 label
    xpath = f"//label[.//input[@value='{mapped_value}']]"
    
    # 查找并点击
    label_element = web_page.find_by_xpath(xpath, timeout=10)
    label_element.click(simulative=False)
    sleep(0.5)


def to_campaigns_page_if_need(web_page: WebBrowser, url: str):
    """如果当前页面不是目标页面，则导航到目标页面"""
    current_url = web_page.get_url()
    if not current_url.startswith(url):
        web_page.navigate(url, load_timeout=300)
        web_page.wait_load_completed(timeout=30)
        # 进入广告页也有需要登录的情况
        _amazon_api.login(web_page)
        # 等待页面元素加载完成
        wait_page_elements_ready(web_page, timeout=60)


def set_campaigns_params(web_page: WebBrowser, start_date: Optional[str] = None, end_date: Optional[str] = None, orgins: Optional[list] = None, status: Optional[str] = None, clicks_num: int = 0):
    """
    设置筛选参数
    
    参数:
        web_page: 浏览器对象
        start_date: 开始日期，格式 "YYYY-MM-DD"，可选
        end_date: 结束日期，格式 "YYYY-MM-DD"，可选
        orgins: 国家/地区列表，可选，如果包含"全选"则全选所有国家
        status: 广告活动状态，可选（如 "已启用"、"已暂停"、"已存档"、"全部" 等）
    """
    # 第一步：判断是否存在"删除所有"按钮，如果存在则点击清除所有筛选
    if wait_for_element_by_xpath(web_page, XPath.RemoveAll, timeout=3):
        web_page.find_by_xpath(XPath.RemoveAll).click(simulative=False)
        sleep(1)
        print("已清除所有筛选条件")
    
    # 第二步：筛选日期（如果提供了日期参数）
    if start_date and end_date:
        if wait_for_element_by_xpath(web_page, XPath.CampaignDate, timeout=10):
            # 获取日期选择器按钮元素
            campaign_date_btn = web_page.find_by_xpath(XPath.CampaignDate)
            
            # 将日期选择器元素滚动到屏幕中间，确保智能日期选择功能正常工作
            scroll_to_center_script = '''
            function (ele, _) {
                ele.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
            }
            '''
            campaign_date_btn.execute_javascript(scroll_to_center_script)
            sleep(0.5)
            
            # 点击打开日期选择器
            campaign_date_btn.click(simulative=False)
            sleep(1)
            
            # 使用find方法获取日期选择器容器元素（从元素库中获取）
            date_picker = web_page.find("广告活动日期", timeout=5)
            
            # 使用select_date方法选择日期范围
            select_date(web_page, date_picker, start_date, end_date, simulative=True)
            
            sleep(1)
            
            # 点击应用按钮
            web_page.wait_appear(web_page.find_by_xpath(XPath.DateApply),timeout =20)
            web_page.find_by_xpath(XPath.DateApply).click()
            # 等待数据刷新完成
            wait_data_refresh_completed(web_page, timeout=60)
            print(f"已设置日期范围: {start_date} 至 {end_date}")
    
    # 第三步：设置国家/地区筛选（如果提供了国家参数）
    if orgins is not None:
        if wait_for_element_by_xpath(web_page, XPath.FilterBy, timeout=2):
            # 点击筛选条件按钮
            web_page.find_by_xpath(XPath.FilterBy).click()
            sleep(1)
            
            # 点击国家/地区选项
            web_page.find_by_xpath(XPath.CountryOption).click()
            sleep(1)
            
            # 创建副本，避免修改原始列表
            orgins_copy = orgins.copy() if isinstance(orgins, list) else list(orgins)
            
            # 支持全选
            if "全选" in orgins_copy:
                query_all_xpath = '//button[text()="全选"]'
                web_page.find_by_xpath(query_all_xpath).click()
            else:
                # 定义所有选项的 XPath
                CountryOptions = '//label[contains(@data-takt-id, "-checkbox")]'
                
                # 因为前面已经清除过了，所以不会有已选择的国家，直接进行国家选择
                # 开始遍历页面上的所有国家选项
                for option in web_page.find_all_by_xpath(CountryOptions):
                    # 尝试从 <p> 标签获取国家名称（兼容新结构）
                    try:
                        p_tag = option.find_by_xpath(".//p")
                        current_text = p_tag.get_text().strip()
                    except:
                        # 如果找不到 <p> 标签，则使用整个 label 的文本
                        current_text = option.get_text().strip()
                    
                    # 如果这个文本在你的目标列表 orgins_copy 里
                    if current_text in orgins_copy:
                        # 直接点击 option (label) 进行选择
                        option.click()
                        sleep(0.2)
                        
                        # 从待办列表中移除已找到的国家
                        orgins_copy.remove(current_text)
                
                # 验证是否所有目标都找到了
                if len(orgins_copy) > 0:
                    raise Exception(f"未找到地区：{'、'.join(orgins_copy)}")
            
            # 点击应用按钮
            ApplyCountryBtn = '//button[contains(@data-takt-id, "country:apply")]'
            # web_page.wait_appear(web_page.find_by_xpath(XPath.Apply_button),timeout =20)
            web_page.find_by_xpath(ApplyCountryBtn, timeout=5).click()
            # 等待数据刷新完成
            wait_data_refresh_completed(web_page, timeout=60)
    
    # 第四步：设置广告活动状态筛选（如果提供了状态参数）
    if status is not None:
        if wait_for_element_by_xpath(web_page, XPath.FilterBy, timeout=2):
            # 点击筛选条件按钮
            web_page.find_by_xpath(XPath.FilterBy).click()
            sleep(1)
            
            # 点击进行中（状态）选项
            web_page.find_by_xpath(XPath.StateOption).click()
            sleep(1)
            
            # 选择状态
            select_campaign_status(web_page, status)
            
            # 点击应用按钮（需要根据实际页面调整XPath）
            try:
                ApplyStatusBtn = '//button[contains(@id,"state:apply")]'
                web_page.find_by_xpath(ApplyStatusBtn, timeout=5).click()

                # 等待数据刷新完成
                wait_data_refresh_completed(web_page, timeout=60)
            except:
                # 如果上面的XPath找不到，尝试其他可能的XPath
                try:
                    ApplyStatusBtn = '//button[contains(text(), "应用") or contains(text(), "Apply")]'
                    web_page.find_by_xpath(ApplyStatusBtn).click()
                    # 等待数据刷新完成
                    wait_data_refresh_completed(web_page, timeout=60)
                except:
                    print("未找到应用按钮，可能已自动应用")
                    # 即使没有找到应用按钮，也等待一下数据刷新
                    wait_data_refresh_completed(web_page, timeout=60)
            print(f"已选择广告活动状态: {status}")

    # 第五步：设置点击数筛选（如果提供了点击数）
    if clicks_num != 0:
        if wait_for_element_by_xpath(web_page, XPath.FilterBy, timeout=2):
            # 点击筛选条件按钮
            web_page.find_by_xpath(XPath.FilterBy).click()
            sleep(1)
            
            # 点击 点击量 选项
            web_page.find_by_xpath(XPath.Click_xpath).click()
            sleep(1)
            
            # 填写数量
            web_page.find_by_xpath(XPath.Click_frame).input(clicks_num)
            
            # 点击应用按钮（需要根据实际页面调整XPath）
            try:
                ApplyClickBtn = '//button[contains(@id,"clicks:apply")]'
                web_page.find_by_xpath(ApplyClickBtn, timeout=5).click()

                # 等待数据刷新完成
                wait_data_refresh_completed(web_page, timeout=60)
            except:
                # 如果上面的XPath找不到，尝试其他可能的XPath
                try:
                    ApplyStatusBtn = '//button[contains(text(), "应用") or contains(text(), "Apply")]'
                    web_page.find_by_xpath(ApplyStatusBtn).click()
                    # 等待数据刷新完成
                    wait_data_refresh_completed(web_page, timeout=60)
                except:
                    print("未找到应用按钮，可能已自动应用")
                    # 即使没有找到应用按钮，也等待一下数据刷新
                    wait_data_refresh_completed(web_page, timeout=60)
            print(f"已筛选点击量: 大于{clicks_num}")

def get_campaigns(web_page: WebBrowser, file_folder: str, file_name: str, start_date: Optional[str] = None, end_date: Optional[str] = None, orgins: Optional[list] = None, status: Optional[str] = None, clicks_num:int = 0):
    """
    获取广告活动数据文件
    
    参数:
        web_page: 浏览器对象
        file_folder: 文件保存文件夹路径
        file_name: 文件名
        start_date: 开始日期，格式 "YYYY-MM-DD"，可选
        end_date: 结束日期，格式 "YYYY-MM-DD"，可选
        orgins: 国家/地区列表，可选，如果包含"全选"则全选所有国家
        status: 广告活动状态，可选（如 "已启用"、"已暂停"、"已存档"、"全部" 等）
    
    返回:
        下载的文件路径
    """
    # 进入广告页
    domain = get_ad_domain(web_page)
    url = f"{domain}/campaign-manager"
    to_campaigns_page_if_need(web_page, url)
    
    # 设置过滤参数
    set_campaigns_params(web_page, start_date=start_date, end_date=end_date, orgins=orgins, status=status, clicks_num=clicks_num)
    
    # 导出数据
    from pathlib import Path
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    
    # 点击导出按钮
    web_page.find_by_xpath(XPath.Export).click()
    sleep(1)
    try:
        # 点击下载
        web_page.find_by_xpath('//button[contains(@id,"export")][contains(text(),"下载") or contains(text(),"Download")]', timeout=3).click()
    except:
        pass
    # 使用 download_handler 处理下载和紫鸟弹窗
    download_file_path = download_handler(web_page, str(file_folder), file_name)
    
    return download_file_path


def test_run():
    if "xbot_extensions" in __file__:
        return
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    # web_page.find_by_xpath(XPath.CampaignDate).click(simulative=False)
    file_folder = r"C:\Users\30231\Desktop\2026年03月26日"
    file_name = "campaigns"
    start_date = "2025-10-01"
    end_date = "2025-11-30"
    orgins = ["美国", "加拿大"]
    status = "已启用"
    
    file_path = get_campaigns(
        web_page,
        file_folder=file_folder,
        file_name=file_name,
        start_date=start_date,
        end_date=end_date,
        orgins=orgins,
        status=status
    )
    print(f"文件下载完成: {file_path}")
    exit()


def main(args):
    # 测试代码入口
    # test_run()
    
    # 业务代码入口
    web_page = args.get("web_page")
    file_folder = args.get("file_folder")
    file_name = args.get("file_name")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    orgins = args.get("orgins")
    status = args.get("status")
    clicks_num = args.get('clicks_num')
    
    # 参数校验
    if not file_folder:
        raise Exception("缺少参数: file_folder")
    if not file_name:
        raise Exception("缺少参数: file_name")
    
    # 处理 orgins 参数（字符串转列表）
    if orgins:
        if isinstance(orgins, str):
            orgins = [orgins]
        if not isinstance(orgins, list):
            raise Exception(f"地区参数错误：{orgins}")
        orgins = list(set(orgins))  # 去重
    
    # 获取广告活动数据文件
    file_path = get_campaigns(
        web_page,
        file_folder=file_folder,
        file_name=file_name,
        start_date=start_date,
        end_date=end_date,
        orgins=orgins,
        status=status,
        clicks_num=clicks_num
    )
    
    # 将结果保存到args中
    args['file_path'] = file_path
