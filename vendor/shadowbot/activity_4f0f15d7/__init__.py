from .import package
import xbot_visual
from . import slider_captcha
from . import slider_acceleration_captcha
from . import shopee_captcha
from . import arithmetic_captcha
from . import zfb_rotate_captcha
from . import dewu_captcha
from . import temu_connect_captcha
from . import shopee_similarity_silder_captcha
from . import temu_rotate_captcha
from . import temu_drag_photo_captcha
from . import temu_click_same_point_captcha
from . import shopee_similarity_move_captcha
from . import fruit_content_captcha
from . import svg_animation_captcha
from . import gif_math_captcha
from . import tysfrzcs_slider_captcha
from . import keeta_color_connect_capthca
from . import wph_color_charactor_captcha

def process3(背景元素,缺块元素,拖拽滑块,偏移距离,窗口对象,重试次数):
    """
    滑块拼图验证免费版(win)
    解决大部分滑块拼图验证码(win)
    * @param 背景元素，
    * @param 缺块元素，
    * @param 拖拽滑块，
    * @param 偏移距离，
    * @param 窗口对象，
    * @param 重试次数，
    """
    outputs = []
    inputs = {"背景元素":背景元素,"缺块元素":缺块元素,"拖拽滑块":拖拽滑块,"偏移距离":偏移距离,"窗口对象":窗口对象,"重试次数":重试次数}
    extension_module, activity_func = xbot_visual.process.activity_entry("xbot_extensions.activity_4f0f15d7.process3", __name__)
    try:
        return xbot_visual.process.run(process="xbot_extensions.activity_4f0f15d7.process3",package=__name__,inputs=inputs, outputs=outputs)
    finally:
        xbot_visual.process.replace_activity_module_to_entry_method("xbot_extensions.activity_4f0f15d7.process3", extension_module, activity_func)

