import json
import re

import requests

import config
from topic_rules import afu_fit_level, classify_topic, default_afu_scene, rule_score


def _fallback_analysis(item):
    title = item["title"]
    labels = classify_topic(title)
    score = rule_score(title, item.get("rank", 99))
    fit_level = afu_fit_level(title)
    if fit_level in ["强", "中"]:
        platform = "小红书 / 微博"
        angle = "把热搜翻译成用户自己的身体或生活问题，给出可收藏的判断标准。"
        afu = default_afu_scene(title)
        title_suggestion = f"{title}，普通人最该先看懂什么？"
        format_suggestion = "小红书图文卡片 + 微博短评"
    elif "财经理财" in labels:
        platform = "钉钉 / 微博"
        angle = "提炼政策或市场变化对普通人的影响，避免直接给投资建议。"
        afu = "仅做信息提醒，不强行挂阿福。"
        title_suggestion = f"{title}，和普通人有什么关系？"
        format_suggestion = "钉钉内参"
    else:
        platform = "微博"
        angle = "先观察热度，只有能自然切健康或生活方式时再跟。"
        afu = "不建议硬接阿福。"
        title_suggestion = "暂不建议产出"
        format_suggestion = "观察"
    if score >= 80 and fit_level in ["强", "中"]:
        action = "立即跟进"
    elif score >= config.MIN_SCORE:
        action = "今日观察"
    else:
        action = "不建议跟进"
    return {
        "title": title,
        "rank": item.get("rank", "?"),
        "score": score,
        "category": "、".join(labels),
        "afu_fit": fit_level,
        "platform": platform,
        "title_suggestion": title_suggestion,
        "format_suggestion": format_suggestion,
        "angle": angle,
        "afu_hook": afu,
        "action": action,
        "risk_boundary": "不做诊断和疗效承诺，涉及急症/异常指标要提示及时线下就医。",
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
                "afu_fit": afu_fit_level(item["title"]),
                "default_afu_scene": default_afu_scene(item["title"]),
            }
        )

    prompt = f"""你是“蚂蚁阿福”官方账号的热点选题编辑，任务是从微博热搜中判断哪些值得运营跟进。

你必须先理解蚂蚁阿福：
- 蚂蚁阿福是蚂蚁集团旗下 AI 健康朋友，不是普通健康媒体，也不是替代医生的诊断工具。
- 核心心智：专业可信、像朋友、能陪用户管理自己和家人的健康。
- 强承接场景：体检报告/检查指标解读、症状要不要就医、用药/药盒/处方理解、爸妈/长辈健康、挂号看病准备、健康焦虑安抚、生活方式小目标。
- 内容目标：先击中用户的身体/生活困扰，再给出通俗健康解释，最后自然承接“问阿福/让阿福帮你整理下一步”。
- 边界：不替代医生诊断，不给确定治疗方案，不制造医疗恐慌，不硬蹭与健康无关的热点。

请只输出 JSON 数组，不要输出 Markdown。
每个对象字段：
- title：原热搜标题
- rank：热搜排位
- score：0-100，越高越值得立即跟进
- category：健康风险/生活方式/女性家庭/情绪心理/财经理财/娱乐IP/泛热点 等
- afu_fit：强/中/弱，判断这个热点和阿福是否能自然承接
- platform：适合 小红书/微博/钉钉内参/不建议跟进，可多选
- title_suggestion：给运营的标题建议，优先小红书语感；不适合则写“暂不建议产出”
- format_suggestion：图文卡片/短视频脚本/微博短评/钉钉内参/评论区互动 等
- angle：运营切口，必须具体，不要空泛
- afu_hook：阿福如何自然承接；不适合就写“不建议强接”
- action：立即跟进/今日观察/不建议跟进
- risk_boundary：一句话说明表达边界，尤其医疗安全边界
- reason：一句话说明判断依据

判断标准：
1. 小红书优先：生活方式、女性健康、情绪睡眠、体检报告、用药、爸妈健康、饮食安全、季节健康。
2. 微博优先：突发公共健康、明星/IP 中能自然切健康的事件、可以快速评论的健康风险。
3. 钉钉内参：值得提醒运营但未必适合马上发内容的热点。
4. “阿福强承接”的热点要优先：体检/报告/症状/用药/爸妈/就医/医保/挂号。
5. 不要为了阿福硬蹭热点。必须能回答“用户为什么点、为什么收藏、为什么会问阿福”。
6. 小红书标题要像人话，优先使用：第一批、别再、建议、发给爸妈、到底、先别慌、不是矫情 等结构。
7. 任何医疗建议都要保守，不能替代医生诊断。

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
                "afu_fit": row.get("afu_fit", afu_fit_level(title)),
                "platform": row.get("platform", "今日观察"),
                "title_suggestion": row.get("title_suggestion", ""),
                "format_suggestion": row.get("format_suggestion", ""),
                "angle": row.get("angle", ""),
                "afu_hook": row.get("afu_hook", ""),
                "action": row.get("action", "今日观察"),
                "risk_boundary": row.get("risk_boundary", ""),
                "reason": row.get("reason", ""),
                "url": source.get("url", row.get("url", "")),
            }
        )
    return normalized
