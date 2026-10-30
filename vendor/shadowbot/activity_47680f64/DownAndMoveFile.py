# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
import xbot_visual
import os
import shutil
import time
from .CreateDir import main as create_dir


def sort_file_by_create_time(dir_path):
    return xbot_visual.dir.find_files(path=dir_path, patterns="*.*", find_subdir=False, skip_hidden_file=False, is_sort=True, sort_by="create_time", sort_way="decrease", _block=("__内置指令", 14, "获取文件列表"))


class DownloadFile:
    def __init__(self, max_wait, download_path, old_file_cnt):
        # 初始化参数
        self.max_wait = max_wait

        # 获取downloads目录
        self.download_dir_path = download_path 

        # 原始文件数量
        self.old_file_count = old_file_cnt

        # 保存文件列表
        self.save_file_paths = []

    # 检测所有文件是否下载完毕
    def is_down_file_over(self):
        print("等待文件下载完成...")
        wait = self.max_wait
        time.sleep(3)
        while wait > 0:
            file_name = sort_file_by_create_time(self.download_dir_path)
            file_str = "".join(file_name)
            if ".crdownload" not in file_str:
                self.new_file_cnt = len(file_name)-self.old_file_count
                if self.new_file_cnt > 0:
                    print(f"下载{self.new_file_cnt}个新文件！")
                    break
                
            time.sleep(1)
            wait -= 1
        else:
            raise TimeoutError(f"下载文件超过最大等待时长: {self.max_wait}秒")

    def get_file_path(self):
        file_paths = sort_file_by_create_time(self.download_dir_path)
        if len(file_paths) <= self.old_file_count:
            raise Exception("文件数量低于预期，请检查下载请求是否被浏览器拦截！")

        if not file_paths:
            raise FileNotFoundError(f"目录下没有发现文件： 【{self.download_dir_path}】")

        for file_path in file_paths[:self.new_file_cnt]:
            yield file_path


    def move_file(self, args):
        """
        这里可以忽略多文件的情况，按照设定Downloads文件夹不应该有多个文件
        """
        root_dir = args.get("保存文件夹路径")
        is_rename = args.get("是否重命名")
        new_file_name = args.get("重命名_文件名")

        l = ["\\", "/", ":", "*", "?", '"', "'", "<", ">", "|"]
        for i in l:
            new_file_name = new_file_name.replace(i , "")

        # 创建保存路径
        # 创建多级路径
        # move_dir = f"{root_dir}\\{platform_main}-{platform_sub}-【{data_set}】\\{date_stamp}"

        move_dir = root_dir
        create_dir(args={"创建文件夹路径": move_dir})

        # 获取旧文件路径
        for idx, old_file_path in enumerate(self.get_file_path()):
            file_name = os.path.basename(old_file_path)

            if is_rename and new_file_name:
                # 拼接新文件路径
                file_suffix = os.path.splitext(old_file_path)[-1]
                new_file_name = new_file_name+ f"_{idx+1}" + file_suffix
                print(f"下载【{file_name}】重命名为【{new_file_name}】")
            else:
                new_file_name = file_name

            # 文件转存
            save_file_path = os.path.join(move_dir, new_file_name)

            if old_file_path == save_file_path:
                self.save_file_paths.append(save_file_path)
            else:
                shutil.copy2(old_file_path, save_file_path)
                os.remove(old_file_path)
                # shutil.move(old_file_path, save_file_path)
                self.save_file_paths.append(save_file_path)



def main(args):
    max_wait = args.get("等待下载完成最大时长")
    chrome_download_path = args.get("浏览器下载保存路径")
    old_file_cnt = args.get("下载前文件数量", 0)

    down = DownloadFile(max_wait, chrome_download_path, old_file_cnt)

     # 检查是否存在正在下载的文件
    down.is_down_file_over()

     # 移动文件到目的路径
    down.move_file(args)

    # 保存路径返回出去
    args["文件路径列表"] = down.save_file_paths
    return down.save_file_paths
    


    