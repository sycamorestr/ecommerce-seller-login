# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

import uuid
import datetime

from xbot.selector import Selector


def gen_selector(xpath):
    if isinstance(xpath, str):
        xpath = [xpath]
    uid = str(uuid.uuid4())
    data = {'id': uid, 'name': uid, 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpath}}
    return Selector(data)
    
def select_date_in_picker(web_page, target_date: str) -> None:
    date_control = '//button/span[text()="日"]'
    date_picker_panel = '(//*[@class="oui-date-picker-menu-v2  oui-date-picker-period-panel"])[1]'

    target_year, target_month, target_day = map(int, target_date.split('-'))

    # 打开日期面板
    # web_page.find_by_xpath(date_control, timeout=10).click(delay_after=1)
    panel = web_page.find_by_xpath(date_picker_panel, timeout=10)

    def get_current_year_month():
        year = int(
            panel.find_by_xpath('.//span[@data-role="current-year"]', timeout=5)
            .get_text()
            .replace('年', '')
        )
        month = int(
            panel.find_by_xpath('.//span[@data-role="current-month"]', timeout=5)
            .get_text()
            .replace('月', '')
        )
        return year, month

    def month_index(y, m):
        return y * 12 + (m - 1)

    target_index = month_index(target_year, target_month)

    # === 核心：循环校验直到年月正确 ===
    MAX_LOOP = 48  # 最多允许滚动 4 年，防死循环
    loop = 0

    while True:
        current_year, current_month = get_current_year_month()
        current_index = month_index(current_year, current_month)

        if current_index == target_index:
            break  # ✅ 月份稳定，退出

        if loop >= MAX_LOOP:
            raise RuntimeError(
                f"月份切换异常，当前 {current_year}-{current_month}，目标 {target_year}-{target_month}"
            )

        # 根据实时状态决定方向（防止 12 → 1 → 12 抖动）
        if current_index < target_index:
            btn_xpath = './/span[@data-role="next-month"]'
        else:
            btn_xpath = './/span[@data-role="prev-month"]'

        panel.find_by_xpath(btn_xpath, timeout=5).click(delay_after=0.8)
        loop += 1

    # === 点击目标日期 ===
    target_value = f"{target_year:04d}-{target_month:02d}-{target_day:02d}"
    date_cells = web_page.find_all_by_xpath('.//td[@data-role="date"]', timeout=5)

    for cell in date_cells:
        if cell.get_attribute('data-value') == target_value:
            cell.click(delay_after=0.3)
            return

    raise ValueError(f"未能找到目标日期 {target_date}")


def main(args):
    select_date_in_picker(xbot.web.get_active("chrome"), "2026-01-02")
    pass
