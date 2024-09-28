import re

from tqdm import tqdm
import urllib.request
import subprocess
import os

from app.common.signal_bus import signalBus


def download_with_progress(download_url, save_path):

    aria2_path = os.path.abspath("./app/resource/binary/aria2c.exe")

    if os.path.exists(aria2_path):
        command = [aria2_path, "--max-connection-per-server=16", f"--dir={os.path.dirname(save_path)}", f"--out={os.path.basename(save_path)}", f"{download_url}"]
        if os.path.exists(save_path):
            command.insert(2, "--continue=true")
        # process = subprocess.Popen(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # progress_pattern = re.compile(r'\[#\w+\s+\S+/\S+\((\d+)%\).*?DL:(\d+\.\d+)')
        # speed_pattern
        try:
            for line in process.stdout:
                # match = progress_pattern.search(line)
                print(line)
                # if match:
                #     # print(f"匹配内容：{match.group(1)}")
                #     progress = int(match.group(1))
                #     speed = str(match.group(2))
                #     signalBus.check_ocr_progress.emit(progress,speed)
        except Exception as e:
            print(e)
        # if process.returncode != 0:
        #     raise Exception
    else:
        # 获取文件大小
        response = urllib.request.urlopen(download_url)
        file_size = int(response.info().get('Content-Length', -1))

        # 使用 tqdm 创建进度条
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            def update_bar(block_count, block_size, total_size):
                if pbar.total != total_size:
                    pbar.total = total_size
                downloaded = block_count * block_size
                pbar.update(downloaded - pbar.n)

            urllib.request.urlretrieve(download_url, save_path, reporthook=update_bar)
