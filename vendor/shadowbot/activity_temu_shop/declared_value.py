# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re
import os
import math

import xbot
from xbot import print, sleep
from xbot_extensions.lazy_loading import get_lazy_element_list_by_xpath
from .import package
from .package import variables as glv
from .utils import Tools


def declared_value(web_page, two_list):
    """申报价格"""
    Tools.handle_info(web_page)
    data_list = []
    
    # 判断当前页面是否在目标页
    for _ in range(2):
        url = web_page.get_url()
        if '/newon/product-select' not in url:
            domain_url = Tools.get_domain_from_url(url)
            web_page.navigate(f'{domain_url}/newon/product-select')
        else:
            break
    else:
        raise Exception('该店铺的该站点没有上新生命周期管理内容')

    # 等待元素加载完毕
    Tools.wait_loading(web_page)
    # 消除信息提示
    Tools.handle_info(web_page)
    sleep(2)
    
    # 判断价格待确认是否被勾选
    wait_confirm_xpath = '//div//span[text()="价格待确认"]/following-sibling::div'
    wait_confirm_sel = Tools.gen_selector(wait_confirm_xpath)
    if not web_page.wait_appear(wait_confirm_sel, timeout=3):
        # 点击价格待确认
        web_page.find_by_xpath('//div//span[text()="价格待确认"]').click(delay_after=0.1)

    # 等待数据加载完毕
    Tools.wait_loading(web_page)

    # 点击页码选择框
    page_frame_xpath = '//div[contains(@class,"TB_bottomRight")]//div[@data-testid="beast-core-input-suffix"]'
    web_page.find_by_xpath(page_frame_xpath).click(delay_after=0.1)

    # 进行页码选择
    page_xpath = '//ul[@role="listbox"]/li/span[text()=50]'
    web_page.find_by_xpath(page_xpath).click(delay_after=0.1)

    # 获取总数据条数
    total_num_xpath = '//div[contains(@class,"TB_bottomRight")]//li[contains(@class,"PGT_totalText")]'
    total_num_text = web_page.find_by_xpath(total_num_xpath).get_text()
    total_num = re.search(r'(\d+)', total_num_text, re.S).group(1)

    if total_num == '0':
        return 

    # 获取循环次数
    page = math.ceil(int(total_num) / 50)

    for i in range(page):

        # 等待页面加载完毕
        Tools.wait_loading(web_page)

        # 点击勾选全部信息
        all_info_xpath = '(//thead/tr[1]/th[1]//label)[1]'
        web_page.find_by_xpath(all_info_xpath).click(delay_after=0.1)

        # 点击批量查看并申报价格
        value_button_xpath = '//button[contains(@class,"BTN_outerWrapper") and span[text()="批量查看并确认申报价格"] and not(@disabled)]'
        sleep(1)

        # 判断批量查看并申报价格是否被禁用
        if len(web_page.find_all_by_xpath(value_button_xpath, timeout=1)) >0:
            web_page.find_by_xpath(value_button_xpath).click(delay_after=0.1)
        else:
            # 点击下一页
            if page > 1 and i < page - 1:
                next_page = '//li[@data-testid="beast-core-pagination-next"]'
                web_page.find_by_xpath(next_page).click(delay_after=0.1)
            continue

        # 等待弹窗加载
        Tools.wait_loading(web_page)
        sleep(1)

        # 获取弹窗内的tbody元素（通过弹窗容器定位，避免获取到旧的tbody）
        # 优先查找弹窗内的tbody，如果没有则查找可见的tbody
        target_tr_display = None
        for _ in range(5):
            try:
                # 方法1: 通过弹窗容器查找tbody（更可靠）
                portal_xpath = '//div[@data-testid="beast-core-portal-main"]'
                portal_elements = web_page.find_all_by_xpath(portal_xpath, timeout=1)
                if portal_elements:
                    # 查找弹窗内可见的tbody
                    for portal in portal_elements:
                        tbody_in_portal = portal.find_all_by_xpath('.//tbody[@data-testid="beast-core-table-middle-tbody"]', timeout=0.5)
                        if tbody_in_portal:
                            # 选择可见的tbody
                            visible_tbody = [_ for _ in tbody_in_portal if _.get_bounding(to96dpi=False)[2] != 0]
                            if visible_tbody:
                                target_tr_display = visible_tbody[-1]  # 使用最后一个（最新的）
                                break
                
                # 方法2: 如果方法1失败，使用原来的方法但选择最新的可见tbody
                if target_tr_display is None:
                    target_tr_xpath = '//tbody[@data-testid="beast-core-table-middle-tbody"]'
                    target_tr_sel = web_page.find_all_by_xpath(target_tr_xpath, timeout=1)
                    visible_tbody_list = [_ for _ in target_tr_sel if _.get_bounding(to96dpi=False)[2] != 0]
                    if visible_tbody_list:
                        target_tr_display = visible_tbody_list[-1]  # 使用最后一个（最新的）
                
                if target_tr_display:
                    break
            except Exception as e:
                print(f'获取tbody失败，重试中... {e}')
                sleep(1)
        
        if target_tr_display is None:
            print('无法获取到有效的tbody元素，跳过当前页')
            # 尝试关闭弹窗
            try:
                cancel_xpath = '(//button[contains(@class,"BTN_outerWrapper")]/span[text()="取消"])'
                cancel_list_ele = web_page.find_all_by_xpath(cancel_xpath, timeout=1)
                cancel_display = [_ for _ in cancel_list_ele if _.get_bounding(to96dpi=False)[2] != 0]
                if cancel_display:
                    cancel_display[0].click(delay_after=0.1)
            except:
                pass
            continue

        # 当前页面可见的取消按钮xpath
        cancel_xpath = '(//button[contains(@class,"BTN_outerWrapper")]/span[text()="取消"])'
        cancel_display = None
        for _ in range(3):
            try:
                cancel_list_ele = web_page.find_all_by_xpath(cancel_xpath, timeout=1)
                cancel_display = [_ for _ in cancel_list_ele if _.get_bounding(to96dpi=False)[2] != 0][0]
                break
            except:
                sleep(1)
        
        if cancel_display is None:
            print('无法获取取消按钮，跳过当前页')
            continue

        # 当前页面可见的确认按钮xpath
        confirm_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[contains(text(),"全部提交")]'
        confirm_display = None
        for _ in range(3):
            try:
                confirm_list_sel = web_page.find_all_by_xpath(confirm_xpath, timeout=1)
                confirm_display = [_ for _ in confirm_list_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
                break
            except:
                sleep(1)
        
        # 打个标记，判断商品是否被移除、是否有调整操作以及是否点击了取消
        goods_remove = False      # 是否执行过“移除”
        value_adjust = False      # 是否执行过“调整申报价格/放弃调整报价”等改价相关操作
        is_cancle = False         # 是否点击过“取消”

        # 使用集合跟踪已处理的行，避免同一行在懒加载/刷新后被重复处理
        processed_keys = set()  # key 由 skc_id + sku_info + origin_value 组成，确保同一 SKC 不同颜色也能各自处理
        no_new_data_count = 0   # 记录连续没有新数据的次数
        handled_skc_list = []   # 记录已“命中测试数据并处理”的 skc_id，用于去重输出

        def get_visible_tbody():
            """每次循环重新获取最新的可见 tbody，适配动态刷新/懒加载"""
            try:
                portal_xpath = '//div[@data-testid="beast-core-portal-main"]'
                portal_elements = web_page.find_all_by_xpath(portal_xpath, timeout=1)
                if portal_elements:
                    for portal in portal_elements:
                        tbody_in_portal = portal.find_all_by_xpath('.//tbody[@data-testid="beast-core-table-middle-tbody"]', timeout=0.5)
                        visible_tbody = [_ for _ in tbody_in_portal if _.get_bounding(to96dpi=False)[2] != 0]
                        if visible_tbody:
                            return visible_tbody[-1]
                # 兜底：直接取页面上最新的可见 tbody
                target_tr_xpath = '//tbody[@data-testid="beast-core-table-middle-tbody"]'
                target_tr_sel = web_page.find_all_by_xpath(target_tr_xpath, timeout=1)
                visible_tbody_list = [_ for _ in target_tr_sel if _.get_bounding(to96dpi=False)[2] != 0]
                if visible_tbody_list:
                    return visible_tbody_list[-1]
            except Exception as e:
                print(f'重新获取tbody失败: {e}')
            return None

        # 使用懒加载方式处理数据
        while True:
            sleep(0.5)  # 等待新数据渲染

            # 每次循环都重新获取最新的 tbody，防止 DOM 被重建后引用失效
            tbody = get_visible_tbody()
            if tbody is None:
                print('未找到可见tbody，结束本页处理')
                break

            try:
                trs = tbody.find_all_by_xpath('./tr', timeout=1)
            except:
                print('无法获取tr列表，退出循环')
                break

            current_tr_count = len(trs)
            if current_tr_count == 0:
                print('没有找到tr元素，退出循环')
                break

            # 如果本轮没有新增可处理的行，累加次数；连续3次则认为已加载完成
            before_size = len(processed_keys)
            # 先滚动到最后一行，触发懒加载
            try:
                Tools.see_element(trs[-1], 'center')
                sleep(0.3)
            except:
                pass

            # 处理当前tbody中的tr（每次循环重新获取tds，避免DOM刷新后丢列）
            for idx, tr in enumerate(trs):
                # 获取行内所有的td，必要时兜底包含th
                try:
                    tds = tr.find_all_by_xpath('./td', timeout=0.2)
                    if len(tds) == 0:
                        tds = tr.find_all_by_xpath('./td|./th', timeout=0.2)
                except:
                    continue


                # 若tds长度为0则进行下次循环
                if len(tds) == 0:
                    continue

                # 若长度为12（无“建议申报价”那一列）
                if len(tds) == 12:
                    try:
                        # 获取当前商品的skc
                        skc_id = tds[1].find_by_xpath('.//div[contains(text(),"SKC：")]').get_text()
                        skc_id = skc_id.split('SKC：')[1]
                        # print(skc_id)

                        # 获取sku属性集
                        sku_info = tds[2].find_by_xpath('./div/div[1]').get_text()
                        
                        # 获取原申报价格
                        origin_value = tds[5].find_by_xpath('./span/span/span[2]').get_text()
                        
                        # 如果该“行”（同 skc_id + sku_info + 原价）已处理过，跳过
                        unique_key = f'{skc_id}-{sku_info}-{origin_value}'
                        if unique_key in processed_keys:
                            processed_keys.add(unique_key)
                            continue
                        
                        # 获取参考申报价格
                        reference_value = tds[6].find_by_xpath('.//span[text()="¥" or text()="$" or text()="￥"]/following-sibling::span').get_text()

                        # 获取改价意愿的属性值
                        value_wish_vale = tds[7].find_by_xpath('.//input').get_attribute('value')

                        # 进行对比（two_list 结构为 [sku_info, origin_value, price]）
                        # 使用“完全相等 + 价格数值相等”来匹配，避免子串误伤
                        matched = False
                        for value_info_list in two_list:
                            cfg_sku = str(value_info_list[0]).strip()
                            cfg_origin = str(value_info_list[1]).strip()

                            # 归一化价格文本，只取数字部分做 float 对比，避免 25 vs 25.00 等问题
                            try:
                                row_price = float(re.findall(r'\d+\.?\d*', origin_value)[0])
                                cfg_price = float(re.findall(r'\d+\.?\d*', cfg_origin)[0])
                            except Exception:
                                row_price = origin_value
                                cfg_price = cfg_origin

                            # 如果sku信息和原申报价格都可以匹配的上
                            if sku_info.strip() == cfg_sku and row_price == cfg_price:
                                matched = True

                                # 记录已处理的 skc_id（本页该 SKC 下其他行不再处理）
                                if skc_id not in handled_skc_list:
                                    handled_skc_list.append(skc_id)

                                # 将数据添加入列表
                                if len(value_info_list) < 4:
                                    value_info_list.append(reference_value)
                                if value_info_list not in data_list:
                                    data_list.append(value_info_list)

                                # 进行参考申报价格对比，若参考价格高于提供的价格，则不进行修改,  
                                # 进行调整报价
                                print(f'对信息为 SKC_ID：{skc_id} sku信息：{sku_info} 原申报价格：{origin_value} 的商品进行调整报价')
                                if float(reference_value) < float(value_info_list[2]):
                                    if value_wish_vale == '放弃调整报价':
                                        break

                                    # 点击调整为参考申报价格
                                    tds[7].find_by_xpath('.//input').click(delay_after=0.1)
                                    web_page.find_by_xpath('//ul/li/span[text()="放弃调整报价"]').click(delay_after=0.1)
                                    # 记录已执行过改价相关操作
                                    value_adjust = True
                                    break
                                else:
                                    break
                        
                        # 如果没有匹配，点击移除
                        if not matched:
                            tds[-1].find_by_xpath('./a').click(delay_after=0.1)
                            sleep(1)
                            
                            # 若全需要移除，则不进行提交，点击取消
                            try:
                                remove_disabled = tds[-1].find_all_by_xpath('./a/span[text()="移除"]/../../a[@disabled]', timeout=0.5)
                                if len(remove_disabled) > 0:
                                    # 点击取消
                                    cancel_display.click(delay_after=0.1)
                                    is_cancle = True
                                    break  # 退出tr处理循环
                            except:
                                pass

                            # 标记更新
                            goods_remove = True
                    except Exception as e:
                        print(f'处理12列数据时出错: {e}')
                
                # 若长度为13（多了一列“建议申报价”等）
                elif len(tds) == 13:
                    try:
                        # 获取当前商品的skc
                        skc_id = tds[1].find_by_xpath('.//div[contains(text(),"SKC：")]').get_text()
                        skc_id = skc_id.split('SKC：')[1]

                        # 获取sku属性集
                        sku_info = tds[2].find_by_xpath('./div/div[1]').get_text()
                        
                        # 获取原申报价格
                        origin_value = tds[6].find_by_xpath('./span/span/span[2]').get_text()
                        
                        # 如果该“行”（同 skc_id + sku_info + 原价）已处理过，跳过
                        unique_key = f'{skc_id}-{sku_info}-{origin_value}'
                        if unique_key in processed_keys:
                            processed_keys.add(unique_key)
                            continue
                        
                        # 获取参考申报价格
                        reference_value = tds[7].find_by_xpath('.//span[text()="¥" or text()="$" or text()="￥"]/following-sibling::span').get_text()
                    
                        # 获取改价意愿的属性值
                        value_wish_vale = tds[8].find_by_xpath('.//input').get_attribute('value')

                        # 进行对比（two_list 结构为 [sku_info, origin_value, price]）
                        matched = False
                        for value_info_list in two_list:
                            cfg_sku = str(value_info_list[0]).strip()
                            cfg_origin = str(value_info_list[1]).strip()

                            # 归一化价格文本，只取数字部分做 float 对比
                            try:
                                row_price = float(re.findall(r'\d+\.?\d*', origin_value)[0])
                                cfg_price = float(re.findall(r'\d+\.?\d*', cfg_origin)[0])
                            except Exception:
                                row_price = origin_value
                                cfg_price = cfg_origin

                            # 如果sku信息和原申报价格都可以匹配的上
                            if sku_info.strip() == cfg_sku and row_price == cfg_price:
                                matched = True

                                # 记录已处理的 skc_id（本页该 SKC 下其他行不再处理）
                                if skc_id not in handled_skc_list:
                                    handled_skc_list.append(skc_id)

                                # 记录已处理的 skc_id
                                if skc_id not in handled_skc_list:
                                    handled_skc_list.append(skc_id)

                                # 将数据添加入列表
                                if len(value_info_list) < 4:
                                    value_info_list.append(reference_value)
                                if value_info_list not in data_list:
                                    data_list.append(value_info_list)

                                # 进行参考申报价格对比，若参考价格高于提供的价格，则不进行修改,  
                                # 否则，进行放弃调整报价
                                # 进行调整报价
                                print(f'对信息为 SKC_ID：{skc_id} sku信息：{sku_info} 原申报价格：{origin_value} 的商品进行调整报价')
                                if float(reference_value) < float(value_info_list[2]):
                                    if value_wish_vale == '放弃调整报价':
                                        break

                                    # 点击调整为参考申报价格
                                    try:
                                        tds[8].find_by_xpath('.//input').click(delay_after=0.1)
                                        web_page.find_by_xpath('//ul/li[text()="放弃调整报价"]').click(delay_after=0.1)
                                    except:
                                        tds[8].find_by_xpath('.//input').click(delay_after=0.1)
                                        web_page.find_by_xpath('//ul/li[text()="放弃调整报价"]').click(delay_after=0.1)
                                    # 记录已执行过改价相关操作
                                    value_adjust = True
                                    break
                                else:
                                    break
                        
                        # 如果没有匹配，点击移除
                        if not matched:
                            tds[-1].find_by_xpath('./a').click(delay_after=0.1)
                            sleep(1)
                            
                            # 若全需要移除，则不进行提交，点击取消
                            try:
                                remove_disabled = tds[-1].find_all_by_xpath('./a/span[text()="移除"]/../../a[@disabled]', timeout=0.5)
                                if len(remove_disabled) > 0:
                                    # 点击取消
                                    cancel_display.click(delay_after=0.1)
                                    is_cancle = True
                                    break  # 退出tr处理循环
                            except:
                                pass

                            # 标记更新
                            goods_remove = True
                    except Exception as e:
                        print(f'处理13列数据时出错: {e}')
                
                # 标记为已处理
                try:
                    processed_keys.add(unique_key)
                except:
                    pass
                
                # 如果点击了取消，退出循环
                if is_cancle:
                    break
            
            # 如果点击了取消，退出外层循环
            if is_cancle:
                break
            
            # 判断是否出现新数据
            after_size = len(processed_keys)
            if after_size == before_size:
                no_new_data_count += 1
                if no_new_data_count >= 3:
                    print(f'数据加载完成，共处理{after_size}条')
                    break
            else:
                no_new_data_count = 0

        # 本页结束时，根据是否有实际操作决定处理方式：
        # 1）若既没有移除，也没有任何改价相关操作，则不提交，直接取消并给出日志警告
        # 2）否则保持当前行为（如需点击“确定”提交，可在此处补充提交逻辑）
        try:
            if not is_cancle:
                if (not goods_remove) and (not value_adjust):
                    # 无任何操作，点击“取消”并给出警告日志
                    cancel_display.click(delay_after=0.1)
                    try:
                        xbot.logging.warning('本页既没有进行移除操作也没有进行调整价格操作，请检查网页元素是否发生变化或SKU是否信息正确')
                    except Exception:
                        print('本页既没有进行移除操作也没有进行调整价格操作，请检查网页元素是否发生变化或SKU是否信息正确')
                else:
                    # 全部提交操作
                    if is_cancle is False:
                        # 点击确定
                        confirm_display.click(simulative=True)
                        yes_xpath = '//button/span[text()="确认"]'
                        yes_list_sel = web_page.find_all_by_xpath(yes_xpath, timeout=1)
                        yes_display = [_ for _ in yes_list_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
                        yes_display.click(delay_after=0.1)
            break
        except Exception as e:
            print(f'本页结束处理时出错: {e}')
            # 点击取消
            cancel_display.click(delay_after=0.1)

        print(f'本页处理的skc_id为 {handled_skc_list }')

        # 点击下一页
        if page > 1 and i < page - 1:
            next_page = '//li[@data-testid="beast-core-pagination-next"]'
            web_page.find_by_xpath(next_page).click(delay_after=0.1)
            sleep(1)

    print(data_list)
    return data_list

    
def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return 
    web_page = xbot.web.get_active(mode='superbrowser', silent_running=True)
    data_list = [
        # ['Blue + A Pair of Gloves', '35.00', '22.73'],
        # ['White Light', '15.00', '6.33'],
        # ['Multi-color Light', '15.00', '6.33'],
        # ['Copper color', '29.00', '14.94'],
        # ['Silver', '29.00', '14.94'],
        # ['Gold', '29.00', '14.94'],
        # ['M-Blue', '29.00', '9.12'],
        # ['unicom black', '29.00', '21.80'],
        # ['Gray', '50.00', '19.94'],
        # ['White', '44.42', '16.72'],
        # ['White', '29.00', '8.81'],
        # ['Black', '29.00', '21.80'],
        # ['Green', '18.00', '7.82']
        # ['White', '13.50', '6'],
        # ['Blue', '25', '17']
        ['Red','22.00','14'],
    ]
    declared_value(web_page, data_list)

    exit()

def main(args):
    test()

    web_page = args.get('web_page')
    two_list = args.get('two_list')

    data_list = declared_value(web_page, two_list)
    args['data_list'] = data_list