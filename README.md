# AfuTrendRadar

阿福热点选题雷达。它不是单纯把微博热搜推到钉钉，而是把热搜转成运营判断：

- 这条热点值不值得跟
- 适合小红书、微博还是只做钉钉内参
- 具体选题切口是什么
- 阿福能不能自然承接
- 应该立即跟进还是今日观察

## 运行逻辑

1. 抓取微博实时热搜，内置多个来源兜底。
2. 对新增热搜做规则预筛。
3. 用 DeepSeek 生成运营判断。
4. 将结构化选题建议推送到钉钉。
5. 把已推送话题写入 `data/sent_topics.json`，避免重复打扰。

## GitHub Secrets

在仓库 `Settings -> Secrets and variables -> Actions` 增加：

| Secret | 必填 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 是 | DeepSeek API Key |
| `DINGTALK_WEBHOOKS` | 是 | 钉钉机器人 webhook，多个群用英文逗号分隔 |
| `DINGTALK_SECRETS` | 是 | 钉钉机器人加签 secret，顺序要和 webhook 一一对应 |
| `WEIBO_COOKIE` | 否 | 微博登录 Cookie。公开接口不稳定时可填，提高抓取成功率 |

## cron-job.org 触发方式

这个仓库不使用 GitHub Actions `schedule`，适合继续用 cron-job.org 定时触发。

请求方式：

```text
POST
https://api.github.com/repos/313663490-beep/AfuTrendRadar/actions/workflows/radar.yml/dispatches
```

Headers：

```text
Accept: application/vnd.github+json
Authorization: Bearer 你的GitHub_PAT
X-GitHub-Api-Version: 2022-11-28
Content-Type: application/json
```

Body：

```json
{"ref":"main"}
```

GitHub PAT 建议使用 fine-grained token：

- Repository access：只选择 `AfuTrendRadar`
- Repository permissions：
  - Actions: Read and write
  - Contents: Read-only

如果要用 classic token，则需要 `repo` 和 `workflow` 权限。

## 本地测试

```bash
pip install -r requirements.txt
python scripts/radar.py
```

未配置钉钉凭证时，脚本只会在终端打印报告。

