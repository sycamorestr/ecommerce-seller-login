"""影刀应用 cookie 的 main 顺序：获取已打开网页 → 保存 → Cookie登录 → 获取指定 Cookie。

浏览器需已带远程调试端口。不要把本机桌面路径写进仓库。
"""
import argparse
import time

from platforms.cookie.cookie_login_pw import get_cookie, load_cookies, save_cookies
from platforms.web_get.web_get_pw import visual_get


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdp-url", required=True)
    parser.add_argument("--cookie-file", required=True)
    args = parser.parse_args()
    page = None
    attempt = 0
    while attempt <= 3:
        try:
            page = visual_get(
                web_type="chrome",
                mode="activated",
                value="",
                use_wildcard=False,
                silent_running=False,
                wait_load_completed=True,
                load_timeout=20,
                stop_load_if_load_timeout="handleExcept",
                open_page=False,
                url=None,
                cdp_url=args.cdp_url,
            )
            break
        except Exception as exc:
            if attempt == 3:
                raise
            print(exc)
            attempt += 1
            time.sleep(3)
    save_cookies(page, args.cookie_file, partition_key="")
    load_cookies(page, args.cookie_file, add_local_storage=True)
    print(get_cookie("1111", "chrome", name=None, cdp_url=args.cdp_url))


if __name__ == "__main__":
    main()
