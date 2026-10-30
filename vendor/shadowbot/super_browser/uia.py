# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用流程"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
import ctypes
import ctypes.wintypes as wt
import time
from dataclasses import dataclass, field

# -*- coding: utf-8 -*-
"""激活并验证 Chromium / Electron / CEF 窗口的 UI Automation 树。

核心调用顺序与 ShadowBot 6.3.9 的 Chromium 激活路径一致：

1. 向顶层窗口和全部子 HWND 发送 ``WM_GETOBJECT(lParam=1)``；
2. 再发送 ``WM_GETOBJECT(lParam=UiaRootObjectId/-25)``；
3. 通过真实 UIA 查询触发 ``ElementFromHandle``，并轮询渲染窗口的 UIA 树。

``force_uia`` 保留了旧的布尔接口。需要诊断超时、目标 HWND 或节点数量时，
请使用 ``force_uia_detailed``。

注意：如果目标以 ``--disable-renderer-accessibility`` 等方式硬禁用了无障碍
提供程序，外部进程不能保证重新启用它；此时本模块会在超时后明确返回失败。
"""

# ---------------------------------------------------------------------------
# 私有 UIA 客户端：优先 UIA8，仅能力缺失时回退旧 CUI，不改全局依赖。
# ---------------------------------------------------------------------------
import importlib.util
import math
import sys
import threading
from contextlib import contextmanager

CONNECTION_TIMEOUT_MS = 60000
TRANSACTION_TIMEOUT_MS = 120000
MAX_TREE_NODES = 10000
TREE_TIMEOUT_SECONDS = 300
_state = threading.local()


class OperationTimeout(BaseException):
    """阶段预算耗尽信号：必须穿透 ``except Exception`` 直达阶段边界。"""


def check_budget():
    deadline = getattr(_state, 'deadline', None)
    if deadline is not None and time.monotonic() >= deadline:
        raise OperationTimeout('紫鸟阶段超时: ' + getattr(_state, 'label', 'UIA'))


def remaining(limit):
    check_budget()
    deadline = getattr(_state, 'deadline', None)
    return min(limit, max(0, deadline-time.monotonic())) if deadline is not None else limit


def pause(seconds):
    available = remaining(seconds)
    time.sleep(available)
    if available < seconds:
        raise OperationTimeout('紫鸟阶段超时: ' + getattr(_state, 'label', 'UIA'))
    check_budget()


@contextmanager
def budget(seconds, label):
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('超时时间必须为大于0的有限数字')
    old_deadline = getattr(_state, 'deadline', None)
    old_label = getattr(_state, 'label', None)
    deadline = time.monotonic() + seconds
    _state.deadline = min(old_deadline, deadline) if old_deadline is not None else deadline
    _state.label = label
    try:
        check_budget()
        yield
        check_budget()
    finally:
        _state.deadline, _state.label = old_deadline, old_label


@contextmanager
def phase(label):
    previous = getattr(_state, 'label', None)
    _state.label = label
    try:
        check_budget()
        yield
        check_budget()
    finally:
        _state.label = previous


def _create_native(core, create):
    from comtypes import COMError
    modern_interface = getattr(core, 'IUIAutomation2', None)
    native = None
    if modern_interface is not None:
        try:
            native = create('{e22ad333-b25f-460c-83d0-0581107395c9}', interface=modern_interface)
        except COMError as exc:
            # 只允许类/接口不存在；超时、权限和其他故障不得静默切后端。
            if (exc.hresult & 0xFFFFFFFF) not in (0x80040154, 0x80004002, 0x80040111):
                raise
    if native is None:
        return create('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=core.IUIAutomation), 'CUIAutomation'
    native.ConnectionTimeout = CONNECTION_TIMEOUT_MS
    native.TransactionTimeout = TRANSACTION_TIMEOUT_MS
    if native.ConnectionTimeout != CONNECTION_TIMEOUT_MS or native.TransactionTimeout != TRANSACTION_TIMEOUT_MS:
        raise RuntimeError('UIA8 超时设置回读不一致')
    return native, 'CUIAutomation8'


def _load_private_auto():
    import uiautomation.uiautomation as installed
    alias = __name__ + '_private'
    spec = importlib.util.spec_from_file_location(alias, installed.__file__)
    if spec is None or spec.loader is None:
        raise RuntimeError('无法加载现有 uiautomation 实现')
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(alias, None)
        raise

    class PrivateClient:
        _local = threading.local()

        @classmethod
        def instance(cls):
            client = getattr(cls._local, 'client', None)
            if client is None:
                client = cls()
                cls._local.client = client
            return client

        def __init__(self):
            import comtypes.client
            self.UIAutomationCore = comtypes.client.GetModule('UIAutomationCore.dll')
            self.IUIAutomation, self.backend = _create_native(self.UIAutomationCore, comtypes.client.CreateObject)
            self.ViewWalker = self.IUIAutomation.RawViewWalker

    module._AutomationClient = PrivateClient

    def bounded_children(control):
        with budget(TREE_TIMEOUT_SECONDS, '枚举子控件'):
            children = []
            child = control.GetFirstChildControl()
            while child:
                check_budget()
                if len(children) >= MAX_TREE_NODES:
                    raise OperationTimeout('UIA 子控件数量超出上限')
                children.append(child)
                child = child.GetNextSiblingControl()
            return children

    original_walk = module.WalkControl
    def bounded_walk(*args, **kwargs):
        # 生成器 yield 时不能持有上下文：调用方可能提前 break。
        deadline = time.monotonic() + TREE_TIMEOUT_SECONDS
        for index, item in enumerate(original_walk(*args, **kwargs)):
            check_budget()
            if index >= MAX_TREE_NODES or time.monotonic() >= deadline:
                raise OperationTimeout('UIA 树遍历超出时间或节点上限')
            yield item

    original_exists = module.Control.Exists
    def bounded_exists(control, maxSearchSeconds=5, searchIntervalSeconds=module.SEARCH_INTERVAL, printIfNotExist=False):
        result = original_exists(control, remaining(maxSearchSeconds), searchIntervalSeconds, printIfNotExist)
        check_budget()
        return result

    module.Control.GetChildren = bounded_children
    module.Control.Exists = bounded_exists
    module.WalkControl = bounded_walk
    return module


auto = _load_private_auto()


def send_message_bounded(hwnd, message, wparam, lparam, timeout_ms=10000):
    import win32gui
    wait_ms = max(1, int(remaining(timeout_ms/1000.0)*1000))
    result = win32gui.SendMessageTimeout(hwnd, message, wparam, lparam, 0x0001 | 0x0002, wait_ms)
    check_budget()
    return result


import ctypes
import ctypes.wintypes as wt
import time


WM_GETOBJECT = 0x003D
CHROMIUM_SCREEN_READER_OBJECT_ID = 1
UIA_ROOT_OBJECT_ID = -25
OBJID_CLIENT = 0xFFFFFFFC

SMTO_BLOCK = 0x0001
SMTO_ABORTIFHUNG = 0x0002
SEND_FLAGS = SMTO_BLOCK | SMTO_ABORTIFHUNG

COINIT_APARTMENTTHREADED = 0x2

ULONG_PTR = ctypes.c_size_t
DWORD_PTR = ULONG_PTR
LRESULT = wt.LPARAM
HRESULT = ctypes.c_long


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wt.DWORD),
        ("Data2", wt.WORD),
        ("Data3", wt.WORD),
        ("Data4", wt.BYTE * 8),
    ]


IID_IACCESSIBLE = GUID(
    0x618736E0,
    0x3C3D,
    0x11CF,
    (wt.BYTE * 8)(0x81, 0x0C, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71),
)

user32 = ctypes.WinDLL("user32", use_last_error=True)
oleacc = ctypes.OleDLL("oleacc", use_last_error=True)
ole32 = ctypes.OleDLL("ole32", use_last_error=True)

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

user32.SendMessageTimeoutW.argtypes = (
    wt.HWND,
    wt.UINT,
    wt.WPARAM,
    wt.LPARAM,
    wt.UINT,
    wt.UINT,
    ctypes.POINTER(DWORD_PTR),
)
user32.SendMessageTimeoutW.restype = LRESULT
user32.EnumWindows.argtypes = (WNDENUMPROC, wt.LPARAM)
user32.EnumWindows.restype = wt.BOOL
user32.EnumChildWindows.argtypes = (wt.HWND, WNDENUMPROC, wt.LPARAM)
user32.EnumChildWindows.restype = wt.BOOL
user32.GetWindowTextLengthW.argtypes = (wt.HWND,)
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = (wt.HWND, wt.LPWSTR, ctypes.c_int)
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetClassNameW.argtypes = (wt.HWND, wt.LPWSTR, ctypes.c_int)
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowThreadProcessId.argtypes = (wt.HWND, ctypes.POINTER(wt.DWORD))
user32.GetWindowThreadProcessId.restype = wt.DWORD
user32.IsWindow.argtypes = (wt.HWND,)
user32.IsWindow.restype = wt.BOOL
user32.IsWindowVisible.argtypes = (wt.HWND,)
user32.IsWindowVisible.restype = wt.BOOL

oleacc.AccessibleObjectFromWindow.argtypes = (
    wt.HWND,
    wt.DWORD,
    ctypes.POINTER(GUID),
    ctypes.POINTER(ctypes.c_void_p),
)
oleacc.AccessibleObjectFromWindow.restype = HRESULT
ole32.CoInitializeEx.argtypes = (ctypes.c_void_p, wt.DWORD)
ole32.CoInitializeEx.restype = HRESULT
ole32.CoUninitialize.argtypes = ()
ole32.CoUninitialize.restype = None


class _ResultBase(object):
    """为结果对象提供轻量 repr，不依赖 dataclasses 或类型注解。"""

    def __repr__(self):
        values = ", ".join(
            "{}={!r}".format(name, getattr(self, name))
            for name in self.__slots__
        )
        return "{}({})".format(self.__class__.__name__, values)


class MessageAttempt(_ResultBase):
    """一次有超时保护的 WM_GETOBJECT 调用结果。"""

    __slots__ = (
        "hwnd",
        "class_name",
        "object_id",
        "delivered",
        "message_result",
        "last_error",
    )

    def __init__(
        self,
        hwnd,
        class_name,
        object_id,
        delivered,
        message_result,
        last_error,
    ):
        self.hwnd = hwnd
        self.class_name = class_name
        self.object_id = object_id
        self.delivered = delivered
        self.message_result = message_result
        self.last_error = last_error


class MsaaAttempt(_ResultBase):
    """可选的旧版 MSAA 兼容探测结果。"""

    __slots__ = ("hwnd", "acquired", "hresult", "error")

    def __init__(self, hwnd, acquired, hresult, error=None):
        self.hwnd = hwnd
        self.acquired = acquired
        self.hresult = hresult
        self.error = error


class UiaSnapshot(_ResultBase):
    """一次 UIA 查询看到的目标树状态。"""

    __slots__ = (
        "client_available",
        "reachable",
        "top_nodes",
        "render_nodes",
        "document_nodes",
        "content_ready",
        "error",
    )

    def __init__(
        self,
        client_available=False,
        reachable=False,
        top_nodes=0,
        render_nodes=0,
        document_nodes=0,
        content_ready=False,
        error=None,
    ):
        self.client_available = client_available
        self.reachable = reachable
        self.top_nodes = top_nodes
        self.render_nodes = render_nodes
        self.document_nodes = document_nodes
        self.content_ready = content_ready
        self.error = error


class ForceUiaResult(_ResultBase):
    """UIA 激活结果；可直接用于 ``if result:``。"""

    __slots__ = (
        "success",
        "status",
        "top_hwnd",
        "matched_top_hwnds",
        "target_hwnds",
        "attempts",
        "snapshot",
        "elapsed_ms",
        "msaa_attempts",
        "errors",
    )

    def __init__(
        self,
        success,
        status,
        top_hwnd,
        matched_top_hwnds,
        target_hwnds,
        attempts,
        snapshot,
        elapsed_ms,
        msaa_attempts=(),
        errors=None,
    ):
        self.success = success
        self.status = status
        self.top_hwnd = top_hwnd
        self.matched_top_hwnds = matched_top_hwnds
        self.target_hwnds = target_hwnds
        self.attempts = attempts
        self.snapshot = snapshot
        self.elapsed_ms = elapsed_ms
        self.msaa_attempts = msaa_attempts
        self.errors = [] if errors is None else errors

    def __bool__(self):
        return self.success


def _window_text(hwnd):
    length = user32.GetWindowTextLengthW(wt.HWND(hwnd))
    buffer = ctypes.create_unicode_buffer(max(length + 1, 2))
    user32.GetWindowTextW(wt.HWND(hwnd), buffer, len(buffer))
    return buffer.value


def _class_name(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(wt.HWND(hwnd), buffer, len(buffer))
    return buffer.value


def _window_process_id(hwnd):
    process_id = wt.DWORD()
    user32.GetWindowThreadProcessId(wt.HWND(hwnd), ctypes.byref(process_id))
    return int(process_id.value)


def _resolve_top_window(hwnd, title_substr, process_id):
    if hwnd is not None:
        hwnd = int(hwnd)
        if not user32.IsWindow(wt.HWND(hwnd)):
            raise ValueError(f"无效或已销毁的 HWND: 0x{hwnd:X}")
        if process_id is not None and _window_process_id(hwnd) != process_id:
            raise ValueError(f"HWND 0x{hwnd:X} 不属于进程 {process_id}")
        return hwnd, (hwnd,)

    if not title_substr and process_id is None:
        raise ValueError("hwnd、title_substr、process_id 至少提供一个")

    title_key = title_substr.casefold() if title_substr else None
    found = []

    @WNDENUMPROC
    def callback(candidate, _lparam):
        candidate = int(candidate)
        if not user32.IsWindowVisible(wt.HWND(candidate)):
            return True
        if process_id is not None and _window_process_id(candidate) != process_id:
            return True
        if title_key is not None and title_key not in _window_text(candidate).casefold():
            return True
        found.append(candidate)
        return True

    ctypes.set_last_error(0)
    if not user32.EnumWindows(callback, 0):
        error = ctypes.get_last_error()
        if error:
            raise ctypes.WinError(error)

    if not found:
        filters = []
        if title_substr:
            filters.append(f"标题包含 {title_substr!r}")
        if process_id is not None:
            filters.append(f"PID={process_id}")
        raise RuntimeError(f"未找到{'且'.join(filters)}的可见顶层窗口")

    return found[0], tuple(found)


def _enum_descendants(top_hwnd):
    descendants = []

    @WNDENUMPROC
    def callback(candidate, _lparam):
        descendants.append(int(candidate))
        return True

    ctypes.set_last_error(0)
    if not user32.EnumChildWindows(wt.HWND(top_hwnd), callback, 0):
        error = ctypes.get_last_error()
        if error:
            raise ctypes.WinError(error)
    return descendants


def _target_priority(hwnd):
    class_name = _class_name(hwnd)
    if class_name == "Chrome_RenderWidgetHostHWND":
        return 0, hwnd
    if class_name.startswith("Chrome_WidgetWin"):
        return 1, hwnd
    if class_name == "Intermediate D3D Window":
        return 2, hwnd
    return 3, hwnd


def _activation_targets(top_hwnd, max_targets):
    descendants = _enum_descendants(top_hwnd)
    descendants.sort(key=_target_priority)
    # 顶层 HWND 始终优先；EnumChildWindows 已递归枚举所有后代，而非仅直接子窗口。
    unique = dict.fromkeys((top_hwnd, *descendants))
    return tuple(unique)[:max_targets]


def _send_getobject(hwnd, object_id, timeout_ms):
    message_result = DWORD_PTR()
    ctypes.set_last_error(0)
    delivered = bool(
        user32.SendMessageTimeoutW(
            wt.HWND(hwnd),
            WM_GETOBJECT,
            wt.WPARAM(0),
            wt.LPARAM(object_id),
            SEND_FLAGS,
            timeout_ms,
            ctypes.byref(message_result),
        )
    )
    error = 0 if delivered else ctypes.get_last_error()
    return MessageAttempt(
        hwnd=hwnd,
        class_name=_class_name(hwnd),
        object_id=object_id,
        delivered=delivered,
        message_result=int(message_result.value),
        last_error=error,
    )


def _release_iunknown(pointer):
    """调用 IUnknown::Release，避免旧实现泄漏 COM 引用。"""
    vtable = ctypes.cast(
        pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
    ).contents
    release = ctypes.WINFUNCTYPE(wt.ULONG, ctypes.c_void_p)(vtable[2])
    release(pointer)


def _try_msaa(hwnd):
    """兼容极旧 CEF；此调用本身无超时，因此默认不开启。"""
    initialized = False
    accessible = ctypes.c_void_p()
    try:
        init_hr = int(ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED))
        initialized = init_hr >= 0
        hr = int(
            oleacc.AccessibleObjectFromWindow(
                wt.HWND(hwnd),
                wt.DWORD(OBJID_CLIENT),
                ctypes.byref(IID_IACCESSIBLE),
                ctypes.byref(accessible),
            )
        )
        acquired = hr >= 0 and bool(accessible.value)
        return MsaaAttempt(hwnd=hwnd, acquired=acquired, hresult=hr)
    except Exception as exc:
        return MsaaAttempt(hwnd=hwnd, acquired=False, hresult=-1, error=str(exc))
    finally:
        if accessible.value:
            _release_iunknown(accessible)
        if initialized:
            ole32.CoUninitialize()


def _count_uia_tree(control, max_depth, max_nodes):
    """迭代计数，避免深 UIA 树造成 Python 递归溢出。"""
    nodes = 0
    document_nodes = 0
    stack = [(control, 0)]
    while stack and nodes < max_nodes:
        current, depth = stack.pop()
        nodes += 1
        try:
            if getattr(current, "ControlTypeName", "") == "DocumentControl":
                document_nodes += 1
        except Exception:
            pass
        if depth >= max_depth:
            continue
        try:
            children = current.GetChildren()
        except Exception:
            continue
        stack.extend((child, depth + 1) for child in reversed(children))
    return nodes, document_nodes


def _uia_snapshot(
    top_hwnd,
    targets,
    *,
    max_depth,
    max_nodes,
    min_content_nodes,
):
    try:
        top_control = auto.ControlFromHandle(top_hwnd)
        top_nodes, document_nodes = _count_uia_tree(
            top_control, max_depth=max_depth, max_nodes=max_nodes
        )

        render_nodes = 0
        render_hwnds = [
            hwnd
            for hwnd in targets
            if _class_name(hwnd) == "Chrome_RenderWidgetHostHWND"
        ]
        for render_hwnd in render_hwnds:
            control = auto.ControlFromHandle(render_hwnd)
            count, documents = _count_uia_tree(
                control, max_depth=max_depth, max_nodes=max_nodes
            )
            render_nodes = max(render_nodes, count)
            document_nodes += documents

        # render_nodes 包含渲染 HWND 对应的根节点；至少再出现一个后代才算内容树。
        if render_hwnds:
            content_ready = render_nodes >= min_content_nodes
        else:
            # 某些 CEF 封装不保留标准渲染 HWND，此时使用 DocumentControl 兜底。
            content_ready = (
                document_nodes > 0 and top_nodes >= min_content_nodes
            )

        return UiaSnapshot(
            client_available=True,
            reachable=True,
            top_nodes=top_nodes,
            render_nodes=render_nodes,
            document_nodes=document_nodes,
            content_ready=content_ready,
        )
    except Exception as exc:
        return UiaSnapshot(
            client_available=True,
            reachable=False,
            error=f"UIA 查询失败: {exc}",
        )


def force_uia_detailed(
    hwnd=None,
    title_substr=None,
    *,
    process_id=None,
    timeout=5.0,
    poll_interval=0.2,
    message_timeout_ms=1000,
    max_targets=256,
    max_depth=30,
    max_nodes=10_000,
    min_content_nodes=2,
    verify=True,
    use_msaa_fallback=False,
):
    """激活 UIA 树并返回可诊断的结果。

    ``timeout`` 是轮询 UIA 内容树的最长时间。值为 0 时只执行一轮。
    ``message_timeout_ms`` 限制每个跨进程消息，防止目标卡死拖住调用者。
    ``use_msaa_fallback`` 仅建议用于不能响应 UIA -25 的旧版 CEF，因为
    ``AccessibleObjectFromWindow`` 自身没有可配置的消息超时。
    """
    if timeout < 0:
        raise ValueError("timeout 不能小于 0")
    if poll_interval <= 0:
        raise ValueError("poll_interval 必须大于 0")
    if message_timeout_ms <= 0:
        raise ValueError("message_timeout_ms 必须大于 0")
    if max_targets <= 0 or max_depth <= 0 or max_nodes <= 0:
        raise ValueError("max_targets、max_depth、max_nodes 必须大于 0")
    if min_content_nodes <= 0:
        raise ValueError("min_content_nodes 必须大于 0")

    started = time.monotonic()
    top_hwnd, matched = _resolve_top_window(hwnd, title_substr, process_id)
    # timeout=0 表示只跑一轮，不表示允许跨进程消息无限占用总时间。
    # 仍给双阶段消息留出一个小的全局预算，避免 256 个挂死 HWND 各等 1 秒。
    single_pass = timeout == 0
    effective_timeout = timeout or max(1.0, message_timeout_ms * 4 / 1000)
    deadline = started + effective_timeout

    attempts = []
    msaa_attempts = []
    errors = []
    activated_hwnds = set()
    targets = (top_hwnd,)
    snapshot = UiaSnapshot()

    while True:
        try:
            targets = _activation_targets(top_hwnd, max_targets=max_targets)
        except Exception as exc:
            errors.append(f"枚举子窗口失败: {exc}")
            targets = (top_hwnd,)

        for target in targets:
            if target in activated_hwnds or not user32.IsWindow(wt.HWND(target)):
                continue
            for object_id in (
                CHROMIUM_SCREEN_READER_OBJECT_ID,
                UIA_ROOT_OBJECT_ID,
            ):
                call_timeout = message_timeout_ms
                remaining_ms = int((deadline - time.monotonic()) * 1000)
                if remaining_ms <= 0:
                    break
                call_timeout = max(1, min(call_timeout, remaining_ms))
                attempts.append(_send_getobject(target, object_id, call_timeout))
            activated_hwnds.add(target)

            if (
                use_msaa_fallback
                and _class_name(target) == "Chrome_RenderWidgetHostHWND"
            ):
                msaa_attempts.append(_try_msaa(target))

            if time.monotonic() >= deadline:
                break

        # ControlFromHandle 对应真实 UIA 客户端查询，是完整激活序列的一部分。
        snapshot = _uia_snapshot(
            top_hwnd,
            targets,
            max_depth=max_depth,
            max_nodes=max_nodes,
            min_content_nodes=min_content_nodes,
        )

        delivered = any(item.delivered for item in attempts)
        if snapshot.content_ready:
            success = True
            status = "uia_tree_available"
            break
        if not snapshot.client_available:
            # 没安装验证库时仍保留旧接口“消息已成功送达”的语义。
            success = delivered
            status = "triggered_unverified" if delivered else "trigger_failed"
            if snapshot.error:
                errors.append(snapshot.error)
            break
        if not verify:
            success = delivered
            status = "activation_sent" if delivered else "trigger_failed"
            break
        if single_pass or time.monotonic() >= deadline:
            success = False
            status = "provider_unavailable_or_hard_disabled"
            if snapshot.error:
                errors.append(snapshot.error)
            break

        remaining = deadline - time.monotonic()
        time.sleep(min(poll_interval, max(remaining, 0)))

    elapsed_ms = round((time.monotonic() - started) * 1000)
    return ForceUiaResult(
        success=success,
        status=status,
        top_hwnd=top_hwnd,
        matched_top_hwnds=matched,
        target_hwnds=targets,
        attempts=tuple(attempts),
        snapshot=snapshot,
        elapsed_ms=elapsed_ms,
        msaa_attempts=tuple(msaa_attempts),
        errors=errors,
    )


def force_uia(hwnd=None, title_substr=None, wait=3.0):
    """兼容旧调用：激活目标窗口并返回 UIA 内容树是否可用。"""
    return force_uia_detailed(
        hwnd=hwnd,
        title_substr=title_substr,
        timeout=wait,
    ).success



def main(args):
    pass

