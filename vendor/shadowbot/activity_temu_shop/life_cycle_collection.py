# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import re
import math
import time
import json

import xbot
from xbot import print, sleep
from xbot.app import databook
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler

import threading

def To_tbody_top(web_page):
    """将数据滚动都顶部"""
    script = """
        function (element, input) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'start'});
        }
    """
    web_page.find_by_xpath('(//table/tbody/tr)[1]').execute_javascript(script)



def life_cycle_collection(web_page, product_state):
    """商品管理-生命周期数据采集"""

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

            sleep(interval) # 间隔等待
    
    # 设置线程
    confirm_thread = threading.Thread(
        target=wait_saler_center,
        kwargs={
            "url": 'authentication',
        },
        daemon=True
    )
    # 启动线程
    confirm_thread.start()

    try:
        return _collect_life_cycle_rows(web_page, product_state)
    finally:
        is_completed = True
        confirm_thread.join(timeout=5)


def _iter_life_cycle_rows(web_page, data_xpath, page_number):
    """批量读取每屏文本，以持续无新增SKU收敛，兼容页尾滚动回弹。"""
    seen = set()
    quiet_since = None
    no_new_rounds = 0
    read_script = r'''function(element, input) {
        const text = node => node ? node.innerText.trim() : '';
        return JSON.stringify(Array.from(element.children).filter(r =>
            r.matches('tr[data-testid="beast-core-table-body-tr"]')).map(r => {
            const cells = Array.from(r.children).filter(c => c.tagName === 'TD');
            const sku = r.querySelectorAll('span[class*="use-columns_skuId__"]');
            const info = cells[1];
            const ellipsis = info && info.querySelector('div[data-testid="beast-core-ellipsis"]');
            return {cells: cells.map(text), sku_count: sku.length,
                sku: text(sku[0]),
                control: Array.from(r.querySelectorAll('a[data-testid="beast-core-button-link"] span'))
                    .some(s => ['收起', '展开剩余'].includes(text(s))),
                name: text(info && info.querySelector('div[class*="product-info_productName"]')),
                category: text(ellipsis && ellipsis.nextElementSibling),
                spu: text(info && info.querySelector('div[class*="product-info_nameBlock"]'))};
        }));
    }'''
    scroll_script = '''function(element, input) {
        let node = element;
        while (node && !(node.clientHeight > 0 && node.scrollHeight > node.clientHeight + 2 &&
                /auto|scroll|overlay/.test(getComputedStyle(node).overflowY))) node = node.parentElement;
        node = node || document.scrollingElement;
        if (!node || !node.clientHeight) throw new Error('未找到有效的垂直滚动容器');
        const before = node.scrollTop;
        const max = Math.max(0, node.scrollHeight - node.clientHeight);
        node.scrollTop = Math.min(max, before + Math.max(1, node.clientHeight * 0.8));
        return JSON.stringify({before: before, after: node.scrollTop, max: max});
    }'''
    for batch in range(1000):
        started = time.monotonic()
        Tools.wait_loading(web_page, appear_time=0)
        expand_xpath = data_xpath + '//a[@data-testid="beast-core-button-link"][span[text()="展开剩余"]]'
        for attempt in range(1000):
            buttons = web_page.find_all_by_xpath(expand_xpath, timeout=0)
            if not buttons:
                break
            buttons[0].click()
            Tools.wait_loading(web_page, appear_time=0)
        else:
            raise RuntimeError('第{}页展开SKU未收敛'.format(page_number))

        tbody = web_page.find_by_xpath('//tbody[@data-testid="beast-core-table-middle-tbody"]')
        rows = json.loads(tbody.execute_javascript(read_script))
        if not isinstance(rows, list) or not rows:
            raise RuntimeError('第{}页第{}轮懒加载表格为空或类型异常'.format(page_number, batch + 1))
        before_count = len(seen)
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('cells'), list):
                raise ValueError('第{}页行结构无效：{!r}'.format(page_number, row))
            if row.get('control') and row.get('sku_count') == 0:
                continue
            sku = row.get('sku', '')
            if row.get('sku_count') != 1 or not sku.isdigit():
                raise ValueError('第{}页SKU无效：{!r}'.format(page_number, row))
            # 重复主行仅用于恢复共享字段，重复子行直接跳过。
            if sku in seen and len(row['cells']) <= 3:
                continue
            seen.add(sku)
            yield row
        position = json.loads(tbody.execute_javascript(scroll_script))
        if not isinstance(position, dict) or any(
                not isinstance(position.get(k), (int, float)) for k in ('before', 'after', 'max')):
            raise ValueError('第{}页滚动状态无效：{!r}'.format(page_number, position))
        added = len(seen) - before_count
        # 页面回弹也会产生位移，只有新SKU才能重置无新增计时。
        if added:
            quiet_since = None
            no_new_rounds = 0
        else:
            no_new_rounds += 1
            if quiet_since is None:
                quiet_since = time.monotonic()
        quiet = 0 if quiet_since is None else time.monotonic() - quiet_since
        print('第{}页第{}屏：新增SKU={}，累计={}，滚动={:.0f}/{:.0f}，耗时={:.2f}s，连续无新增={}轮/{:.1f}s'.format(
            page_number, batch + 1, added, len(seen), position['after'], position['max'],
            time.monotonic() - started, no_new_rounds, quiet))
        if no_new_rounds >= 5 and quiet >= 5:
            print('第{}页连续{}轮/{:.1f}秒无新增SKU，结束当前页（不要求滚动条严格到底）；累计{}条'.format(
                page_number, no_new_rounds, quiet, len(seen)))
            return
        sleep(0.3)
    raise RuntimeError('第{}页懒加载超过1000轮，停止采集'.format(page_number))


def _collect_life_cycle_rows(web_page, product_state):
    # 判断是否在目标页面
    Tools.check_target_web(web_page, "newon/product-select")

    # 等待页面加载完毕
    web_page.wait_load_completed()

    # 获取快速筛选信息
    fast_select_xpath = '//div[contains(@class,"use-quick-field_tsx_container")]/div[text()="快速筛选"]/following-sibling::div//div[contains(@style,"rgb")]'
    fast_select_ele = web_page.find_all_by_xpath(fast_select_xpath, timeout=2)
    if len(fast_select_ele) > 0:

        # 消除信息框
        Tools.handle_info(web_page)
        
        for rgb in fast_select_ele:
            rgb.click()

    # 等待数据加载完毕
    Tools.wait_loading(web_page, appear_time=0)
    sleep(0.3)

    # 获取商品状态数量
    product_num_xpath = f'(//div[contains(text(),"{product_state}")])[1]'
    product_num = web_page.find_by_xpath(product_num_xpath).get_text()
    num = re.search(r'(\d+)', product_num, re.S).group(1)

    # 若没有数据则返回
    if num == "0":
        xbot.logging.info(f'当前店铺的{product_state}状态无商品')
        return 

    # 存储数据列表
    return_data = []

    # 点击目标状态
    web_page.find_by_xpath(product_num_xpath).click()

    # 获取表头信息
    ths = web_page.find_all_by_xpath('//thead/tr[1]/th/span')
    th_list = [th.get_text() for th in ths[2:-1]]
    th_list.insert(0,'商品简介')
    th_list.insert(1,'类目')
    th_list.insert(2,'SPU')
    return_data.append(th_list)
    
    # 关闭评价弹窗
    if len(web_page.find_all_by_xpath('//div[contains(@class,"satisfaction-score_title")]//*[@data-testid="beast-core-icon-close"]', timeout=0)) > 0:
        web_page.find_all_by_xpath('//div[contains(@class,"satisfaction-score_title")]//*[@data-testid="beast-core-icon-close"]', timeout=0)[0].click()

    # 点击页码选择框
    page_frame_xpath = '//div[contains(@class,"TB_bottomRight")]//div[@data-testid="beast-core-input-suffix"]'
    web_page.find_by_xpath(page_frame_xpath).click()

    # 进行页码选择
    page_xpath = '//ul[@role="listbox"]/li/span[text()=100]'
    web_page.find_by_xpath(page_xpath).click()

    # 获取总数据条数
    total_num_xpath = '//div[contains(@class,"TB_bottomRight")]//li[contains(@class,"PGT_totalText")]'
    total_num_text = web_page.find_by_xpath(total_num_xpath).get_text()
    total_num = re.search(r'(\d+)', total_num_text, re.S).group(1)

    if total_num == '0':
        return 

    # 获取循环次数
    page = math.ceil(int(total_num) / 100)

    seen_skus = set()
    for page_index in range(page):
        tmp_row_data = []
        page_products = set()
        main_row_cache = {}
        Tools.wait_loading(web_page, appear_time=0)

        data_xpath = '//tbody[@data-testid="beast-core-table-middle-tbody"]/tr[@data-testid="beast-core-table-body-tr"]'
        tbody = web_page.find_by_xpath('//tbody[@data-testid="beast-core-table-middle-tbody"]')
        tbody.scroll_to(location='top', behavior='instant', search_up=True)
        page_start_count = len(return_data)
        lazy_data_list = _iter_life_cycle_rows(web_page, data_xpath, page_index + 1)
        for i,lazy_data in enumerate(lazy_data_list):

            row_data = []
            row = i + 1

            tds = lazy_data['cells']
            sku_id = lazy_data['sku']
            if sku_id in seen_skus:
                if len(tds) > 3:
                    if sku_id not in main_row_cache:
                        raise RuntimeError('第{}页仍出现上一页主SKU={}，翻页可能尚未生效'.format(page_index + 1, sku_id))
                    tmp_row_data = list(main_row_cache[sku_id])
                continue
            if len(tds) <= 3 and not tmp_row_data:
                raise ValueError('第{}页第{}行SKU={}缺少所属商品主行'.format(page_index + 1, row, sku_id))
            if len(tds) > 3:
            
                # 获取商品简介
                shop_introduce = lazy_data['name']
                shop_category = lazy_data['category']
                SPU_ID = lazy_data['spu']
                spu_match = re.search(r'SPU\s*[:：]\s*(\d+)', SPU_ID)
                if spu_match is None:
                    raise ValueError('第{}页第{}行SPU无法解析：{!r}'.format(page_index + 1, row, SPU_ID))
                SPU_ID = spu_match.group(1)
                page_products.add(SPU_ID)

                # 获取其余的信息
                row_data = list(tds[2:])

                # 将商品信息添加入数据表格
                row_data.insert(0, shop_introduce)
                row_data.insert(1, shop_category)
                row_data.insert(2, SPU_ID)
                tmp_row_data = list(row_data)
                main_row_cache[sku_id] = list(row_data)

            # 只有一列的情况
            elif len(tds) == 1:
                # 根据表头获取SKU属性集下标
                sku_index = th_list.index('SKU属性集')
                tmp_row_data[sku_index] = tds[0]
                row_data = list(tmp_row_data)

            elif len(tds) == 2:
                # 根据表头获取SKU属性集与申报价格下标
                sku_index = th_list.index('SKU属性集')
                declear_index = [i for i,v in enumerate(th_list) if '申报价格' in v][0]
                tmp_row_data[sku_index] = tds[0]
                tmp_row_data[declear_index] = tds[1]
                row_data = list(tmp_row_data)

            # 有三列的情况
            elif len(tds) == 3:
                sku_index = th_list.index('SKU属性集')
                if sku_index + 2 >= len(tmp_row_data):
                    raise ValueError('SKU={}列数不足：{}，SKU列={}'.format(sku_id, len(tmp_row_data), sku_index))
                for offset, td in enumerate(tds):
                    tmp_row_data[sku_index + offset] = td
                row_data = list(tmp_row_data)

            if sku_id in seen_skus:
                continue
            seen_skus.add(sku_id)
            return_data.append(list(row_data))
            xbot.app.databook.append_row(list(row_data))

        print('第{}页累计读取{}个SPU，分页总数文本={!r}'.format(page_index + 1, len(page_products), total_num_text))
        page_added = len(return_data) - page_start_count
        if page_added == 0:
            raise RuntimeError('第{}页没有新增SKU，疑似翻页未生效；已采集{}条'.format(page_index + 1, len(seen_skus)))
        print('第{}页采集新增{}条SKU，累计{}条'.format(page_index + 1, page_added, len(seen_skus)))
        if page_index + 1 >= page:
            break

        # 进行换页操作
        next_page_xpath = '//li[@data-testid="beast-core-pagination-next"]'
        next_page_sel = Tools.gen_selector(next_page_xpath)
        if web_page.wait_appear(next_page_sel, timeout=1):
            next_page_class = web_page.find_by_xpath(next_page_xpath).get_attribute('class')
            if 'disabled' not in next_page_class:
                web_page.find_by_xpath(next_page_xpath).click()
                
                print('切换下一页')
                # 等待数据加载完毕
                Tools.wait_loading(web_page, appear_time=0)
                # 将数据滚动到顶部
                To_tbody_top(web_page)
                sleep(3)
                continue
            else:
                break
        break
    print('生命周期采集结束，状态={}，SKU共{}条'.format(product_state, len(seen_skus)))
    return return_data


def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active(mode='chrome')
    product_state = '已下架'
    result = life_cycle_collection(web_page, product_state)
    print(result)
    exit()


def main(args):
    # 测试模块
    test()

    # 功能模块
    web_page = args.get('web_page')
    product_state = args.get('product_state')

    data = life_cycle_collection(web_page, product_state)
    args['data'] = data
