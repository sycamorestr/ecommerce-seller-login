"""离线检查登录结果和验证码处理，不访问千牛或云码。"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeout

import captcha as c
import login as q


class LoginTests(unittest.TestCase):
    def test_existing_login_redirect_skips_credentials(self):
        page = Mock(url="https://myseller.taobao.com/home.htm/QnworkbenchHome/")
        result = q.qianniu_login(page, "test-account", "test-password")
        self.assertTrue(result.ok)
        page.frame_locator.assert_not_called()

    def test_empty_token_is_not_replaced_by_environment(self):
        with patch.dict(os.environ, {"YUNMA_TOKEN": "stale-token"}):
            with patch.object(q, "login_steps") as steps:
                page = Mock()
                result = q.qianniu_login(page, "test-account", "test-password", "")
        self.assertTrue(result.ok)
        steps.assert_called_once_with(page, "test-account", "test-password", "", 5)

    def test_known_login_errors_return_readable_result(self):
        for error in (q.NeedsHumanError("短信验证"), q.QianniuLoginError("密码错误")):
            with self.subTest(error=error):
                with patch.object(q, "login_steps", side_effect=error):
                    result = q.qianniu_login(Mock(), "test-account", "test-password")
                self.assertFalse(result.ok)
                self.assertEqual(result.error, str(error))

    def test_unexpected_errors_keep_original_traceback(self):
        with patch.object(q, "login_steps", side_effect=RuntimeError("test failure")):
            with self.assertRaisesRegex(RuntimeError, "test failure"):
                q.qianniu_login(Mock(), "test-account", "test-password")


class CaptchaTests(unittest.TestCase):
    def test_yunma_request_payload(self):
        conn = Mock()
        conn.getresponse.return_value.read.return_value = json.dumps({"msg": "识别成功", "data": {"data": "120"}}).encode()
        with patch.object(c.http.client, "HTTPConnection", return_value=conn):
            result = c.yunma_recg("test-token", "image")
        self.assertEqual(result["msg"], "识别成功")
        self.assertEqual(conn.request.call_args.args, ("POST", c.YUNMA_PATH))
        self.assertEqual(json.loads(conn.request.call_args.kwargs["body"]), {"image": "image", "token": "test-token", "type": 20226})
        conn.close.assert_called_once()

    def test_cloud_connection_closes_on_failure(self):
        conn = Mock()
        conn.request.side_effect = OSError("network failure")
        with patch.object(c.http.client, "HTTPConnection", return_value=conn):
            with self.assertRaisesRegex(OSError, "network failure"):
                c.yunma_recg("test-token", "image")
        conn.close.assert_called_once()

    def test_image_composition_and_base64_round_trip(self):
        tip = Image.new("RGBA", (100, 30), (1, 2, 3, 255))
        background = Image.new("RGBA", (320, 180), (4, 5, 6, 255))
        image = c.decode_image(c.encode_image(c.join_images(tip, background)))
        self.assertEqual(image.size, (320, 221))
        self.assertEqual(image.getpixel((0, 0)), (1, 2, 3, 255))
        self.assertEqual(image.getpixel((0, 35)), (255, 255, 255, 255))
        self.assertEqual(image.getpixel((0, 41)), (4, 5, 6, 255))

    def test_missing_token_hands_captcha_to_human(self):
        with patch.object(c, "yunma_recg") as cloud:
            with self.assertRaises(c.NeedsHumanError):
                c.handle_verification(Mock(), "", 5)
            cloud.assert_not_called()

    def test_missing_images_do_not_count_as_verification_success(self):
        with tempfile.TemporaryDirectory() as folder:
            with (
                patch.object(c, "CACHE_DIR", Path(folder)),
                patch.object(c, "sleep"),
                patch.object(c, "is_visible", return_value=True),
                patch.object(c, "collect_data_images", return_value=[]),
                patch.object(c, "yunma_recg") as cloud,
            ):
                with self.assertRaises(c.NeedsHumanError):
                    c.handle_verification(Mock(), "test-token", 2)
                cloud.assert_not_called()

    def test_recognized_image_drags_the_expected_distance(self):
        images = [
            "data:image/png;base64," + c.encode_image(Image.new("RGB", size))
            for size in ((100, 30), (320, 180))
        ]
        page = Mock()
        page.frame_locator.return_value.locator.return_value.first.bounding_box.return_value = {
            "x": 10, "y": 20, "width": 40, "height": 40,
        }
        with tempfile.TemporaryDirectory() as folder:
            with (
                patch.object(c, "CACHE_DIR", Path(folder)),
                patch.object(c, "sleep"),
                patch.object(c, "is_visible", side_effect=[True, False]),
                patch.object(c, "collect_data_images", return_value=images),
                patch.object(c, "yunma_recg", return_value={"msg": "识别成功", "data": {"data": "120"}}),
                patch.object(c.random, "randint", return_value=0),
                patch.object(c, "mouse_drag") as drag,
            ):
                c.handle_verification(page, "test-token", 2)
                drag.assert_called_once_with(page, 30, 40, 116, 40, overshoot=True)

    def test_visibility_only_treats_timeout_as_absence(self):
        frame = Mock()
        wait = frame.locator.return_value.first.wait_for
        wait.side_effect = PlaywrightTimeout("not found")
        self.assertFalse(c.is_visible(frame, ".captcha"))
        wait.side_effect = PlaywrightError("invalid selector")
        with self.assertRaises(PlaywrightError):
            c.is_visible(frame, ".captcha")


if __name__ == "__main__":
    unittest.main()
