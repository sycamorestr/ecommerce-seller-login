"""离线检查配置读取和已有浏览器的连接，不使用真实账号。"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import main as app
from login import LoginResult


def config_values(**overrides):
    return {
        "cdp_url": "http://127.0.0.1:19222",
        "account": "test-account", "password": "test-password",
        "yunma_token": "", "retries": 5,
        **overrides,
    }


class ConfigTests(unittest.TestCase):
    def test_config_is_independent_of_working_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "platform" / "config.json"
            path.parent.mkdir()
            values = {"cdp_url": "http://127.0.0.1:19222", "account": "测试账号", "password": ' p%\\"$word '}
            path.write_text(json.dumps(values), encoding="utf-8-sig")
            original_cwd = Path.cwd()
            try:
                os.chdir(folder)
                with patch.object(app, "CONFIG_PATH", path):
                    loaded = app.load_config()
            finally:
                os.chdir(original_cwd)
            self.assertEqual(loaded["password"], values["password"])
            self.assertEqual(loaded["yunma_token"], "")
            self.assertEqual(loaded["retries"], 5)
            self.assertEqual(loaded["cdp_url"], values["cdp_url"])

    def test_missing_address_stops_before_connecting(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            for address in (None, " "):
                values = config_values(cdp_url=address)
                if address is None:
                    values.pop("cdp_url")
                path.write_text(json.dumps(values), encoding="utf-8")
                with patch.object(app, "CONFIG_PATH", path), patch.object(app, "sync_playwright") as start:
                    with self.assertRaisesRegex(ValueError, "cdp_url"):
                        app.main()
                    start.assert_not_called()

    def test_blank_credentials_stop_before_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            for key in ("account", "password"):
                with self.subTest(key=key):
                    path.write_text(json.dumps(config_values(**{key: " "})), encoding="utf-8")
                    with patch.object(app, "CONFIG_PATH", path), patch.object(app, "sync_playwright") as start:
                        with self.assertRaises(ValueError):
                            app.main()
                        start.assert_not_called()

    def test_missing_config_shows_original_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(app, "CONFIG_PATH", Path(folder) / "missing.json"):
                with self.assertRaises(FileNotFoundError):
                    app.main()


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.runtime = MagicMock()
        self.chromium = self.runtime.__enter__.return_value.chromium
        self.browser = self.chromium.connect_over_cdp.return_value
        self.context = MagicMock()
        self.browser.contexts = [self.context]
        self.page = self.context.new_page.return_value
        self.context.pages = [self.page]
        self.config = config_values()
        self.login = Mock()
        for patcher in (
            patch.object(app, "qianniu_login", self.login),
            patch.object(app, "sync_playwright", return_value=self.runtime),
            patch.object(app, "load_config", return_value=self.config),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_success_reuses_context_and_keeps_browser(self):
        self.login.return_value = LoginResult(True)
        self.assertEqual(app.main(), 0)
        self.login.assert_called_once_with(
            page=self.page, account="test-account", password="test-password",
            yunma_token="", retries=5,
        )
        self.chromium.connect_over_cdp.assert_called_once_with("http://127.0.0.1:19222", no_defaults=True)
        self.chromium.launch.assert_not_called()
        self.browser.new_context.assert_not_called()
        self.browser.close.assert_not_called()
        self.context.close.assert_not_called()
        self.page.close.assert_not_called()

    def test_manual_verification_keeps_window_after_program_exits(self):
        self.login.return_value = LoginResult(False, "短信验证")
        self.assertEqual(app.main(), 1)
        self.browser.close.assert_not_called()
        self.context.close.assert_not_called()
        self.page.close.assert_not_called()

    def test_unexpected_login_error_propagates_and_keeps_browser(self):
        self.login.side_effect = RuntimeError("test failure")
        with self.assertRaisesRegex(RuntimeError, "test failure"):
            app.main()
        self.browser.close.assert_not_called()
        self.context.close.assert_not_called()
        self.page.close.assert_not_called()

    def test_page_creation_failure_keeps_browser(self):
        self.context.new_page.side_effect = RuntimeError("page failure")
        with self.assertRaisesRegex(RuntimeError, "page failure"):
            app.main()
        self.browser.close.assert_not_called()
        self.context.close.assert_not_called()

    def test_connection_failure_does_not_launch_a_new_browser(self):
        self.chromium.connect_over_cdp.side_effect = RuntimeError("connection failed")
        with self.assertRaisesRegex(RuntimeError, "connection failed"):
            app.main()
        self.chromium.launch.assert_not_called()
        self.login.assert_not_called()


if __name__ == "__main__":
    unittest.main()
