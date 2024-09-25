import os
import time
from pathlib import Path
from shutil import copy, copytree
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

# copy site-packages to dist folder
dist_folder = Path("dist/main/main.dist")
site_packages = Path(get_python_lib())

copied_libs = []

for src in copied_libs:
    src = site_packages / src
    dist = dist_folder / src.name

    print(f"Coping site-packages `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass

# copy standard library
copied_files = ["ctypes", "hashlib.py", "hmac.py", "random.py", "secrets.py", "uuid.py"]
for file in copied_files:
    src = site_packages.parent / file
    dist = dist_folder / src.name

    print(f"Coping stand library `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass

# 手动指定复制文件
scipy_source = Path(r"D:\Learning\compilingEnvironment\miniconda\envs\autoplay\Lib\site-packages\scipy.libs\.load-order-scipy-1.10.1")
scipy_dest_dir = Path(r"D:\Learning\Project\auto_chenbai\dist\main\main.dist\scipy.libs")

# 确保目标文件夹存在
os.makedirs(scipy_dest_dir, exist_ok=True)

# 复制文件
print(f"Copying `{scipy_source}` to `{scipy_dest_dir}`")

try:
    copy(scipy_source, scipy_dest_dir)
except Exception as e:
    print(f"Error copying file: {e}")

print(f"打包用时：{time.time()-start_time}")
