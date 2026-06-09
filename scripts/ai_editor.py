import json
import re

import requests

import config
from topic_rules import classify_topic, rule_score


def _fallback_analysis(item):
    title = item["title"]
    labels = classify_topic(title)
    score = rule_score(title, item.get("rank", 99))
    if any(label in labels for label in ["健康风险", "生活方式", "女性/家庭", "情绪心理"]):
        platform = "小红书 / 微博"
        angle = "把热搜翻译成用户自己的身体或生活问题，给出可收藏的判断标准。"
        afu = "结尾引导用户把症状、体检报告或用药问题继续问阿福。"
    elif "财经理财" in labels:
        platform = "钉钉 / 微博"
        angle = "提炼政策或市场变化对普通人的影响，避免直接给投资建议。"
        afu = "仅做信息提醒，不强行挂阿福。"
    else:
        platform = "微博"
        angle = "先观察热度，只有能自然切健康或生活方式时再跟。"
        afu = "不建议硬接阿福。"
    return {
        "title": title,
        "rank": item.get("rank", "?"),
        "score": score,
        "category": "、".join(labels),
        "platform": platform,
        "angle": angle,
        "afu_hook": afu,
        "action": "可跟进" if score >= config.MIN_SCORE else "观察",
        "reason": "规则兜底判断，AI 不可用时生成。",
        "url": item.get("url", ""),
    }


def _extract_json_array(text):
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        raise ValueError("未找到 JSON 数组")
    return json.loads(match.group(0))


def analyze_topics(items):
    if not config.DEEPSEEK_API_KEY:
        print("未配置 DEEPSEEK_API_KEY，使用规则兜底分析。")
        return [_fallback_analysis(item) for item in items]

    compact_items = []
    for item in items:
        compact_items.append(
            {
                "title": item["title"],
                "rank": item.get("rank"),
                "url": item.get("url"),
                "rule_labels": classify_topic(item["title"]),
                "rule_score": rule_score(item["title"], item.get("rank", 99)),
            }
        )

    prompt = f"""你是阿福官方账号的热点选题编辑，任务是从微博热搜中判断哪些值得运营跟进。

请只输出 JSON 数组，不要输出 Markdown。
每个对象字段：
- title：原热搜标题
- rank：热搜排位
- score：0-100，越高越值得立即跟进
- category：健康风险/生活方式/女性家庭/情绪心理/财经理财/娱乐IP/泛热点 等
- platform：适合 小红书/微博/钉钉内参/不建议跟进，可多选
- angle：运营切口，必须具体，不要空泛
- afu_hook：阿福如何自然承接；不适合就写“不建议强接”
- action：立即跟进/今日观察/不建议跟进
- reason：一句话说明判断依据

判断标准：
1. 小红书优先：生活方式、女性健康、情绪睡眠、体检、用药、爸妈健康、饮食安全。
2. 微博优先：突发公共健康、明星/IP 中能自然切健康的事件。
3. 钉钉内参：值得提醒运营但未必适合马上发内容的热点。
4. 不要为了阿福硬蹭热点。必须能回答“用户为什么点、为什么收藏、为什么会问阿福”。
5. 任何医疗建议都要保守，不能替代医生诊断。

热搜列表：
{json.dumps(compact_items, ensure_ascii=False)}
"""
    payload = {
        "model": config.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是谨慎、懂小红书和微博的健康内容运营编辑。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 3500,
        "stream": False,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
    }
    try:
        resp = requests.post(config.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            print(f"AI 分析失败 {resp.status_code}: {resp.text}")
            return [_fallback_analysis(item) for item in items]
        text = resp.json()["choices"][0]["message"]["content"].strip()
        results = _extract_json_array(text)
    except Exception as exc:
        print(f"AI 分析异常：{exc}")
        return [_fallback_analysis(item) for item in items]

    by_title = {item["title"]: item for item in items}
    normalized = []
    for row in results:
        title = row.get("title", "")
        source = by_title.get(title, {})
        normalized.append(
            {
                "title": title,
                "rank": row.get("rank", source.get("rank", "?")),
                "score": int(row.get("score", 0) or 0),
                "category": row.get("category", "未分类"),
                "platform": row.get("platform", "今日观察"),
                "angle": row.get("angle", ""),
                "afu_hook": row.get("afu_hook", ""),
                "action": row.get("action", "今日观察"),
                "reason": row.get("reason", ""),
                "url": source.get("url", row.get("url", "")),
            }
        )
    return normalized

