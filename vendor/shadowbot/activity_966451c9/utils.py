# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from win32 import win32api, win32gui, win32print
from win32.lib import win32con
import win32clipboard as w


def main(args):
    # aaa = scaling()
    # print(aaa)
    read_text()
    pass


def date_year_select(year_ele:xbot.web.WebElement, select_text, year_pre_ele, year_next_ele):
    
    year_ele_text = year_ele.get_text()
    year_ele_text = "".join(filter(str.isdigit, year_ele_text))

    click_ele = None

    if  int(year_ele_text) == int(select_text):
        return

    if  int(year_ele_text) > int(select_text):
        click_ele = year_pre_ele
    else:
        click_ele = year_next_ele

    while True:
        click_ele.click()

        year_ele_text = year_ele.get_text()
        year_ele_text = "".join(filter(str.isdigit, year_ele_text))

        if year_ele_text == str(select_text):
            break


#电脑的显示缩放比例
def scaling():
    """获取缩放后的分辨率"""
    sX = win32api.GetSystemMetrics(0)   #获得屏幕分辨率X轴
    sY = win32api.GetSystemMetrics(1)   #获得屏幕分辨率Y轴
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)  # 横向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)  # 纵向分辨率
    # 缩放比率
    screen_scale_rate = round(w / sX, 2)
    return screen_scale_rate

#商家体验分
def MerchantExperienceScore(json_data):

    result_dict = {}
    shop_analysis_list = json_data["shop_analysis"]
    for shop_analysis in shop_analysis_list:
        title = shop_analysis["title"]
        value = str(shop_analysis["value"]["value_figure"]*100)+"%"
        rise_than_yesterday = shop_analysis["compare_with_self"]["rise_than_yesterday"]
        than_yesterday = ""
        if rise_than_yesterday > 0:
            than_yesterday = "较昨日上涨"+str(rise_than_yesterday*100)+"%"
        else:
            than_yesterday = "较昨日下降"+str(int(rise_than_yesterday)*100)+"%"

        surpass_peers = "超越同行"+str(shop_analysis["surpass_peers"]["value_figure"]*100)+"%"

        result_dict[title] = [value,than_yesterday,surpass_peers]
    return result_dict

def read_text():
    """
    读取剪切板中的文本内容
    :return: str 剪切板文本内容，如果失败返回None
    """
    try:
        w.OpenClipboard()
        if w.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            data = w.GetClipboardData(win32con.CF_UNICODETEXT)
            w.CloseClipboard()
            return data
        else:
            w.CloseClipboard()
            return None
    except Exception as e:
        print(f"读取剪切板文本失败: {e}")
        try:
            w.CloseClipboard()
        except:
            pass
        return None

def write(text: str, verify: bool = True, max_retry: int = 3):
    """
    将文本写入剪切板，并可选择校验
    :param text: 要写入的文本内容
    :param verify: 是否校验写入结果，默认True
    :param max_retry: 最大重试次数，默认3次
    :return: bool 写入是否成功
    """
    for attempt in range(max_retry):
        try:
            w.OpenClipboard()
            w.EmptyClipboard()
            w.SetClipboardData(win32con.CF_UNICODETEXT, text)
            w.CloseClipboard()
            
            # 校验写入内容
            if verify:
                sleep(0.05)  # 短暂等待确保剪切板更新
                clipboard_content = read_text()
                if clipboard_content == text:
                    print(f"剪切板内容校验成功 (尝试次数: {attempt + 1})")
                    return True
                else:
                    print(f"剪切板内容校验失败 (尝试次数: {attempt + 1})")
                    print(f"期望内容: {text[:50]}{'...' if len(text) > 50 else ''}")
                    print(f"实际内容: {clipboard_content[:50] if clipboard_content else 'None'}{'...' if clipboard_content and len(clipboard_content) > 50 else ''}")
                    if attempt < max_retry - 1:
                        sleep(0.1)  # 重试前等待
                        continue
                    else:
                        raise Exception(f"剪切板内容写入校验失败，已重试{max_retry}次")
            else:
                return True
                
        except Exception as e:
            print(f"写入剪切板失败 (尝试次数: {attempt + 1}): {e}")
            try:
                w.CloseClipboard()
            except:
                pass
            if attempt < max_retry - 1:
                sleep(0.1)
                continue
            else:
                raise Exception(f"剪切板写入失败，已重试{max_retry}次: {e}")
    
    return False


def get_active_by_web_page(web_page):
    if not web_page:
        return "Google Chrome"
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return product_name
