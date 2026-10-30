# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement
from pathlib import Path
from .utils import get_ad_domain
from .download_utils import download_handler


# ============ 国家映射表 ============
# code -> [中文名, 英文全称]
COUNTRY_MAP = {
    "US": ["美国", "United States"],
    "CA": ["加拿大", "Canada"],
    "MX": ["墨西哥", "Mexico"],
    "BR": ["巴西", "Brazil"],
    "GB": ["英国", "United Kingdom"],
    "DE": ["德国", "Germany"],
    "FR": ["法国", "France"],
    "IT": ["意大利", "Italy"],
    "ES": ["西班牙", "Spain"],
    "NL": ["荷兰", "Netherlands"],
    "SE": ["瑞典", "Sweden"],
    "PL": ["波兰", "Poland"],
    "BE": ["比利时", "Belgium"],
    "IE": ["爱尔兰", "Ireland"],
    "TR": ["土耳其", "Turkey"],
    "JP": ["日本", "Japan"],
    "AU": ["澳大利亚", "Australia"],
    "SG": ["新加坡", "Singapore"],
    "IN": ["印度", "India"],
    "AE": ["阿联酋", "United Arab Emirates"],
    "SA": ["沙特阿拉伯", "Saudi Arabia"],
    "ZA": ["南非", "South Africa"],
    "EG": ["埃及", "Egypt"],
}

# 反向索引：中文名 / 英文全称 / 英文小写 / code(大小写) -> code
_COUNTRY_NAME_TO_CODE = {}
for _code, (_zh, _en) in COUNTRY_MAP.items():
    _COUNTRY_NAME_TO_CODE[_zh] = _code
    _COUNTRY_NAME_TO_CODE[_en] = _code
    _COUNTRY_NAME_TO_CODE[_en.lower()] = _code
    _COUNTRY_NAME_TO_CODE[_code] = _code
    _COUNTRY_NAME_TO_CODE[_code.lower()] = _code


def normalize_country_code(country_name: str) -> str:
    """
    将国家名称（中文/英文全称/英文小写/国家code）统一转换成国家 code
    例如: "加拿大" -> "CA", "Canada" -> "CA", "canada" -> "CA", "ca" -> "CA"
    """
    if not country_name:
        raise ValueError("country_name 不能为空")
    key = str(country_name).strip()
    code = _COUNTRY_NAME_TO_CODE.get(key) or _COUNTRY_NAME_TO_CODE.get(key.lower())
    if not code:
        raise ValueError(f"未识别的国家名称: {country_name}")
    return code


class XPath:
    # 国家按钮
    CountryButton = '//button[@id="aac-chrome-trigger"]'
    # 国家选择（用 value=国家code 定位，与显示语言无关）
    CountrySelect = '//button[@value="{country_code}" and @role="option"]'
    # 兜底：按显示文本定位（中文/英文）
    CountrySelectByText = '//button/div[normalize-space(.)="{country_text}"]'
    # 确认按钮
    ConfirmButton = '//button[@id="aac-chrome-change-country-button"]'
    # 输入框取消按钮
    SearchCancelButton = '//button[@data-takt-id="storm-ui-close-button"]'
    # 输入框
    SearchInput = '//div[normalize-space(.)="Search"]/div[normalize-space(.)="Search"]/div[normalize-space(.)="Search"]/div'
    # 第一行下载按钮
    FirstRowDownloadBtn = '//div[@row-index="0"]//a[contains(@href, "/download-report/")]'


def to_reports_page_if_needed(web_page: WebBrowser, url: str):
    """
    如果需要，导航到报告页面
    """
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    web_page.navigate(url, load_timeout=300)
    sleep(2)  # 等待页面加载


def select_country(web_page: WebBrowser, country_name: str):
    """
    选择国家

    country_name 支持：
        - 中文名：如 "加拿大"
        - 英文全称：如 "Canada"
        - 英文小写：如 "canada"
        - 国家 code：如 "CA"

    页面无论显示中文还是英文，都能正确定位（优先用 value=code 定位）
    """
    # 入参 -> 国家 code
    country_code = normalize_country_code(country_name)

    # 1. 点击国家按钮
    try:
        country_button = web_page.find_by_xpath(XPath.CountryButton, timeout=10)
        country_button.click()
        sleep(1)
    except Exception as e:
        raise Exception(f"点击国家按钮失败: {e}")

    # 2. 选择国家：优先按 value=code 定位，失败则按显示文本兜底
    clicked = False

    # 2.1 优先按 value=code 定位（不受中英文显示影响）
    try:
        country_xpath = XPath.CountrySelect.format(country_code=country_code)
        country_option = web_page.find_by_xpath(country_xpath, timeout=5)
        country_option.click()
        clicked = True
        sleep(1)
    except Exception:
        clicked = False

    # 2.2 兜底：按显示文本（中文 / 英文全称）定位
    if not clicked:
        zh, en = COUNTRY_MAP[country_code]
        for text in (zh, en):
            try:
                text_xpath = XPath.CountrySelectByText.format(country_text=text)
                web_page.find_by_xpath(text_xpath, timeout=5).click()
                clicked = True
                sleep(1)
                break
            except Exception:
                continue

    if not clicked:
        raise Exception(f"选择国家失败，国家: {country_name}(code={country_code})")

    # 3. 点击确认按钮
    try:
        confirm_button = web_page.find_by_xpath(XPath.ConfirmButton, timeout=10)
        confirm_button.click()
        sleep(2)  # 等待页面刷新
    except Exception as e:
        raise Exception(f"点击确认按钮失败: {e}")


def search_report(web_page: WebBrowser, report_name: str):
    """
    搜索报告
    """
    # 1. 检查是否有输入框取消按钮，如果有则点击
    try:
        cancel_button = web_page.find_by_xpath(XPath.SearchCancelButton, timeout=5)
        if cancel_button:
            cancel_button.click()
            sleep(0.5)
    except Exception:
        # 没有取消按钮，继续
        pass

    # 2. 在输入框输入报告名称
    try:
        search_input = web_page.find_by_xpath(XPath.SearchInput, timeout=10)
        search_input.click()
        sleep(0.5)
        search_input.input(report_name)
        sleep(2)  # 等待自动搜索完成
    except Exception as e:
        raise Exception(f"输入报告名称失败: {e}")


def find_and_download_report(web_page: WebBrowser, file_folder: str, file_name: str, timeout: int = 300, dialog_timeout: int = 20):
    """
    查找并下载第一行报告
    重试3次，如果没有则返回None
    """
    download_btn = None

    # 重试3次查找下载按钮
    for retry in range(3):
        try:
            download_btn = web_page.find_by_xpath(XPath.FirstRowDownloadBtn, timeout=5)
            if download_btn:
                break
        except Exception:
            if retry < 2:  # 不是最后一次重试
                sleep(2)  # 等待一下再重试
                continue
            else:
                # 最后一次重试失败
                print("未找到可下载的报告（重试3次后）")
                return None

    # 如果没有找到下载按钮，返回None
    if not download_btn:
        print("未找到可下载的报告")
        return None

    # 判断报告是否可以下载（检查链接是否存在且可点击）
    try:
        href = download_btn.get_attribute("href")
        if not href or "/download-report/" not in href:
            print("报告链接无效，无法下载")
            return None
    except Exception as e:
        print(f"检查报告链接失败: {e}")
        return None

    # 下载报告
    try:
        file_path = download_handler(
            web_page,
            download_btn,
            file_folder,
            file_name,
            wait_time=timeout,
            dialog_timeout=dialog_timeout
        )
        return file_path
    except Exception as e:
        raise Exception(f"下载报告失败: {e}")


def download_sponsored_report(
    web_page: WebBrowser,
    country_name: str,
    report_name: str,
    file_folder: str,
    file_name: str,
    timeout: int = 300,
    dialog_timeout: int = 20
):
    """
    下载广告报告

    参数:
        web_page: 浏览器对象
        country_name: 国家名称（支持中文名 / 英文全称 / 英文小写 / 国家code）
        report_name: 报告完整名称
        file_folder: 下载文件夹路径
        file_name: 文件名
        timeout: 下载超时时间（秒）
        dialog_timeout: 对话框超时时间（秒）

    返回:
        文件路径（如果下载成功），否则返回None
    """
    # 创建下载文件夹
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 进入报告页面
    domain = get_ad_domain(web_page)
    url = f"{domain}/reports"
    to_reports_page_if_needed(web_page, url)

    # 1. 选择国家
    select_country(web_page, country_name)

    # 2. 搜索报告
    search_report(web_page, report_name)

    # 3. 查找并下载第一行报告
    file_path = find_and_download_report(web_page, str(file_folder), file_name, timeout, dialog_timeout)

    return file_path


def test_download_report():
    """
    测试函数
    """
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser")
    country_name = "Canada"   # 也可传 "Canada" / "canada" / "CA"
    report_name = "adtest"    # 报告完整名称
    file_folder = r"C:\Users\yingdao\Desktop"
    file_name = "adtest"
    timeout = 300
    dialog_timeout = 20

    file_path = download_sponsored_report(
        web_page,
        country_name,
        report_name,
        file_folder,
        file_name,
        timeout,
        dialog_timeout
    )

    if file_path:
        print(f"报告下载完成: {file_path}")
    else:
        print("未找到可下载的报告")

    exit()


def main(args):
    """
    主函数入口
    """
    # 测试代码入口
    test_download_report()

    # 业务代码入口
    web_page = args.get("web_page")
    country_name = args.get("country_name")  # 国家名称（中文/英文/英文小写/国家code 均可）
    report_name = args.get("report_name")    # 报告完整名称
    file_folder = args.get("file_folder")    # 下载文件夹路径
    file_name = args.get("file_name")        # 文件名
    timeout = args.get("timeout", 300)       # 下载超时时间
    dialog_timeout = 60

    # 参数校验
    if not country_name:
        raise Exception("缺少参数: country_name")
    if not report_name:
        raise Exception("缺少参数: report_name")
    if not file_folder:
        raise Exception("缺少参数: file_folder")
    if not file_name:
        raise Exception("缺少参数: file_name")

    # 处理超时参数：确保是有效的整数（处理空字符串、None等情况）
    try:
        if timeout is None or timeout == "":
            timeout = 300
        timeout = int(timeout)
    except (ValueError, TypeError):
        timeout = 300  # 默认值

    # 下载报告
    file_path = download_sponsored_report(
        web_page,
        country_name,
        report_name,
        file_folder,
        file_name,
        timeout,
        dialog_timeout
    )

    # 将结果保存到args中
    args['file_path'] = file_path