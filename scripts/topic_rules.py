import re


CHANNEL_RULES = [
    (
        "阿福强承接",
        r"体检|报告|指标|病例|处方|药盒|用药|吃药|药|医院|医生|挂号|就医|看病|症状|胸闷|胃痛|腰酸|头晕|眼花|发烧|咳|疼|痛|爸妈|父母|老人|长辈|医保",
    ),
    (
        "健康风险",
        r"病|癌|感染|病毒|心梗|猝死|抢救|住院|ICU|中毒|过敏|死亡|受伤|减肥针|疫苗|症状|急救|公共卫生|传染",
    ),
    (
        "生活方式",
        r"睡|失眠|熬夜|运动|减肥|体重|空调|饮料|水果|糖|咖啡|酒|头发|掉发|皮肤|护肤|戒烟|养生|低精力|皮质醇|抗阻",
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
    if "阿福强承接" in labels:
        score += 30
    if any(label in labels for label in ["健康风险", "生活方式", "女性/家庭", "情绪心理"]):
        score += 25
    if "财经理财" in labels:
        score += 15
    if "娱乐/IP" in labels and any(label in labels for label in ["健康风险", "生活方式", "情绪心理"]):
        score += 10
    if re.search(r"第一批|为什么|怎么|警惕|建议|别|不要|到底|翻案|暴跌|曝光", title):
        score += 10
    return min(score, 100)


def afu_fit_level(title):
    labels = classify_topic(title)
    if "阿福强承接" in labels:
        return "强"
    if any(label in labels for label in ["健康风险", "生活方式", "女性/家庭", "情绪心理"]):
        return "中"
    if "娱乐/IP" in labels and any(label in labels for label in ["健康风险", "生活方式", "情绪心理"]):
        return "中"
    return "弱"


def default_afu_scene(title):
    if re.search(r"体检|报告|指标|病例|处方|药盒", title):
        return "拍报告/上传报告，让阿福先解释异常指标和下一步就医准备。"
    if re.search(r"药|用药|吃药|处方", title):
        return "让阿福帮用户看懂用药时间、注意事项和需要咨询医生的问题。"
    if re.search(r"爸妈|父母|老人|长辈|医保|挂号|医院|看病|就医", title):
        return "帮家人整理症状、挂号科室和问诊问题，降低就医门槛。"
    if re.search(r"症状|疼|痛|胸闷|胃痛|腰酸|头晕|眼花|发烧|咳", title):
        return "先做症状信息整理和风险提醒，必要时建议及时线下就医。"
    if re.search(r"睡|失眠|熬夜|运动|减肥|饮食|水果|空调|头发|掉发", title):
        return "把生活困扰转成健康管理问题，让阿福给出可执行的小目标和提醒。"
    return "只有能自然切到健康问题时才露出阿福，不建议硬接。"
