import sys

import config
from ai_editor import analyze_topics
from dingtalk import send_markdown
from render_message import render_report
from state import load_sent_topics, save_sent_topics
from weibo_sources import get_weibo_hotspots


def main():
    hotspots = get_weibo_hotspots()
    if not hotspots:
        print("没有获取到微博热搜，退出。")
        return 1

    sent = load_sent_topics(config.SENT_TOPICS_FILE)
    fresh = [item for item in hotspots if item["title"] not in sent]
    if not fresh:
        print("没有新增热搜。")
        return 0

    candidates = fresh[: max(config.MAX_TOPICS * 3, 20)]
    analyzed = analyze_topics(candidates)
    selected = [
        item
        for item in analyzed
        if item.get("score", 0) >= config.MIN_SCORE and item.get("action") != "不建议跟进"
    ]
    selected = sorted(selected, key=lambda item: item.get("score", 0), reverse=True)[: config.MAX_TOPICS]
    report = render_report(selected)
    print(report)

    if config.DINGTALK_WEBHOOKS or config.DINGTALK_SECRETS:
        if len(config.DINGTALK_WEBHOOKS) != len(config.DINGTALK_SECRETS):
            print("DINGTALK_WEBHOOKS 和 DINGTALK_SECRETS 数量不一致。")
            return 1
        for webhook, secret in zip(config.DINGTALK_WEBHOOKS, config.DINGTALK_SECRETS):
            send_markdown(webhook, secret, "阿福热点选题雷达", report)
    else:
        print("未配置钉钉凭证，仅打印报告。")

    sent.update(item["title"] for item in selected)
    save_sent_topics(config.SENT_TOPICS_FILE, sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())

