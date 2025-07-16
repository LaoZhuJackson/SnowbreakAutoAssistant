#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   build.py
@Time    :   2024/07/05 11:19:32
@Author  :   KmBase
@Version :   1.0
@License :   (C)Copyright 2022, KmBase
@Desc    :   使用前需要先安装InnoSetup,应用更新时请不要修改app_id
"""

import glob
import platform
import subprocess
import sys
import traceback
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from perfect_build import Config
import uuid

# python .\PerfectBuild\build.py --n


iss_compiler = "D:\\software\\innosetup\\Inno Setup 6\\Compil32.exe"


# subprocess.call(['pip', 'install', '-U', 'nuitka'])
# subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
# subprocess.call(['pip', 'freeze', '>', 'equirements.txt'])


def generate_new_id(mode):
    if mode:
        print(str(uuid.uuid4()).upper())
    else:
        return "EF37701A-BF20-4C1C-8459-34041F620CFE"


class PerfectBuild:
    # 系统信息
    system = platform.system()
    arch = platform.architecture()[0][:2]
    # 配置信息
    app_ver = Config.app_ver
    app_name = Config.app_name
    app_publisher = Config.app_publisher
    app_url = Config.app_url
    app_icon = Config.app_icon
    app_exec = Config.app_exec
    app_dir = Config.app_dir

    def __init__(self, app_id, mode="--p"):
        """
        初始化变量
        """
        self.app_id = app_id
        self.mode = mode.replace("--", "")
        self.dist = f"{self.app_exec}.dist"
        if self.mode == "p":
            self.dist = f"dist//{self.app_exec}"
        self.app_dir = Path(self.app_dir)
        self.build_dir = Path.joinpath(self.app_dir, "build")
        if not self.build_dir.exists():
            self.build_dir.mkdir()
        self.release_dir = Path.joinpath(
            self.app_dir, "release", f"{self.app_ver}{self.mode}"
        )
        if not self.release_dir.exists():
            if not self.release_dir.parent.exists():
                self.release_dir.parent.mkdir()
            self.release_dir.mkdir()

    def nbuild(self):
        """
        官方文档 : https://nuitka.net/
        使用Nuitka构建example:
        nuitka_cmd = [
            "python",
            "-m",
            "nuitka",
            "--show-progress",
            "--show-memory",
            "--standalone",
            "--include-data-dir=output=output",
            "--include-data-dir=icon=icon",
            "--plugin-enable=pyside6",
            f"--output-dir={output_dir}",
            f"--include-data-files=example.db=example.db",
        ]
        """
        output_dir = Path.joinpath(self.app_dir, "build", f"{self.system}-{self.arch}")
        cmd_args = [
            "python",
            "-m",
            "nuitka",
            "--show-progress",
            "--show-memory",
            "--standalone",
            "--plugin-enable=pyqt5",
            f"--output-dir={output_dir}",
            "--windows-uac-admin",
            "--windows-console-mode=disable",
            # 添加文件
            "--include-data-file=patch/scipy.libs/.load-order-scipy-1.10.1=scipy.libs/.load-order-scipy-1.10.1",
            "--include-data-file=patch/shapely.libs/.load-order-shapely-2.0.7=shapely.libs/.load-order-shapely-2.0.7",
            "--include-data-file=AppData/ocr_replacements.json=AppData/ocr_replacements.json",
            "--include-data-file=AppData/version.txt=AppData/version.txt",
            "--include-data-dir=app/resource/images=app/resource/images",
            "--include-data-file=app/resource/help.md=app/resource/help.md",
            "--include-data-dir=app/resource/easyocr=app/resource/easyocr",
        ]
        if platform.system() == "Windows":
            cmd_args.extend((f"--windows-icon-from-ico={self.app_icon}",))
        # '--windows-console-mode=disable',
        cmd_args.append(f"{self.app_dir}/{self.app_exec}.py")
        print(cmd_args)
        process = subprocess.run(cmd_args, shell=True)
        if process.returncode != 0:
            print(traceback.format_exc())
            raise ChildProcessError("Nuitka building failed.")
        print("Nuitka Building done.")

    def pbuild(self):
        """
        官方文档 : https://pyinstaller.org/
        使用Pyinstaller构建example:
        """
        output_dir = Path.joinpath(self.app_dir, "build", f"{self.system}-{self.arch}")
        build_dir = Path.joinpath(output_dir, "build")
        dist_dir = Path.joinpath(output_dir, "dist")
        cmd_args = [
            "pyinstaller",
            "--onedir",
            "--add-data=icon:icon",
            f"--distpath={dist_dir}",
            f"--workpath={build_dir}",
            "--contents-directory=.",
        ]
        if platform.system() == "Windows":
            cmd_args.extend((f"-i{self.app_icon}",))
        # '-w',
        cmd_args.append(f"{self.app_dir}/{self.app_exec}.py")
        print(cmd_args)
        process = subprocess.run(cmd_args, shell=True)
        if process.returncode != 0:
            raise ChildProcessError("Pyinstaller building failed.")
        print("Pyinstaller Building done.")

    def create_setup(self):
        iss_work = self.update_iss()
        if Path(iss_compiler).exists:
            print("Creating Windows Installer...", end="")
            compiler_cmd = [str(iss_compiler), "/cc", str(iss_work)]
            process = subprocess.run(compiler_cmd)
            if process.returncode != 0:
                raise ChildProcessError("Creating Windows installer failed.")
            print("done")

    def update_iss(self):
        settings = {
            "AppId": self.app_id,
            "AppName": self.app_name,
            "AppVersion": self.app_ver,
            "AppMode": self.mode,
            "System": self.system,
            "Arch": self.arch,
            "AppPublisher": self.app_publisher,
            "AppURL": self.app_url,
            "AppIcon": self.app_icon,
            "AppExeName": self.app_exec + ".exe",
            "ProjectDir": str(self.app_dir),
            "BuildDir": str(self.build_dir),
            "ReleaseDir": str(self.release_dir),
            "Dist": str(self.dist),
            "ARCH_MODE": (
                "ArchitecturesInstallIn64BitMode=x64" if self.arch == "64" else ""
            ),
        }

        iss_template = f"PerfectBuild/nuitka-setup-template.iss"
        iss_work = Path.joinpath(
            self.build_dir, f"{self.app_name}-{self.arch}-{self.mode}.iss"
        )
        with open(iss_template) as template:
            iss_script = template.read()

        for key in settings:
            iss_script = iss_script.replace(f"%%{key}%%", settings.get(key))

        with open(iss_work, "w") as iss:
            iss.write(iss_script)
        return iss_work

    def create_portable(self):
        file_list = glob.glob(
            f"{self.build_dir}/{self.system}-{self.arch}/{self.dist}/**",
            recursive=True,
        )
        file_list.sort()
        portable_file = (
            self.release_dir
            / f"{self.app_exec}-{self.app_ver}{self.mode}-Portable-{self.system}-{self.arch}.zip"
        )
        print("Creating portable package...")
        with ZipFile(portable_file, "w", compression=ZIP_DEFLATED) as zf:
            for file in file_list:
                file = Path(file)
                name_in_zip = f"{self.app_exec}/{'/'.join(file.parts[6:])}"
                print(name_in_zip)
                if file.is_file():
                    zf.write(file, name_in_zip)
        print("Creating portable package done.")


def main(args):
    """
    :param args:
        --n:Nuitka building
        --p:Pyinstaller building
        --g:Generate APPID
    :return:
    """
    if len(sys.argv) < 2:
        mode = "--p"
    else:
        mode = args[1]
        if mode == "--g":
            generate_new_id(True)
            return
    app_id = generate_new_id(False)
    pb = PerfectBuild(app_id, mode)
    if mode == "--n":
        pb.nbuild()
    else:
        pb.pbuild()
    pb.create_portable()
    if pb.system == "Windows":
        pb.create_setup()


if __name__ == "__main__":
    main(sys.argv)
