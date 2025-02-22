# PerfectBuild

## 一、项目概述

这是一个用于构建应用程序的 Python 脚本，支持使用 Nuitka 和 Pyinstaller 进行构建，并能够为 Windows 系统创建安装程序和便携式压缩包。

## 二、使用前准备

1. 需先安装 Inno Setup。
2. 确保已安装所需的依赖，如通过执行以下命令安装：
   - `subprocess.call(['pip', 'install', '-r', 'environments.txt'])`
   - `subprocess.call(['pip', 'install', '-U', 'nuitka'])`
   - `subprocess.call(['pip', 'install', '-U', 'pyinstaller'])`

## 三、文件说明

1. `build.py`: 核心脚本
   - `generate_new_id(mode=True)`: 用于生成新的应用UUID，应用更新时请不要修改UUID。
   - `PerfectBuild` 类:
      - `__init__`: 初始化构建所需的变量，包括系统信息、配置信息等。
      - `nbuild`: 使用 Nuitka 进行构建。
      - `pbuild`: 使用 Pyinstaller 进行构建。
      - `create_setup`: 创建 Windows 安装程序。
      - `update_iss`: 更新安装脚本模板。
      - `create_portable`: 创建便携式压缩包。
   - `main`:主函数,根据命令行参数决定构建方式（Nuitka 或 Pyinstaller），并执行相应的构建操作。
   - 命令行参数
      - `--n`: 使用 Nuitka 进行构建。
      - `--p`: 使用 Pyinstaller 进行构建。
      - `--g`: 生成新的应用 ID。
3. `perfect_build`: 示例主程序。
   请根据需求修改主程序。
   主程序需包含Config对象：
    ```python
    class Config:
        app_ver = "1.0.0"
        app_name = "完美构建"
        app_exec = "perfect_build"
        app_publisher = "技术有限公司"
        app_url = "https://www.example.com"
        app_icon = "icon/icon.ico"
        app_dir = app_dir()
    ```
4. `perfect_build.spec`:pyinstaller自动生成配置文件
5. `nuitka-setup-template.iss`:Inno Setup模板文件

## 四、使用方法

- `git clone https://github.com/KmBase/PerfectBuild.git`
- `cd PerfectBuild`
- 安装依赖
- `python build.py`或`python build.py --n`

## 五、注意事项

1. 应用更新时请不要修改 `app_id`。
2. 构建过程中如果出现错误，会抛出相应的异常。
