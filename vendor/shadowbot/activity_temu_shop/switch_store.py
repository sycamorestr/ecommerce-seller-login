import re
import threading
import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import Tools


def _safe_get_active(product_name):
    """安全获取活动页，失败返回 None"""
    try:
        return xbot.web.get_active(mode=product_name)
    except Exception as e:
        print(f"get_active failed: {e}")
        return None


def switch_store(web_page: xbot.web.WebElement, store_name):
    """切换店铺
    如果是非目标店铺, 走切换逻辑, 切换后并校验是否切换成功, 并自动补充
    """
    if not isinstance(store_name, str) or not store_name.strip():
        raise ValueError('目标店铺名称不能为空或非文本：{!r}'.format(store_name))
    store_name = store_name.strip()

    # ---- 用 Event 替代普通 bool，并保证任何分支都能停止子线程 ----
    stop_event = threading.Event()
    product_name = web_page.product_name

    def wait_saler_center(url: str, interval: float = 0.3):
        """循环判断当前页面是否为卖家中心页面，如果是，则进行验证"""
        while not stop_event.is_set():
            # 每次都用最新的活动页，避免持有失效的 browserId
            page = _safe_get_active(product_name)
            if page is None:
                sleep(interval)
                continue
            try:
                target_url = page.get_url()
                if url in target_url:
                    Tools.check_saler_center(page)
            except Exception as e:
                # 连接失败大概率是浏览器被重建，直接退出，让主线程去重拿
                msg = str(e)
                if "ConnectInternal" in msg or "Code:11" in msg or "ResolveBrowser" in msg:
                    print(f"wait_saler_center 连接失效，退出子线程: {e}")
                    return
                print(f"wait_saler_center error: {e}")
            sleep(interval)

    confirm_thread = threading.Thread(
        target=wait_saler_center,
        kwargs={"url": "authentication"},
        daemon=True,
    )
    confirm_thread.start()

    try:
        # ================== 主流程 ==================
        store_name_xpath_list = [
            '(//div[contains(@class,"account-info_mallInfo")]//span[contains(@class, "elli_outerWrapper")])[1]',
            '(//div[contains(@class,"Space_alignCenter")]/div[2])[1]',
            '//div[contains(@class,"site-main_entrySection")]//div[contains(@class,"site-main_mallName")]',
        ]
        store_name_clean = re.sub(r'\s+', '', store_name)

        # 判断当前店铺, 如果是目标店铺不切换
        web_page = _safe_get_active(product_name) or web_page
        for store_name_xpath in store_name_xpath_list:
            try:
                current_name = web_page.find_by_xpath(store_name_xpath, timeout=2).get_text()
                current_name = re.sub(r'\s+', '', current_name.strip())
                if current_name == store_name_clean:
                    return
            except Exception:
                continue

        # --- 切换前先把弹窗关闭 ---
        try:
            close_button = '//span[@class="dxm-close dxmTemuBackCrawlCloseBtn"]'
            all_close_button = web_page.find_all_by_xpath(close_button, timeout=1)
            for btn in all_close_button:
                try:
                    btn.click()
                except Exception:
                    pass
        except Exception:
            pass

        # 等待 authentication 处理完（用新对象判断，避免旧引用）
        for _ in range(30):
            web_page = _safe_get_active(product_name)
            if web_page is None:
                sleep(1)
                continue
            try:
                cur_url = web_page.get_url()
            except Exception:
                cur_url = ""
            if "authentication" not in cur_url:
                break
            sleep(1)

        sleep(2)
        web_page = _safe_get_active(product_name)
        if web_page is None:
            raise RuntimeError("切换店铺时无法获取活动页面")

        # 展开切换面板
        if len(web_page.find_all_by_xpath('//*[normalize-space()="切换"]', timeout=1)) == 0:
            try:
                web_page.find_by_xpath(
                    "//div[contains(@class,'account-info_accountInfo')]", timeout=10
                ).click()
            except Exception:
                web_page = _safe_get_active(product_name)
                web_page.find_by_xpath(
                    '(//div[contains(@class,"Space_alignCenter")]/div[2])[1]'
                ).click()

        if len(web_page.find_all_by_xpath("//*[text()='切换']", timeout=1)) == 1:
            web_page.find_by_xpath("//*[text()='切换']").click()
        if len(web_page.find_all_by_xpath("//*[text()=' 切换']", timeout=1)) == 1:
            web_page.find_by_xpath("//*[text()=' 切换']").click()

        elelms_list = [
            "//div[contains(@class,'account-info_switchSection')]/div",
            '//div[contains(@class,"1f1q4yE1")]',
            '//div[contains(@class,"account-info_renderMallList")]/div[contains(@class,"account-info_mallSection")]',
            '//div[contains(@class,"site-main_mallSection")]',
        ]

        web_page = _safe_get_active(product_name)
        if web_page is None:
            raise RuntimeError("切换面板前无法获取活动页面")

        # 根据切换面板的不同元素选择对应的切换店铺元素处理逻辑
        try:
            if len(web_page.find_all_by_xpath(
                    '//div[contains(@class,"site-main_switchSection")]', timeout=2)) == 1:
                Tools.switch_ydk_store(web_page, elelms_list[3], store_name)
            elif len(web_page.find_all_by_xpath(
                    '//div[starts-with(@class,"MDL_header")]', timeout=2)) == 1:
                Tools.switch_ydk_store(web_page, elelms_list[1], store_name)
            elif len(web_page.find_all_by_xpath(
                    '//div[contains(@class,"account-info_changeMallList")]')) == 1:
                Tools.new_switch_store(web_page, elelms_list[2], store_name)
            else:
                Tools.switch_store(web_page, elelms_list[0], store_name)
        except Exception as e:
            # 保留原始堆栈
            raise RuntimeError(f"当前页面元素未适配: {e}") from e

        # 校验切换是否成功
        is_switch_successful = True
        for store_name_xpath in store_name_xpath_list:
            try:
                current_name = None
                for _ in range(3):
                    web_page = _safe_get_active(product_name)
                    if web_page is None:
                        sleep(2)
                        continue
                    current_name = web_page.find_by_xpath(
                        store_name_xpath, timeout=2
                    ).get_text()
                    current_name = re.sub(r'\s+', '', current_name.strip())
                    if current_name != '-':
                        break
                    sleep(2)

                if current_name is None:
                    continue
                if current_name != store_name_clean:
                    is_switch_successful = False
                    break
            except Exception:
                continue

        if not is_switch_successful:
            raise Exception(f'{store_name} 店铺切换失败')

    finally:
        # 无论成功失败，一定收掉子线程, 防止执行其他指令时关闭浏览器窗口导致异常
        stop_event.set()
        confirm_thread.join(timeout=3)


def main(args):
    test()
    web_page = args.get("web_page", '')
    store_name = args.get("store_name", '')
    switch_store(web_page, store_name)


def test(store_name="gzpas"):
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active(mode='chrome')
    switch_store(web_page, store_name)
    exit()