<div align="center">
    <h1>
        <img src="./asset/logo.png" width="200"/>
        <br/>
        尘白禁区自动化助手
    </h1>
    <h2>Snowbreak Auto Assistant</h2>
    <br/>

![Static Badge](https://img.shields.io/badge/platfrom-Windows-%2329F1FF)
![GitHub Release](https://img.shields.io/github/v/release/LaoZhuJackson/SnowbreakAutoAssistant?color=%2329F1FF)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/LaoZhuJackson/SnowbreakAutoAssistant/total?color=%2329F1FF)
[![Static Badge](https://img.shields.io/badge/QQ_Group-996710620-%2329F1FF)](https://qm.qq.com/q/CIvpwI3qVy)
![Discord](https://img.shields.io/discord/1301841513919152158?logo=discord&color=%2329F1FF)

简体中文 | <a href="docs/README_en.md">English</a>
</div>

## 目前已实现自动化的部分（日常操作已经全部完成）

`2.0版本后所有任务支持窗口被遮挡，鼠标点击采取了一种取巧的方式最小化干扰用户操作，部分不需要鼠标操作的任务可以实现纯后台`
`只适配16:9的屏幕，支持全屏和窗口化，其他比例不一定适配（维护成本过高）`

- 登录游戏：目前取消支持从启动器自动登录，改为从游戏账号登录成功页面开始
- 领取每日物资：邮件，好友体力，供应站体力，鱼饵，宿舍拼图
- 商店购买
- 打活动材料本
- 每日角色碎片
- 自动精神拟境
- 完成日常后领取奖励
- 自动钓鱼——`选完鱼饵后纯后台`
- 自动信源解析
- 自动周常20关
- 自动心动水弹
- 自动验证战场（新迷宫）
- 自动异星守护（无尽和闯关）
![2.png](asset%2F2.png)
![3.png](asset%2F3.png)
![4.png](asset%2F4.png)
## 使用说明
演示视频:[【基于图像识别的芬妮舞狮尘白自动化代理助手-哔哩哔哩】](https://b23.tv/W9OA85k)

目前2.0还在测试版，github就不频繁上传安装包了，需要的加群：996710620

### **以下为2.0版本后的使用说明，普通用户不懂代码的直接下载release中的安装包进行安装，不需要下载源码**

- 确保游戏窗口是16:9，全屏或者窗口化都支持，如果是窗口化把窗口`贴在左上角`，`不要露出窗口标题`，如下图所示
- 下载release中的安装包并选择位置安装，路径`最好不要有中文`
- 安装完成后`取消“运行SAA”的勾选`，去安装目录`手动启动`
- 运行`SAA.exe`程序
- 在设置中选好自己账号所在的服
- 勾选需要使用的功能并做好对应的设置
- 点击开始按钮
  ![正确窗口化放法](asset%2Fcurrect.png)
  ![错误窗口化放法](asset%2Fwrong.png)

### 如何使用gpu运行

- 目前还没支持a卡，n卡的用户可以使用gpu运行ocr，这样可以避免cpu占用过高，使用教程如下图
- 目前群友测试过1050显卡也可以调用gpu
  ![使用gpu](asset%2Fuse_gpu.png)
## 相关项目
- OCR文字识别 https://github.com/JaidedAI/EasyOCR
- 三月七星穹铁道助手 https://github.com/moesnow/March7thAssistant
- maa明日方舟助手 https://github.com/MaaAssistantArknights/MaaAssistantArknights
- 图形界面组件库 https://github.com/zhiyiYo/PyQt-Fluent-Widgets
## 赞助

- 微信

<img src="./asset/support.jpg" width="200"/>

- 爱发电

<img src="./asset/support.png" width="200"/>
