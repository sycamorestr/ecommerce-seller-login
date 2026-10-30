# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv


import json


def find_value(response_body_list: list, keys, match_type=0) -> None:
    def _find_value(data, paths: list):
        if isinstance(data, dict):
            for k, v in data.items():
                paths.append('["{}"]'.format(k))
                _find_value(v, paths)
                paths.pop(-1)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                paths.append('[{}]'.format(i))
                _find_value(item, paths)
                paths.pop(-1)
        else:
            for key in keys:
                if match_type == 0:
                    if str(key) == str(data):
                        result.append("{} -> {}".format("".join(paths), data))
                else:
                    if str(key) in str(data):
                        result.append("{} -> {}".format("".join(paths), data))
    for response_body in response_body_list:
        url = response_body["url"]
        body = response_body["body"]
        result = []
        try:
            body = json.loads(body)
        except Exception as e:
            pass
        _find_value(body, [])
        if len(result) != 0:
            print(url)
            print(response_body["body"])
            for r in result:
                print(r)

            print("分割线".center(200, "-"))

def main(args):
    pass
