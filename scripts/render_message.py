import datetime as dt


def _line(item):
    return (
        f"### {item['title']}\n"
        f"- 排位：{item.get('rank', '?')}｜评分：{item.get('score', 0)}｜动作：{item.get('action', '今日观察')}\n"
        f"- 类别：{item.get('category', '未分类')}\n"
        f"- 适合平台：{item.get('platform', '今日观察')}\n"
        f"- 选题切口：{item.get('angle', '')}\n"
        f"- 阿福承接：{item.get('afu_hook', '')}\n"
        f"- 判断依据：{item.get('reason', '')}\n"
        f"- 链接：{item.get('url', '')}\n"
    )


def render_report(items):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    if not items:
        return f"## 阿福热点选题雷达\n\n{now}\n\n本轮没有达到跟进阈值的新增热点。"
    urgent = [item for item in items if item.get("action") == "立即跟进"]
    watch = [item for item in items if item.get("action") != "立即跟进"]
    lines = [
        "## 阿福热点选题雷达",
        "",
        f"时间：{now}",
        f"本轮建议跟进：{len(items)} 条，其中立即跟进 {len(urgent)} 条。",
        "",
    ]
    if urgent:
        lines.append("## 立即跟进")
        lines.extend(_line(item) for item in urgent)
    if watch:
        lines.append("## 今日观察")
        lines.extend(_line(item) for item in watch)
    return "\n".join(lines)

