# 模板

import xbot
import re
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime


# 所有元素Xpath路径
class Xpath:
    Message_list = '//a[contains(@class, "case-list-item")]'
    Message_Title = ".//span[contains(@class, 'buyer-name')]"
    Message_Content = ".//span[contains(@class, 'subject')]"
    Message_Status = "(.//span[contains(@class, 'case-status-label')] | .//div[contains(@class, 'case-status-badge')])[1]"
    Message_Time = ".//kat-badge[contains(@class, 'nearing-sla')] | .//div[contains(@class, 'badge-text')]"
    Next_Button = "//a[contains(@class, 'next-icon') and not(contains(@class, 'disabled-link'))]"
    Dis_Next_Button = "//a[contains(@class, 'next-icon') and contains(@class, 'disabled-link')]"
    No_Message = "//*[@id='no-messages-header']"
    Site_Info = '//a[contains(@class, "case-list-item")]//*[@class="buyer-lop-country"]/kat-flag[@country]'

# 构建所有需要用到的元素
class Element:
    next_button = create_selector(Xpath.Next_Button,  name='下一页')
    no_message = create_selector(Xpath.No_Message,name ='无需回复消息')



def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")


def gen_selector(xpath: str) -> Selector:
    xpaths = xpath.split(">>")
    # print(xpaths)
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector


def to_page_if_needed(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)



#数据获取
def Message_Content_Data(web_page: WebBrowser, max_pages: int = 0, site: str = 'None'):

    # 1. 初始化一个列表和页数计数器
    all_message_data = []
    current_page = 1
    
    # 等待页面加载完成
    sleep(2)
    
    # 2. 首先检查是否存在"无消息"的提示
    try:
        is_messages_element = web_page.wait_appear(Element.no_message, timeout=3)
        if is_messages_element:
            print("没有需要回复的消息")
            return all_message_data  # 返回一个空列表
    except Exception:
        pass  # 如果没有找到"无消息"元素，说明可能有消息，继续执行
    
    # 3. 执行循环和翻页逻辑
    while True:
        # 增加等待时间，确保元素加载完成
        sleep(1)
        
        # 尝试查找消息列表元素，增加超时时间
        message_elements = web_page.find_all_by_xpath(Xpath.Message_list, timeout=5)
        
        if not message_elements:
            # 如果第一页找不到元素，再等待一下重试
            if current_page == 1:
                print("首次查找消息列表失败，等待页面加载后重试...")
                sleep(3)
                message_elements = web_page.find_all_by_xpath(Xpath.Message_list, timeout=5)
                if not message_elements:
                    print("重试后仍未找到消息列表元素，可能页面确实没有数据")
                    break
            else:
                print(f"第 {current_page} 页未找到消息列表，可能已到达最后一页")
                break
        
        print(f"第 {current_page} 页找到 {len(message_elements)} 条消息")
        count_failures = 0
        max_failures = len(message_elements)  # 允许失败的数量等于元素数量，避免过早退出

        for idx, element in enumerate(message_elements, 1):
            try:
                # 增加超时时间，确保元素加载完成
                send_name = element.find_by_xpath(Xpath.Message_Title, timeout=3).get_text()
                send_content = element.find_by_xpath(Xpath.Message_Content, timeout=3).get_text()
                send_status = element.find_by_xpath(Xpath.Message_Status, timeout=3).get_text()
                
                if site != 'None':
                    send_site = element.find_by_xpath(Xpath.Site_Info, timeout=3).get_attribute("country")
                    if send_site == site.upper():
                        message_item = {
                            "发件人": send_name,
                            "主题": send_content,
                            "状态": send_status
                        }
                else:
                    message_item = {
                        "发件人": send_name,
                        "主题": send_content,
                        "状态": send_status
                    }

                try:
                    # --- 修改开始：兼容处理"到期时间" ---
                    
                    # 1. 尝试查找元素
                    time_element = element.find_by_xpath(Xpath.Message_Time, timeout=2)
                    
                    raw_time_text = ""
                    
                    # 2. 判断获取方式：优先尝试获取文本（新版），如果为空则尝试获取属性（旧版）
                    text_content = time_element.get_text()
                    attr_content = time_element.get_attribute('label')

                    if text_content and ("到期" in text_content or "Time" in text_content):
                        # 命中新版：<div class="badge-text">到期时间：15 小时</div>
                        raw_time_text = text_content
                    elif attr_content:
                        # 命中旧版：<kat-badge label="到期时间：xxx">
                        raw_time_text = attr_content
                    
                    # 3. 数据清洗
                    if raw_time_text:
                        # 替换全角冒号为半角，防止 split 失败
                        clean_text = raw_time_text.replace('：', ':')
                        
                        if ':' in clean_text:
                            # 分割取出冒号后面的部分
                            key, value = clean_text.split(':', 1)
                            message_item["到期时间"] = value.strip()
                        else:
                            # 如果没有冒号，直接存整个文本
                            message_item["到期时间"] = raw_time_text.strip()
                    else:
                        message_item["到期时间"] = "无"

                except Exception as e:
                    # 找不到元素或处理出错
                    message_item["到期时间"] = "无"
                    
                all_message_data.append(message_item)
                print(f"  成功抓取第 {idx} 条消息: {send_name} - {send_content[:30]}...")
                # 重置计数器
                count_failures = 0
                
            except Exception as e:
                count_failures += 1
                print(f"  第 {idx} 条消息抓取失败: {str(e)}")
                # 只有在连续失败超过阈值时才退出
                if count_failures >= max_failures:
                    print(f"连续 {max_failures} 条消息抓取失败，停止处理当前页 ---")
                    break
                continue

        # 处理翻页
        try:
            # 检查是否达到了最大页数限制
            if max_pages > 0 and current_page >= max_pages:
                print(f"已达到指定的最大页数 {max_pages}，停止翻页。")
                break
                
            # 检查是否存在可点击的下一页按钮
            if web_page.wait_appear(Element.next_button, timeout=3):
                web_page.find(Element.next_button).click()
                current_page += 1  # 页数计数器加1
                print(f"点击下一页，准备加载第 {current_page} 页...")
                sleep(3)  # 增加等待时间，确保新页面加载完成
            else:
                print("未找到可点击的'下一页'按钮，已到达最后一页。")
                break
        except Exception as e:
            print(f"查找'下一页'按钮时出错: {str(e)}，已到达最后一页。")
            break
            
    # 4. 所有页面处理完毕，打印最终结果
    if all_message_data:
        print(f"总计获取到 {len(all_message_data)} 条信息。（共处理了 {current_page} 页）")
    else:
        print("执行完成，未抓取到任何信息。")
        print("提示：请检查页面是否正确加载，或XPath选择器是否需要更新。")
    
    return all_message_data

# 整个业务操作流程
def process_method(web_page: WebBrowser, max_pages: int = 0, site: str = 'None'):

    # 步骤1: 准备目标URL并调用函数，确保页面在邮件页面
    domain = get_domain(web_page)
    url = f"{domain}/messaging/inbox?fi=responseNeeded"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    dataList = Message_Content_Data(web_page, max_pages, site)
    return dataList


def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    data1 = process_method(web_page,max_pages = 4)
    print(data1)
    exit()


def main(args):
    # test_run()
    web_page = args.get("web_page")
    max_pages = args.get("max_pages", 0)  # 获取最大页数参数，默认为0
    site = args.get("site") or "None"
    result_list = process_method(web_page, max_pages, site)
    args["data"] = result_list


