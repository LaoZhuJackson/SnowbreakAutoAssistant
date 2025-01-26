import concurrent.futures
import os
import re
import shutil
import subprocess
import time
import traceback
import zipfile
from urllib.request import urlopen

import requests
from tqdm import tqdm

from app.common.config import config
from app.common.setting import VERSION
from app.common.signal_bus import signalBus


class Updater:
    def __init__(self, download_url=None, log_widget=None):
        self.progress_callback = None

        self.log_widget = log_widget
        self.current_version = VERSION
        self.latest_version = None
        self.api_urls = [
            "https://gitee.com/laozhu520/auto_chenbai/releases/latest",
            "https://api.github.com/repos/LaoZhuJackson/SnowbreakAutoAssistant/releases/latest",
        ]
        # 设置代理
        if config.update_proxies.value:
            self.proxies = {
                'http': f'http://127.0.0.1:{config.update_proxies.value}',
                'https': f'http://127.0.0.1:{config.update_proxies.value}'
            }
        else:
            self.proxies = None
        self.download_url = download_url
        self.cover_folder_path = os.path.abspath('./')
        self.temp_path = os.path.abspath("./temp")
        self.exe_path = os.path.abspath("./app/resource/binary/7za.exe")
        self.aria2_path = os.path.abspath("./app/resource/binary/aria2c.exe")

        if download_url is None:
            # 执行更新本程序
            fastest_mirror = self.find_fastest_mirror(self.api_urls)
            try:
                with requests.get(fastest_mirror, proxies=self.proxies, stream=True) as response:
                    if response.status_code == 200:
                        data = response.json()
                        # print(f"{data=}")
                        if "github" in fastest_mirror:
                            self.download_url = self.check_for_updates_github(data)
                        else:
                            self.download_url = self.check_for_updates_gitee(data['release'])
                        print(f"下载链接: {self.download_url}")
                    else:
                        print(f"网站返回状态码不等于200:{response.status_code}")
            except Exception as e:
                print(f"出现错误：{e}")
                traceback.print_exc()
        else:
            print(f"下载链接: {self.download_url}")
        self.download_file_path = os.path.join(self.temp_path, os.path.basename(
            self.download_url) if self.download_url else os.path.join(self.temp_path, 'update.zip'))
        self.extract_folder_path = self.temp_path

    def check_for_updates_github(self, data):
        print("检查更新中...")
        download_url = None
        latest_version = data['tag_name']
        self.latest_version = latest_version
        for asset in data["assets"]:
            if "full" not in asset["browser_download_url"]:
                # 增量更新
                download_url = asset["browser_download_url"]
                break
        if download_url is None:
            raise Exception("没有找到增量更新包")

        # 比较版本号
        if latest_version != self.current_version:
            print(f"发现新版本：{self.current_version} -> {latest_version}")
        else:
            print(f"本地版本: {self.current_version}")
            print(f"远程版本: {latest_version}")
            print("当前已是最新版本")
        # 返回带文件名的url
        return download_url

    def check_for_updates_gitee(self, data):
        print("检查更新中...")
        download_url = None
        latest_version = data['tag']['name']
        self.latest_version = latest_version
        for asset in data["release"]["attach_files"]:
            if "full" not in asset:
                # 增量更新
                download_url = asset['cli_download_url']
                break
        if download_url is None:
            raise Exception("没有找到增量更新包")

        # 比较版本号
        if latest_version != self.current_version:
            print(f"发现新版本：{self.current_version} -> {latest_version}")
        else:
            print(f"本地版本: {self.current_version}")
            print(f"远程版本: {latest_version}")
            print("当前已是最新版本")
        # 返回带文件名的url
        return download_url

    def find_fastest_mirror(self, mirror_urls, timeout=5):
        """测速并找到最快的镜像。"""
        def check_mirror(mirror_url):
            try:
                start_time = time.time()
                response = requests.head(mirror_url, proxies=self.proxies, timeout=timeout, allow_redirects=True)
                end_time = time.time()
                if response.status_code == 200:
                    # print(f"{mirror_url=},{end_time - start_time}")
                    return mirror_url, end_time - start_time
            except Exception as e:
                print(e)
            return None, None

        # 初始化最快的镜像变量
        fastest_mirror = None
        fastest_time = float('inf')

        # 遍历 URL 进行测速
        for url in mirror_urls:
            mirror, response_time = check_mirror(url)
            if mirror and response_time < fastest_time:
                fastest_mirror = mirror
                fastest_time = response_time

        # if fastest_mirror:
        #     print(f"最快的镜像是: {fastest_mirror}，响应时间: {fastest_time}")
        # else:
        #     print("没有可用的镜像")

        return fastest_mirror if fastest_mirror else mirror_urls[0]

    def download_update(self):
        print("下载更新中...")
        try:
            if os.path.exists(self.download_file_path):
                print("文件已存在")
                return True
            os.makedirs(os.path.dirname(self.download_file_path), exist_ok=True)
            # print(self.aria2_path)
            if os.path.exists(self.aria2_path):
                print("使用下载方式：aria2")
                command = [self.aria2_path, "--max-connection-per-server=16",
                           "--dir={}".format(os.path.dirname(self.download_file_path)),
                           "--out={}".format(os.path.basename(self.download_file_path)), self.download_url]

                # 添加代理支持
                if self.proxies and 'http' in self.proxies:
                    command.append(f"--http-proxy={self.proxies['http']}")
                if self.proxies and 'https' in self.proxies:
                    command.append(f"--https-proxy={self.proxies['https']}")

                if os.path.exists(self.download_file_path):
                    command.insert(2, "--continue=true")
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                progress_pattern = re.compile(r'\[#\w+\s+\S+/\S+\((\d+)%\)')
                try:
                    for line in process.stdout:
                        match = progress_pattern.search(line)
                        # print(line)
                        if match:
                            # print(f"匹配内容：{match.group(1)}")
                            progress = int(match.group(1))
                            # self.progress_callback(progress)
                            signalBus.checkUpdateSig.emit(progress)
                except Exception as e:
                    print(e)
            else:
                print("使用下载方式：requests.get")
                response = requests.get(self.download_url, proxies=self.proxies, stream=True)
                print(f"response:{response}")
                file_size = int(response.headers.get('Content-Length', 0))
                print(f"size:{file_size}")
                downloaded_size = 0

                with requests.get(self.download_url, proxies=self.proxies, stream=True, timeout=600) as r:
                    with open(self.download_file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                if self.progress_callback:
                                    progress = int((downloaded_size / file_size) * 100)
                                    self.progress_callback(progress)
            print("下载完成")
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            traceback.print_exc()
            return False

    def extract_update(self):
        print("解压更新文件...")
        try:
            if os.path.exists(self.exe_path):
                # 命令行运行7z
                subprocess.run([self.exe_path, "x", self.download_file_path, f"-o{self.temp_path}", "-aoa"], check=True)
            else:
                # 没有7z就用自带的
                shutil.unpack_archive(self.download_file_path, self.extract_folder_path)
            print("解压完成")
        except Exception as e:
            print(f"解压失败: {e}")

    def apply_update(self):
        print("应用更新...")
        try:
            # 复制解压的文件到项目目录
            for item in os.listdir(self.extract_folder_path):
                src_path = os.path.join(self.extract_folder_path, item)
                dest_path = os.path.join("./", item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dest_path)
            print("更新完成")
        except Exception as e:
            print(f"应用更新失败: {e}")

    def clean_up(self):
        print("清理临时文件...")
        try:
            os.remove(self.download_file_path)
            print(f"清理完成: {self.download_file_path}")
            shutil.rmtree(self.extract_folder_path)
            print(f"清理完成: {self.extract_folder_path}")
        except Exception as e:
            print(f"清理失败: {e}")

    def run(self):
        if self.download_update():
            print("下载完成")
            # self.extract_update()
            # self.apply_update()
            # self.clean_up()
        else:
            print("无需更新或更新未成功")


if __name__ == "__main__":
    updater = Updater()
    updater.run()
