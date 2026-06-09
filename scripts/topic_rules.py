import re


CHANNEL_RULES = [
    (
        "健康风险",
        r"病|癌|感染|病毒|心梗|猝死|抢救|住院|ICU|中毒|过敏|死亡|受伤|减肥针|医保|药|疫苗|症状|体检|报告|医院|医生",
    ),
    (
        "生活方式",
        r"睡|失眠|熬夜|运动|减肥|体重|空调|饮料|水果|糖|咖啡|酒|头发|皮肤|护肤|戒烟|养生",
    ),
    (
        "女性/家庭",
        r"女性|女生|妈妈|孕|生育|月经|更年期|爸妈|父母|孩子|老人|家庭|伴侣",
    ),
    (
        "情绪心理",
        r"焦虑|抑郁|紧张|情绪|压力|讨好|心理|失控|崩溃|孤独",
    ),
    (
        "财经理财",
        r"股|基金|黄金|银行|利率|存款|房贷|养老金|社保|税|理财|投资|消费|保险|诈骗|钱|降息|汇率",
    ),
    (
        "娱乐/IP",
        r"明星|演员|演唱会|综艺|电影|电视剧|开播|官宣|生日|王嘉尔|何炅|热播|票房",
    ),
]


def classify_topic(title):
    labels = []
    for label, pattern in CHANNEL_RULES:
        if re.search(pattern, title, re.I):
            labels.append(label)
    return labels or ["泛热点"]


def rule_score(title, rank):
    labels = classify_topic(title)
    score = 30
    if rank <= 10:
        score += 20
    elif rank <= 30:
        score += 10
    if any(label in labels for label in ["健康风险", "生活方式", "女性/家庭", "情绪心理"]):
        score += 25
    if "财经理财" in labels:
        score += 15
    if "娱乐/IP" in labels and any(label in labels for label in ["健康风险", "生活方式", "情绪心理"]):
        score += 10
    if re.search(r"第一批|为什么|怎么|警惕|建议|别|不要|到底|翻案|暴跌|曝光", title):
        score += 10
    return min(score, 100)

