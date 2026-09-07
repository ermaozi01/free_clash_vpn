# ⏰ 免费机场订阅链接

## ⚠️ 注意

- 欢迎无产阶级革命斗士免费使用本订阅
- 链接来自网络，仅作学习使用
- 使用页面所提供的任意资源时，请务必遵守当地法律

## 🚀 每12小时更新一次

- clash订阅链接：`https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/subscribe/clash.yml`

- v2ray订阅链接：`https://raw.githubusercontent.com/ermaozi01/free_clash_vpn/main/subscribe/v2ray.txt`

无法访问上方链接时可以用下面的代理链接

- clash订阅链接：`https://cdn.jsdelivr.net/gh/ermaozi01/free_clash_vpn/subscribe/clash.yml`

- v2ray订阅链接：`https://cdn.jsdelivr.net/gh/ermaozi01/free_clash_vpn/subscribe/v2ray.txt`


## 📘 客户端使用方法

- 📱 [Android](https://www.ermao.net/skill/clashforandroid/)
- 🖥 [Windows](https://www.ermao.net/uncategorized/clash-for-windows/)

## 💸 付费订阅

[>> 便宜机场评测](https://www.ermao.net/resource/vpn/)

我搜罗的一些比较便宜的机场，觉得免费订阅不好使的朋友们可以在这里面找找。

## ⭐ 感谢支持

[![操，图挂了……](https://cdn.jsdelivr.net/gh/ermaozi01/free_clash_vpn/mail/project_info.svg)](https://ermao.net)

## 本地检查与维护

使用 Python 3.12：

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python main.py
```

采集源仍为长风分享 RSS。只有两种订阅均下载并通过格式检查后才更新文件；
请求失败或内容无效会返回非零退出码，不覆盖旧订阅。格式检查不代表节点连通或可用。

GitHub Actions 每 12 小时运行一次，使用内置 `GITHUB_TOKEN` 提交文件和读取项目公开信息，
无需额外配置 `TOKEN`。三个写入工作流共用并发组，避免同时改写分支；
原有每周清理提交历史行为保持不变。GitHub 并发组只保留一个等待中的任务，
高频手动触发可能替换尚未开始的运行。
