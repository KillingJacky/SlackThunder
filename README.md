## 简介
这是一个用slack聊天界面下达迅雷远程下载指令的程序。以满足个人需求为主，故简陋。

## 部署
### 准备
1. 一台能够连接迅雷服务器和slack服务器的机器，例如：NAS，VPS。能运行Python的路由也行。

2. docker环境准备。本文将介绍以docker方式部署，裸机安装方式自行研究。

3. 迅雷帐号。

4. slack帐号以及App token.

    个人用户获得token最简单的方法是生成test token， 前往此处生成https://api.slack.com/docs/oauth-test-tokens

### 部署
1. docker pull killingjacky/slackthunder

2. 准备宿主机目录和配置文件

    ```
    mkdir slackthunder
    cd slackthunder
    wget -O config.py https://raw.githubusercontent.com/KillingJacky/SlackThunder/master/config.default.py
    # edit config.py
    mkdir vcode
    ```

3. docker run --name slackthunder -v \`pwd\`/config.py:/app/config.py:ro -v \`pwd\`/vcode:/app/vcode --env SLACK_TOKEN='your-token-here' -d killingjacky/slackthunder

4. docker logs -f slackthunder 
    确认迅雷登陆成功（有时需要填写验证码），确认slack connected（有时会连不上）。

## 使用
### 命令行
进入相应的channel，默认配置为#thunder：

1. `login`

2. `logout`

3. `listdev` - list the downloader devices

4. `select {index}` - select the downloader

5. `adddir {dir}` - add a download target dir

6. `listdir` - list all the saved target dirs

7. `rmdir {dir}` - remove a preset download target dir

8. `cleardir` - clear all the saved target dirs

9. `{url}` - download into the default target dir (configured on yc.xunlei.com)

10. `{url} {index}` - download into the index selected target dir

11. `info` or `list` - list the downloading status

12. `listfini` - list the finished tasks (recent 10)

14. `rmtask {index}` - stop the index selected task and trash it

14. `ping` - test if the slack script is working

### 手机App
以iOS为例，在safari中长按链接（磁力链，普通下载链等）-> 分享 -> 选择Slack -> 选择相应的channel -> 发送。这也是我写这个小程序的最初需求出发点（迅雷远程网站无手机版，复制粘贴链接非常麻烦）。


## 协议/声明
本程序迅雷远程协议参考https://github.com/iambus/xunlei-lixian 鸣谢，并跟随MIT协议。

本程序应个人需求而生，系业余开发，因精力所限不接受新功能开发请求，但欢迎pull request/fork。