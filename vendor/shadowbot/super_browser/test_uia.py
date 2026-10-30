import time
import ctypes
import comtypes
import comtypes.client


def safe_get(fn, default=""):
    try:
        return fn()
    except Exception:
        return default


class ChromeUIAActivator:

    def __init__(self):
        comtypes.CoInitialize()
        comtypes.client.GetModule("UIAutomationCore.dll")

        from comtypes.gen.UIAutomationClient import (
            CUIAutomation,
            IUIAutomation,
        )

        self.uia = comtypes.client.CreateObject(
            CUIAutomation,
            interface=IUIAutomation,
        )

        self.walker = self.uia.RawViewWalker

    def activate_and_find_chrome(self, hwnd, max_depth=15):
        hwnd = int(hwnd)

        if not ctypes.windll.user32.IsWindow(hwnd):
            print("无效 HWND:", hwnd)
            return None

        # 这一步已经会触发 WM_GETOBJECT / UiaRootObjectId
        root = self.uia.ElementFromHandle(
            ctypes.c_void_p(hwnd)
        )

        print(
            "ROOT:",
            "Framework =", safe_get(lambda: root.CurrentFrameworkId),
            "Class =", safe_get(lambda: root.CurrentClassName),
            "Name =", safe_get(lambda: root.CurrentName),
        )

        # 给 Chrome 一点时间创建 accessibility tree
        time.sleep(0.5)

        queue = [(root, 0)]
        count = 0

        while queue:
            element, depth = queue.pop(0)

            if depth > max_depth:
                continue

            count += 1

            framework = safe_get(
                lambda: element.CurrentFrameworkId
            )

            cls = safe_get(
                lambda: element.CurrentClassName
            )

            name = safe_get(
                lambda: element.CurrentName
            )

            automation_id = safe_get(
                lambda: element.CurrentAutomationId
            )

            print(
                f"[{count}] "
                f"depth={depth} "
                f"Framework={framework!r} "
                f"Class={cls!r} "
                f"Name={name!r} "
                f"AutomationId={automation_id!r}"
            )

            # 找到 Chromium UIA 子树
            if framework and framework.lower() == "chrome":
                print("")
                print("===== 找到 Chrome UIA Provider =====")
                print("Framework:", framework)
                print("Class:", cls)
                print("Name:", name)
                print("AutomationId:", automation_id)

                return element

            try:
                child = self.walker.GetFirstChildElement(element)

                while child:
                    queue.append((child, depth + 1))

                    child = self.walker.GetNextSiblingElement(
                        child
                    )

            except Exception as e:
                print(
                    "walker error:",
                    type(e).__name__,
                    repr(e)
                )

        print("")
        print("扫描完成，没有找到 FrameworkId=Chrome")
        return None


def test_func():
    """私有 UIA8 客户端与打开店铺入口的契约测试。"""
    import types
    from comtypes import COMError
    from unittest.mock import patch
    from . import api, api_uia, uia

    page = object()
    target = types.SimpleNamespace(
        open_store=lambda *args, **kwargs: ('测试', page))
    with patch.object(api, 'get_version', return_value=api.Version.V6), \
            patch.object(api, 'ZiNiao', return_value=target):
        assert api.open_store('测试', '相等')[1] is page
    with patch.object(api_uia, 'get_version', return_value=api_uia.Version.V6), \
            patch.object(api_uia, 'ZiNiao', return_value=target):
        assert api_uia.open_store('测试', '相等')[1] is page

    modern_core = types.SimpleNamespace(IUIAutomation2=object(), IUIAutomation=object())
    legacy_core = types.SimpleNamespace(IUIAutomation=object())
    calls = []
    def create(clsid, interface):
        calls.append(clsid)
        return types.SimpleNamespace()
    _, backend = uia._create_native(modern_core, create)
    assert backend == 'CUIAutomation8' and len(calls) == 1
    calls[:] = []
    _, backend = uia._create_native(legacy_core, create)
    assert backend == 'CUIAutomation' and len(calls) == 1
    calls[:] = []
    def unsupported(clsid, interface):
        calls.append(clsid)
        if len(calls) == 1:
            raise COMError(-2147221164, 'class not registered', None)
        return object()
    assert uia._create_native(modern_core, unsupported)[1] == 'CUIAutomation'
    assert len(calls) == 2

    try:
        with uia.budget(0.01, '测试预算'):
            uia.pause(0.05)
    except uia.OperationTimeout:
        pass
    else:
        raise AssertionError('准备阶段预算未生效')
    assert uia.remaining(1) == 1
    return True


def main(args):
    import time
    import uiautomation as installed
    from uiautomation.uiautomation import _AutomationClient
    from . import uia
    old = _AutomationClient.instance()
    identity = (old.IUIAutomation, old.ViewWalker, installed.Control)
    assert test_func()
    client = uia.auto._AutomationClient.instance()
    report = {'contract_passed': True, 'backend': client.backend}
    if client.backend == 'CUIAutomation8':
        report['connection_timeout_ms'] = client.IUIAutomation.ConnectionTimeout
        report['transaction_timeout_ms'] = client.IUIAutomation.TransactionTimeout
        assert report['connection_timeout_ms'] == 60000
        assert report['transaction_timeout_ms'] == 120000
    started = time.monotonic()
    try:
        mode = args.get('测试模式', '契约测试')
        if mode == '契约测试':
            pass
        elif mode == '读取账号':
            from .ziniao_v6_uia import ZiNiao
            ziniao = ZiNiao()
            with uia.budget(50, '读取账号测试'):
                document, panel = ziniao._wait_any_panel(('full', 'basic', 'login'), timeout=30)
                report['panel'] = panel
                if panel != 'login':
                    document = ziniao._open_full_panel(timeout=20)
                    ziniao._clear_account_search(document, timeout=10)
                    ziniao._click_account_first_page(document)
                    ziniao._require_account_page_size_20(document)
                    records = ziniao._wait_account_page_records(document, timeout=10)
                    report['available_store_names'] = [row[0] for row in records]
                    report['record_count'] = len(records)
        elif mode in ('打开店铺', 'UIA打开店铺'):
            import xbot_visual
            from xbot.web import WebBrowser
            result = xbot_visual.process.run(
                process=('open_store' if mode == '打开店铺' else 'process9'), package=__name__,
                inputs={'店铺名称': args.get('店铺名称', ''), '匹配类型': '相等',
                        '打开账号': '点击', '超时时间': 50, '隐私模式': False},
                outputs=['完整店铺名称', 'web_page'])
            page = result.web_page
            assert isinstance(page, WebBrowser), type(page).__name__
            report['web_page_type'] = type(page).__name__
            report['page_url_readable'] = isinstance(page.get_url(), str)
            report['opened_store_name'] = result.完整店铺名称
        else:
            raise ValueError('测试模式仅支持契约测试、读取账号、打开店铺、UIA打开店铺')
    finally:
        assert old.IUIAutomation is identity[0]
        assert old.ViewWalker is identity[1]
        assert installed.Control is identity[2]
    report['old_client_unchanged'] = True
    report['elapsed_seconds'] = round(time.monotonic() - started, 3)
    args['report'] = report
    return args