"""运行入口：读取配置 → 连接指定浏览器 → 在新标签页登录。"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from login import qianniu_login

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    if not config.get("cdp_url", "").strip():
        raise ValueError("请在 config.json 中填写已有浏览器环境的 cdp_url（调试地址）。")
    if not config["account"].strip() or not config["password"].strip():
        raise ValueError("请先在 config.json 中填写账号和密码。")
    config.setdefault("yunma_token", "")
    config.setdefault("retries", 5)
    return config


def main() -> int:
    config = load_config()
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(
            config["cdp_url"], no_defaults=True,
        )
        # 使用现有环境的 Cookie，在新标签页操作。
        context = browser.contexts[0]
        page = context.new_page()
        print("已连接指定浏览器环境，正在打开千牛……")
        result = qianniu_login(
            page=page,
            account=config["account"],
            password=config["password"],
            yunma_token=config["yunma_token"],
            retries=config["retries"],
        )
        if result.ok:
            print("自动登录流程已完成，请在浏览器中确认登录结果和店铺。")
        else:
            print("自动登录未完成：" + result.error)
        print("程序结束，浏览器和标签页保持打开，可继续手动操作。")
        # 退出 with 只断开 Playwright 连接，不关闭已有浏览器。
        return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
