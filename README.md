# AfuTrendRadar

阿福热点选题雷达。它不是单纯把微博热搜推到钉钉，而是把热搜转成运营判断：

- 这条热点值不值得跟
- 适合小红书、微博还是只做钉钉内参
- 具体选题切口是什么
- 阿福能不能自然承接
- 应该立即跟进还是今日观察

## 运行逻辑

1. 抓取微博实时热搜，内置多个来源兜底。
2. 按旧版健康播报验证过的“健康全场景”标准做规则预筛。
3. 用 DeepSeek 生成运营判断。
4. 将结构化选题建议推送到钉钉。
5. 把已推送话题写入 `data/sent_topics.json`，避免重复打扰。

## 监测范围

本仓库只做阿福健康选题，不做理财/财经/投资播报。健康监测范围同步自旧版微博健康播报，覆盖：

- 疾病、症状、治疗、药物、疫苗、医院、ICU、住院、手术、抢救、诊断、感染、中毒、过敏、流行病、食品安全、公共卫生
- 饮食健康、营养、体重管理、减肥、增重、暴饮暴食、饮食误区、医嘱误解、食物中毒
- 心理情绪、生活方式、运动伤害、睡眠、熬夜、保健品、养生、美容整形、衰老、死亡
- 母婴、怀孕、生育、早产、育儿健康、母乳、月经、更年期
- 环境健康、自然灾害与意外伤害
- 医保改革、异地就医、药品集采、医疗反腐、医患关系、医保基金监管
- 健康类科学辟谣、医学科普、人畜共患病、咬伤、狂犬病

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
