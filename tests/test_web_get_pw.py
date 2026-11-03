import socket
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

import pytest

import platforms.web_get.web_get_pw as web
from platforms.web_get.web_get_pw import (
    PageLoadTimeoutError,
    PageNotFoundError,
    UnsupportedModeError,
    match_text,
)


def test_match_text():
    assert match_text("Beta Shop", "Shop", use_wildcard=False)
    assert not match_text("Beta Shop", "shop", use_wildcard=False)
    assert match_text("Beta Shop", "Beta*", use_wildcard=True)
    assert not match_text("Beta Shop", "Shop", use_wildcard=True)
    assert match_text("anything", None, use_wildcard=False)


def test_unsupported_mode_and_missing_cdp():
    with pytest.raises(UnsupportedModeError):
        web.get(url="https://example.com/")
    with pytest.raises(UnsupportedModeError):
        web.get(title="x", mode="ie")
    with pytest.raises(UnsupportedModeError):
        web.get_active(mode="360se")
    with pytest.raises(UnsupportedModeError):
        web.get_all(mode="firefox")
    with pytest.raises(web.WebGetError):
        web.get(url="https://example.com/", mode="chrome")
    with pytest.raises(ValueError):
        web.get(mode="chrome", cdp_url="http://127.0.0.1:9")
    with pytest.raises(ValueError):
        web.visual_get(mode="other", web_type="chrome", cdp_url="http://127.0.0.1:9")


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _chrome_bin() -> Path:
    matches = sorted(Path.home().joinpath(".cache/ms-playwright").glob("chromium-*/chrome-linux64/chrome"))
    if not matches:
        pytest.skip("chromium binary not installed")
    return matches[-1]


def _wait_cdp(port: int) -> None:
    url = f"http://127.0.0.1:{port}/json/version"
    last = None
    for _ in range(50):
        try:
            with urllib.request.urlopen(url, timeout=0.2) as response:
                if response.status == 200:
                    return
        except Exception as exc:
            last = exc
            time.sleep(0.1)
    raise RuntimeError(f"cdp not ready: {last}")


def _launch_chrome(tmp_path, port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [
            str(_chrome_bin()),
            "--headless=new",
            "--no-first-run",
            "--no-default-browser-check",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={tmp_path}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_cdp(port)
    except Exception:
        proc.kill()
        raise
    return proc


class _Hang:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(1)
        self.stopped = False
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        while not self.stopped:
            self.sock.settimeout(0.5)
            try:
                conn, _addr = self.sock.accept()
            except socket.timeout:
                continue
            try:
                conn.recv(4096)
                conn.sendall(
                    b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nTransfer-Encoding: chunked\r\n\r\n"
                )
                while not self.stopped:
                    threading.Event().wait(0.2)
            except Exception:
                pass
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

    def close(self):
        self.stopped = True
        self.sock.close()


@pytest.fixture
def running_chrome(tmp_path):
    port = _free_port()
    proc = _launch_chrome(tmp_path, port)
    endpoint = f"http://127.0.0.1:{port}"
    browser = web.connect(endpoint)
    context = browser.contexts[0]
    first = context.new_page()
    first.goto("data:text/html,<title>Alpha Shop</title><p>a</p>")
    second = context.new_page()
    second.goto("data:text/html,<title>Beta Shop</title><p>b</p>")
    try:
        yield endpoint
    finally:
        web.close_connection(endpoint)
        proc.kill()
        proc.wait(timeout=5)


def test_get_newest_fuzzy_and_get_all(running_chrome):
    newest = web.get(title="Shop", mode="chrome", cdp_url=running_chrome, load_timeout=0)
    assert newest.title() == "Beta Shop"
    wildcard = web.get(title="Alpha*", mode="chrome", use_wildcard=True, cdp_url=running_chrome, load_timeout=0)
    assert wildcard.title() == "Alpha Shop"
    by_url = web.get(url="Beta", mode="edge", cdp_url=running_chrome, load_timeout=0)
    assert "Beta" in by_url.url
    pages = web.get_all(title="Shop", mode="chrome", cdp_url=running_chrome)
    assert [page.title() for page in pages] == ["Alpha Shop", "Beta Shop"]
    everything = web.visual_get_all(mode="all", web_type="chrome", cdp_url=running_chrome)
    assert len(everything) >= 2
    titled = web.visual_get_all(mode="title", value="Alpha", web_type="chrome", cdp_url=running_chrome)
    assert [page.title() for page in titled] == ["Alpha Shop"]


def test_visual_get_and_active_and_open_page(running_chrome):
    page = web.visual_get(
        mode="title",
        value="Alpha Shop",
        web_type="chrome",
        cdp_url=running_chrome,
        load_timeout=0,
    )
    assert page.title() == "Alpha Shop"
    active = web.visual_get(mode="activated", web_type="chrome", cdp_url=running_chrome, load_timeout=0)
    assert active.title() in {"Alpha Shop", "Beta Shop"}
    opened = web.get(
        title="missing-title",
        mode="chrome",
        open_page=True,
        page_url="data:text/html,<title>Opened</title>",
        cdp_url=running_chrome,
        load_timeout=5,
    )
    assert opened.title() == "Opened"
    with pytest.raises(PageNotFoundError):
        web.get(title="still-missing", mode="chrome", cdp_url=running_chrome, load_timeout=0)


def test_load_timeout_stops(tmp_path):
    hang = _Hang()
    port = _free_port()
    proc = _launch_chrome(tmp_path, port)
    endpoint = f"http://127.0.0.1:{port}"
    try:
        browser = web.connect(endpoint)
        page = browser.contexts[0].new_page()
        page.goto(f"http://127.0.0.1:{hang.port}/slow", wait_until="commit", timeout=3000)
        with pytest.raises(PageLoadTimeoutError):
            web.get(url="/slow", mode="chrome", cdp_url=endpoint, load_timeout=0.4, stop_if_timeout=True)
    finally:
        web.close_connection(endpoint)
        proc.kill()
        proc.wait(timeout=5)
        hang.close()
