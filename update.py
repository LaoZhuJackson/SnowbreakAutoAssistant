import sys
import os
import zipfile
import shutil
import subprocess

# 从命令行参数获取 zip 文件路径
update_zip_path = sys.argv[1] if len(sys.argv) > 1 else "./temp/update.zip"
extract_folder = "./temp/extracted_files"


def extract_update():
    with zipfile.ZipFile(update_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)


def replace_old_files():
    for root, dirs, files in os.walk(extract_folder):
        for file in files:
            src_file = os.path.join(root, file)
            # 计算 src_file 相对于 extract_folder 的相对路径。这样可以保留解压文件的目录结构,替换时才可以保持目录结构替换
            dst_file = os.path.join(".", os.path.relpath(src_file, extract_folder))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.move(src_file, dst_file)


def clean_temp_folder():
    shutil.rmtree("./temp")


def main():
    extract_update()
    replace_old_files()
    clean_temp_folder()
    subprocess.Popen(["./main.exe"])


if __name__ == "__main__":
    main()
