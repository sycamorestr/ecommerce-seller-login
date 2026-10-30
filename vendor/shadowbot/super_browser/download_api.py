import json
from pathlib import Path

from . import ziniao_v6
from .utils_v6 import  Version, get_version


def get_download_path_v5():
   preferences_Path = Path.home() / r"AppData\Local\SuperBrowser\User Data\BrowserWorkbench_1\Default\Preferences"

   if not preferences_Path.exists():
      sb_Path = Path.home() / r"AppData\Local\SuperBrowserClient\SuperBrowser"
      if not sb_Path.exists():
         raise FileNotFoundError("Cannot find SuperBrowserClient installation directory.")
      data_temps = list(sb_Path.glob("*/AsyncStorage/BROWSER_DATATEMP_FOLDER.data"))
      data_temps.sort(reverse=True)
      if len(data_temps) == 0:
         raise FileNotFoundError("Cannot find BROWSER_DATATEMP_FOLDER.data file.")

    #   print(data_temps[0])      
      cache_text = data_temps[0].read_text(encoding='utf-8').strip()
      cache_path = Path(cache_text)
      if not cache_text or not cache_path.exists():
         raise FileNotFoundError("Cannot find SuperBrowser cache path.")
      
      preferences_Path = cache_path / "User Data/BrowserWorkbench_1/Default/Preferences"
   
   if not preferences_Path.exists():
      raise FileNotFoundError("Cannot find SuperBrowser preferences file.")
   
   json_data = json.loads(preferences_Path.read_text(encoding='utf-8'))

   download_config = json_data.get("download")
   default_directory = download_config["default_directory"]
   default_directory = str(Path(default_directory).parent)
   prompt_for_download = download_config.get("prompt_for_download")
   return default_directory, prompt_for_download


def get_download_path_v6():
    """
    获取紫鸟v6当前活跃实例的下载文件保存位置。
    通过 Local State 中的 active_time 判断哪个实例是当前活跃的。
    """
    userdata_path = Path.home() / r"AppData\Roaming\ziniaobrowser\userdata"

    if not userdata_path.exists():
        raise FileNotFoundError("Cannot find ziniaobrowser userdata: %s" % userdata_path)

    latest_id = None
    latest_time = 0

    for instance_dir in userdata_path.glob("chrome_*"):
        local_state = instance_dir / "Local State"
        if not local_state.exists():
            continue

        try:
            data = json.loads(local_state.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        active_time = (
            data.get("profile", {})
            .get("info_cache", {})
            .get("Default", {})
            .get("active_time", 0)
        )
        if active_time > latest_time:
            latest_time = active_time
            latest_id = instance_dir.name

    if latest_id is None:
        raise FileNotFoundError("Cannot determine active instance in: %s" % userdata_path)

    preferences_path = userdata_path / latest_id / "Default" / "Preferences"
    if not preferences_path.exists():
        raise FileNotFoundError("Cannot find Preferences for: %s" % latest_id)

    json_data = json.loads(preferences_path.read_text(encoding="utf-8"))

    # 关闭"下载前询问"时路径存在 savefile，开启时存在 download
    savefile_config = json_data.get("savefile", {})
    download_config = json_data.get("download", {})

    directory = (
        download_config.get("default_directory")
    )

    if not directory:
        raise FileNotFoundError("No default_directory for: %s" % latest_id)

    prompt_for_download = download_config.get("prompt_for_download")
    return str(Path(directory).parent), prompt_for_download


def get_download_path():
    if get_version() == Version.V5:
        download_path, is_check = get_download_path_v5()
    else:
        download_path, is_check = get_download_path_v6()
    return download_path, is_check


def download_handler(web_page, selector_or_element, save_file_dir, save_file_name, wait_time, dialog_timeout, **kwargs):
    # download_file_name = download(web_page, selector_or_element, save_file_dir, save_file_name, wait_time, download_path, is_check, dialog_timeout)
    # return download_file_name
    
    return ziniao_v6.download_handler(web_page, selector_or_element, save_file_dir, save_file_name, wait_time, dialog_timeout)


def upload_handler(web_page, selector_or_element, file_names, simulative, dialog_timeout):
    # upload(web_page, selector_or_element, file_names, simulative, dialog_timeout)
    ziniao_v6.upload_handler(web_page, selector_or_element, file_names, simulative, dialog_timeout)