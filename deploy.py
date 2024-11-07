import os
import subprocess
import zipfile
from pathlib import Path
from shutil import copytree, copy, rmtree

from app.common.setting import VERSION


def copy_with_overwrite(src, dest):
    """
    如果文件夹已经存在则删除后复制，文件则直接覆盖。
    """
    if dest.exists():
        if dest.is_dir():
            rmtree(dest)
        else:
            dest.unlink()

    if src.is_dir():
        copytree(src, dest)
    else:
        copy(src, dest)


# 打包 dist 文件夹中的文件，排除特定文件和文件夹
def create_zip_with_exclusions(output_filename, source_dir, exclusions):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(source_dir):
            # 检查是否在排除的文件夹路径中
            if any(e in str(Path(foldername)) for e in exclusions):
                print(f"压缩排除：{foldername}")
                continue
            for filename in filenames:
                file_path = Path(foldername) / filename
                # 检查是否是排除的文件
                if any(file_path.resolve().match(excl) for excl in exclusions):
                    print(f"压缩排除：{file_path}")
                    continue
                zipf.write(file_path, file_path.relative_to(source_dir))


def update_version_in_file(filename, new_version):
    try:
        # 以写入模式打开文件，这将清空文件内容
        with open(filename, 'w') as file:
            # 写入新版本号
            file.write(new_version)

        print(f"文件 {filename} 的内容已更新为 {new_version}")

    except IOError as e:
        # IOError是FileNotFoundError和OSError的基类，用于处理文件I/O错误
        print(f"无法写入文件 {filename}：{e}")


if __name__ == "__main__":
    update_version_in_file('./AppData/version.txt', 'v1.2.0')

    # 运行 Nuitka 命令
    command = [
        "python", "-m", "nuitka", "--mingw64", "--standalone", "--onefile",
        "--show-memory", "--show-progress", "--plugin-enable=pyqt5",
        "--windows-uac-admin", "--windows-disable-console",
        "--windows-icon-from-ico=app/resource/images/logo.ico",
        "--output-dir=dist", "main.py"
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Nuitka Output:", result.stdout)
        print("Nuitka Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("An error occurred during Nuitka compilation:", e.stderr)

    # 删除指定文件夹及其子文件夹
    folders_to_delete = [
        Path("dist/main.build"),
        Path("dist/main.dist"),
        Path("dist/main.onefile-build")
    ]

    for folder in folders_to_delete:
        if folder.exists() and folder.is_dir():
            rmtree(folder)
            print(f"Deleted folder: {folder}")

    # 复制文件和文件夹
    src_dest_pairs = [
        (Path("app/resource/images"), Path("dist/app/resource/images")),
        (Path("app/resource/help.md"), Path("dist/app/resource/help.md")),
        (Path("AppData/ocr_replacements.json"), Path("dist/AppData/ocr_replacements.json"))
    ]

    for src, dest in src_dest_pairs:
        print(f"Copying `{src}` to `{dest}`")
        copy_with_overwrite(src, dest)

    # 设置打包输出文件名和排除列表
    output_filename = f"SAA_{VERSION}.zip"
    source_dir = Path("dist")
    exclusions = ["dist\\AppData\\config.json", "dist\\app\\common", "dist\\log"]

    # 打包
    create_zip_with_exclusions(output_filename, source_dir, exclusions)
    print(f"Packing completed: {output_filename}")
