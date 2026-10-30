"""天猫超市登录。独立实现，不修改或调用现有登录指令。"""
import re
import time
from urllib.parse import urlparse
from uuid import uuid4

LOGIN_URL = 'https://web.txcs.tmall.com/login?from=https%3A%2F%2Fweb.txcs.tmall.com%2F'
LOGIN_FRAME = '//iframe[@id="alibaba-login-box"]'
PROXY_FRAME = '//iframe[starts-with(@src,"https://web.txcs.tmall.com/pages/ascm/basic_login_proxy?")]'


def _backend_url(url):
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.hostname == 'web.txcs.tmall.com'
            and parsed.path not in ('/login', '/logout', '/pages/ascm/basic_login_proxy'))


def _supplier_name(label):
    return re.split(r'\s+--\s+', label.strip(), maxsplit=1)[0]


def _match_supplier(labels, requested):
    matches = [index for index, label in enumerate(labels) if label == requested]
    if not matches:
        raise ValueError('未找到精确匹配的二级供应商，请填写完整店铺名或完整选项文本。')
    if len(matches) != 1:
        raise ValueError('完整店铺名对应多个业务身份，请填写含业务类型后缀的完整选项文本。')
    return matches[0]


def _verify_supplier(actual, requested):
    if not actual or actual.strip() != _supplier_name(requested):
        raise RuntimeError('后台当前店铺与指定店铺不一致，停止后续操作。请确认二级供应商身份已绑定。')


def _verify_identity(active, requested):
    suffix = re.split(r'\s+--\s+', requested, maxsplit=1)
    expected = suffix[0] + ('-' + suffix[1] if len(suffix) == 2 else '')
    if not active or re.sub(r'^\d+-', '', active.strip()) != expected:
        raise RuntimeError('后台当前业务身份与指定的完整二级供应商名称不一致，停止后续操作。')


def _validate(args):
    values = {}
    for key, title in [('username', '登录账号'), ('password', '登录密码')]:
        value = args.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(title + '必须填写非空文本。')
        values[key] = value if key == 'password' else value.strip()
    shop_name = args.get('shop_name')
    if shop_name is None:
        shop_name = ''
    if not isinstance(shop_name, str):
        raise ValueError('店铺名须为文本；留空时默认选择第一条可见店铺。')
    values['shop_name'] = shop_name.strip()
    mode = args.get('mode') or 'chrome'
    if mode not in ('chrome', 'edge', 'cef'):
        raise ValueError('浏览器类型必须为 chrome、edge 或 cef。')
    values['mode'] = mode
    for key, default in [('timeout', 60), ('verification_timeout', 120)]:
        value = args.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 600:
            raise ValueError('等待时间必须为 1 到 600 的整数秒。')
        values[key] = value
    return values


def _selector(xpath, name):
    from xbot.selector import Selector
    return Selector({'id': str(uuid4()), 'name': name, 'framework': 'chrome',
                     'type': 'simple', 'version': 2,
                     'xpath': {'enable': 'true', 'segments': xpath.split('>>')}})


def _fill(element, text, title, paste=False, reacquire=None):
    # Retry only replacement input; no login or merchant submission is repeated here.
    for attempt in range(3):
        try:
            if attempt and reacquire is not None:
                element = reacquire()
            if paste:
                element.clipboard_input(text, append=False, click_before_input=True,
                                        focus_timeout=2000, send_key_delay=100,
                                        delay_after=1)
            else:
                element.input(text, simulative=False, cdp_input=True, append=False,
                              force_ime_ENG=False, driver_input=False,
                              focus_timeout=2000, delay_after=1)
        except Exception:
            # A temporary focus failure or stale handle gets a fresh attempt.
            if attempt < 2:
                time.sleep(0.5)
            continue
        deadline = time.monotonic() + 5
        consecutive_matches = 0
        while time.monotonic() < deadline:
            try:
                actual = element.get_value()
            except Exception:
                consecutive_matches = 0
            else:
                consecutive_matches = consecutive_matches + 1 if actual == text else 0
                if consecutive_matches == 2:
                    return
            time.sleep(0.2)
        if attempt < 2:
            time.sleep(0.5)
    raise RuntimeError(title + '自动填写已尝试3次，输入或读回校验仍未成功，未继续提交。') from None


def _select_supplier(browser, requested, timeout):
    selector = _selector(PROXY_FRAME + '>>//li[contains(concat(" ",normalize-space(@class)," ")," menu-item ")]', '二级供应商候选店铺')
    deadline = time.monotonic() + timeout
    click_failures = 0
    while time.monotonic() < deadline:
        try:
            options = browser.find_all(selector, timeout=1)
            visible = [option for option in options if option.is_displayed()]
            labels = [option.get_text() for option in visible]
        except Exception:
            time.sleep(0.3)
            continue
        if requested in labels or (not requested and any(label.strip() for label in labels)):
            index = (_match_supplier(labels, requested) if requested
                     else next(i for i, label in enumerate(labels) if label.strip()))
            selected = requested or labels[index].strip()
            try:
                visible[index].click(simulative=True, move_mouse=True, delay_after=0.5)
            except Exception:
                click_failures += 1
                if click_failures >= 3:
                    raise RuntimeError('选择二级供应商已尝试点击3次，仍未成功，未继续进入商家。') from None
            else:
                return selected
        time.sleep(0.3)
    message = '等待与完整店铺名精确匹配的候选店铺超时' if requested else '等待第一条可见店铺超时'
    raise TimeoutError(message + '，未继续进入商家。')


def _visible(browser, xpath, name):
    selector = _selector(xpath, name)
    if browser.is_element_displayed(selector):
        return browser.find(selector, timeout=1)
    return None


def _state(browser):
    # Navigation temporarily invalidates element handles; only retry reads.
    try:
        if _backend_url(browser.get_url()):
            merchant = _visible(browser, '//span[@class="current-supplier-name"]', '当前商家')
            if merchant:
                return 'backend', merchant.get_text().strip()
        enter = _visible(browser, PROXY_FRAME + '>>//button[contains(@class,"login-button")]', '进入商家')
        if enter:
            return 'supplier', enter
        error = _visible(browser, LOGIN_FRAME + '>>//*[contains(@class,"login-error-msg")]', '登录错误')
        if error and error.get_text().strip():
            return 'error', '账号登录失败，请检查账号、密码或页面验证提示。'
        slider = _visible(browser, LOGIN_FRAME + '>>//*[@id="nc_1_n1z"]', '登录人工验证')
        if slider:
            return 'verification', None
    except Exception:
        # Errors during navigation are not success; bounded polling below determines the outcome.
        pass
    return 'loading', None


def _wait_stage(browser, timeout, verification_timeout):
    import xbot
    deadline = time.monotonic() + timeout
    human_deadline = None
    while time.monotonic() < (human_deadline or deadline):
        stage, value = _state(browser)
        if stage in ('backend', 'supplier'):
            return stage, value
        if stage == 'error':
            raise RuntimeError(value)
        if stage == 'verification' and human_deadline is None:
            xbot.print('天猫超市登录需要人工完成页面验证，等待验证完成。')
            human_deadline = time.monotonic() + verification_timeout
        time.sleep(0.5)
    if human_deadline:
        raise TimeoutError('等待人工验证超时，请完成页面验证后重新执行。')
    raise TimeoutError('天猫超市登录或页面跳转超时，未确认进入目标店铺。')


def _verify_backend(browser, shop_name, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        stage, merchant = _state(browser)
        if stage == 'backend':
            # The page header omits the business-type suffix. Verify the active identity as well.
            active = browser.execute_javascript('function(){var e=document.querySelector(".supplier-name.active");return e?e.textContent.trim():null;}')
            if not active:
                time.sleep(0.5)
                continue
            expected = shop_name
            if not expected:
                company, separator, business = re.sub(r'^\d+-', '', active.strip()).rpartition('-')
                if not separator or not company or not business:
                    time.sleep(0.5)
                    continue
                expected = company + ' -- ' + business
            _verify_supplier(merchant, expected)
            _verify_identity(active, expected)
            return browser
        if stage == 'error':
            raise RuntimeError(merchant)
        time.sleep(0.5)
    raise TimeoutError('选择店铺后未确认进入指定后台，请检查页面状态或人工验证提示。')


def login(values):
    import xbot
    import xbot_visual
    password = xbot_visual.decrypt(values['password'])
    browser = xbot.web.create(LOGIN_URL, mode=values['mode'], silent_running=False,
                              load_timeout=values['timeout'])
    deadline = time.monotonic() + values['timeout']
    username_input = None
    while time.monotonic() < deadline:
        username_input = _visible(browser, LOGIN_FRAME + '>>//input[@id="fm-login-id"]', '天猫超市账号')
        if username_input:
            break
        stage, value = _state(browser)
        if stage == 'backend':
            return _verify_backend(browser, values['shop_name'], values['timeout'])
        time.sleep(0.5)
    if not username_input:
        raise TimeoutError('普通登录账号输入框未出现，请确认页面和浏览器扩展正常。')
    xbot.win32.manual_motion_on()
    try:
        _fill(username_input, values['username'], '登录账号')
        password_input = browser.find(_selector(LOGIN_FRAME + '>>//input[@id="fm-login-password"]', '天猫超市密码'), timeout=values['timeout'])
        _fill(password_input, password, '登录密码')
        login_button = browser.find(_selector(LOGIN_FRAME + '>>//button[contains(@class,"password-login")]', '天猫超市普通登录按钮'), timeout=values['timeout'])
        login_button.click(simulative=True, move_mouse=True, delay_after=0.5)
        stage, value = _wait_stage(browser, values['timeout'], values['verification_timeout'])
        if stage == 'backend':
            return _verify_backend(browser, values['shop_name'], values['timeout'])
        tenant = browser.find(_selector(PROXY_FRAME + '>>(//input[not(@type) or @type="text"])[1]', '天猫超市租户'), timeout=values['timeout'])
        if tenant.get_value() != '天猫超市（MAOCHAO）':
            raise RuntimeError('登录租户不是天猫超市（MAOCHAO），未继续提交。')
        supplier_selector = _selector(PROXY_FRAME + '>>(//input[not(@type) or @type="text"])[2]', '二级供应商精确名称')
        supplier = browser.find(supplier_selector, timeout=values['timeout'])
        if values['shop_name']:
            # Preserve the exact display text, including spaces and the business-type suffix.
            _fill(supplier, values['shop_name'], '二级供应商完整名称', paste=True,
                  reacquire=lambda: browser.find(supplier_selector, timeout=values['timeout']))
        else:
            supplier.click(simulative=True, move_mouse=True, delay_after=0.5)
        # Commit the selected identity through the same visible option a user clicks.
        selected_shop = _select_supplier(browser, values['shop_name'], values['timeout'])
        enter = browser.find(_selector(PROXY_FRAME + '>>//button[contains(@class,"login-button")]', '进入天猫超市商家'), timeout=values['timeout'])
        enter.click(simulative=True, move_mouse=True, delay_after=0.5)
        return _verify_backend(browser, selected_shop, values['timeout'])
    finally:
        xbot.win32.manual_motion_off()
        password = None


def main(args):
    values = _validate(args)
    args['web_page'] = login(values)
    return args
