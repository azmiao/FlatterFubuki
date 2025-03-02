# FlatterFubuki
一起来谄媚布武机吧！

# 台服PCR活动本小游戏自动对战脚本 | 仅限台服

## 环境要求

python >=3.13.1 (低版本需要自己测试，推荐使用[Miniconda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)虚拟化一个版本出来)

安装依赖`requirements.txt`

## 需要的东西

1. 用户配置文件

用模拟器登录游戏或者带ROOT的手机，取出根目录下的`data/data/tw.sonet.princessconnect/shared_prefs/tw.sonet.princessconnect.v2.playerprefs.xml`

并将其丢到本项目的目录下

2. 检查`headers.json`

确认其中的`"APP-VER": "4.9.0"`游戏版本是否是最新

3. 如果需要，请在`proxy.json`中配置代理
