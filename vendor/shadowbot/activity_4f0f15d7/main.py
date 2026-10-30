import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        xbot_visual.image.click(window_kind="screen", window="", template_images=[package.image_selector("图像")], anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", clicks="click", button="left", keys="null", move_mouse=True, timeout="5", delay_after="1", _block=("main", 1, "点击图像"))
    finally:
        pass
