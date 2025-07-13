# 项目结构

```bash
SnowbreakAutoAssistant/
├── 📁 AppData/                   # 一些需要存下来的数据目录
│   ├── 📄 activity_date.json     # 展示在“提醒”上的活动起止时间
│   ├── 📄 config.json            # 用户配置
│   ├── 📄 ocr_replacements.json  # ocr识别结果替换字典
│   ├── 📄 scale_cache.json       # 加速特征匹配的缩放比例
│   └── 📄 version.txt            # 版本信息
│
├── 📁 app/                    # 核心逻辑目录
│   ├── 📁 common/               # 常用工具目录
│   │   ├── 📄 config.py      # 文件操作工具
│   │   ├── 📄 icon.py     # 忘记了，好像没啥用
│   │   ├── 📄 image_utils.py     # 图像相关的工具
│   │   ├── 📄 logger.py     # 图像相关的工具
│   │   ├── 📄 matcher.py     # 实现模板匹配
│   │   ├── 📄 resource.py     # 转换成二进制的资源，实际也不是很需要
│   │   ├── 📄 setting.py     # 一些全局设置，也不是很重要
│   │   ├── 📄 signal_bus.py     # 信号中转站，实现全局通信
│   │   ├── 📄 singleton.py     # 实现单例
│   │   ├── 📄 style_sheet.py     # 样式
│   │   ├── 📄 updater.py     # 更新器，没用上
│   │   └── 📄 utils.py     # 普通常用工具
│   │
│   ├── 📁 modules/               # 【加新功能在这加】各个功能模块
│   │   ├── 📁 alien_guardian/      # 异星守护
│   │   ├── 📁 automation/      # 【核心】底层自动模拟模块
│   │   ├── 📁 base_task/      # 任务基类
│   │   ├── 📁 chasm/      # 精神拟境
│   │   ├── 📁 collect_supplies/      # 收集物资
│   │   ├── 📁 drink/      # 猜心对局
│   │   ├── 📁 enter_game/      # 登入游戏
│   │   ├── 📁 fishing/      # 钓鱼
│   │   ├── 📁 get_reward/      # 收获物资
│   │   ├── 📁 jigsaw/      # 宿舍拼图
│   │   ├── 📁 massaging/      # 按摩
│   │   ├── 📁 maze/      # 验证战场迷宫
│   │   ├── 📁 ocr/      # ocr模块
│   │   ├── 📁 person/      # 角色碎片
│   │   ├── 📁 routine_action/      # 周常行动
│   │   ├── 📁 shopping/      # 商店购买
│   │   ├── 📁 trigger/      # 触发器模块
│   │   ├── 📁 use_power/      # 使用体力
│   │   └── 📁 water_bomb/      # 心动水弹
│   │
│   ├── 📁 repackage/                 # 部分fluent widgets重写
│   │   ├── 📄 custom_message_box.py      # 消息弹窗
│   │   ├── 📄 link_card.py            # 链接卡片
│   │   ├── 📄 samplecardview.py            # 基础卡片
│   │   ├── 📄 text_edit_card.py            # 文本编辑卡
│   │   └── 📄 tree.py       # 商店的树状勾选
│   │
│   ├── 📁 resource/                   # 相关资源
│   │   ├── 📁 binary/          # 已废弃的解压工具
│   │   ├── 📁 easyocr/   # easyocr相关模型
│   │   ├── 📁 i18n/   # 没用上
│   │   ├── 📁 images/   # 图像资源，各种截图
│   │   ├── 📁 qss/   # 不同主题对应的样式
│   │   ├── 📄 help.md       # 内嵌的帮助文档（很久没更新了）
│   │   └── 📄 resource.qrc       # 指明资源路径
│
├── 📁 docs/                    # 项目文档
│   ├── 📄 developer_guide.md   # 开发者文档（当前文件）
│   ├── 📄 api_reference.md     # API接口文档
│   └── 📁 diagrams/            # 架构图/流程图
│
├── 📁 data/                    # 数据存储
│   ├── 📁 cache/               # 运行时缓存
│   └── 📁 templates/           # 模板文件
│
├── 📁 logs/                    # 日志目录
│   ├── 📄 app_<日期>.log       # 应用日志
│   └── 📄 error_<日期>.log     # 错误日志
│
├── 📄 main.py                  # 应用启动入口
├── 📄 requirements.txt         # Python依赖清单
├── 📄 .gitignore               # Git忽略规则
├── 📄 LICENSE                  # 开源许可证
└── 📄 README.md                # 项目概述文档
```