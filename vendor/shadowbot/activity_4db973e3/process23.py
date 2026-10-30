import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        # 91330110MA2GKLF15T
        # https://inv-veri.chinatax.gov.cn/
        process_result = xbot_visual.process.run(process="emphasize_color", package=__name__, inputs={
            "验证码图片路径": "C:\\Users\\songp\\Desktop\\download.png",
            "要突出的颜色": "蓝色",
            "输出图片路径": "C:\\Users\\songp\\Desktop\\out.png",
            }, outputs=[
            "结果图片路径",
        ], _block=("测试-突出验证码颜色", 3, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.结果图片路径, _block=("测试-突出验证码颜色", 4, "打印日志"))
    finally:
        pass
