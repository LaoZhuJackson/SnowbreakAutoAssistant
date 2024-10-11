import os
import time
from pathlib import Path
from shutil import copy, copytree, rmtree
from distutils.sysconfig import get_python_lib

args = [
    'nuitka',
    '--standalone',
    '--onefile',
    '--windows-uac-admin',
    '--windows-disable-console',
    '--follow-import-to=app',
    '--plugin-enable=pyqt5',
    '--include-qt-plugins=sensible,styles',
    '--msvc=latest',
    '--show-memory',
    '--show-progress',
    '--windows-icon-from-ico=app/resource/images/logo.ico',
    '--include-module=app',
    '--nofollow-import-to=pywin',
    '--follow-import-to=win32com,win32gui,win32print,qfluentwidgets,app',
    '--output-dir=dist',
    'main.py',
]

start_time = time.time()

os.system(' '.join(args))


# # copy site-packages to dist folder
# dist_folder = Path("dist/main/main.dist")
# site_packages = Path(get_python_lib())
#
# copied_libs = []
#
# for src in copied_libs:
#     src = site_packages / src
#     dist = dist_folder / src.name
#
#     print(f"Coping site-packages `{src}` to `{dist}`")
#
#     try:
#         if src.is_file():
#             copy(src, dist)
#         else:
#             copytree(src, dist)
#     except:
#         pass
#
# # copy standard library
# copied_files = ["ctypes", "hashlib.py", "hmac.py", "random.py", "secrets.py", "uuid.py"]
# for file in copied_files:
#     src = site_packages.parent / file
#     dist = dist_folder / src.name
#
#     print(f"Coping stand library `{src}` to `{dist}`")
#
#     try:
#         if src.is_file():
#             copy(src, dist)
#         else:
#             copytree(src, dist)
#     except:
#         pass


# 复制文件和文件夹的函数
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


# 复制 app/resource/images 文件夹到 dist/app/resource/images
src_images = Path("app/resource/images")
dest_images = Path("dist/app/resource/images")
print(f"Copying folder `{src_images}` to `{dest_images}`")
copy_with_overwrite(src_images, dest_images)

# 复制 app/resource/help.md 文件到 dist/app/resource/help.md
src_help = Path("app/resource/help.md")
dest_help = Path("dist/app/resource/help.md")
print(f"Copying file `{src_help}` to `{dest_help}`")
copy_with_overwrite(src_help, dest_help)

# 复制 AppData/ocr_replacements.json 文件到 dist/AppData/ocr_replacements.json
src_ocr = Path("AppData/ocr_replacements.json")
dest_ocr = Path("dist/AppData/ocr_replacements.json")
print(f"Copying file `{src_ocr}` to `{dest_ocr}`")
copy_with_overwrite(src_ocr, dest_ocr)

print(f"打包用时：{time.time() - start_time}")
