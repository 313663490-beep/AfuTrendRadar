import json
import os
import random
import re
import time
import urllib.parse

import requests


WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "").strip()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]


def _headers(referer):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": referer,
        "Cache-Control": "no-cache",
    }
    if WEIBO_COOKIE:
        headers["Cookie"] = WEIBO_COOKIE
    return headers


def _request(session, url, referer):
    last_error = None
    for attempt in range(3):
        try:
            resp = session.get(url, headers=_headers(referer), timeout=12)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            last_error = exc
            print(f"微博源请求失败，第 {attempt + 1} 次：{exc}")
            time.sleep(1 + attempt * 2)
    raise RuntimeError(last_error)


def _clean_title(raw):
    return " ".join(str(raw or "").split()).strip("# ")


def _search_url(title):
    return f"https://s.weibo.com/weibo?q={urllib.parse.quote(title)}"


def _dedupe(items):
    result = []
    seen = set()
    for item in items:
        if not item["title"] or item["title"] in seen:
            continue
        seen.add(item["title"])
        item["rank"] = len(result) + 1
        result.append(item)
    return result


def _item(title, rank, url=""):
    title = _clean_title(title)
    if not title:
        return None
    return {
        "title": title,
        "rank": rank,
        "url": url or _search_url(title),
    }


def _from_side_hot_search(session):
    resp = _request(session, "https://weibo.com/ajax/side/hotSearch", "https://weibo.com/")
    data = resp.json()
    realtime = data.get("data", {}).get("realtime", [])
    items = []
    for index, row in enumerate(realtime, start=1):
        title = row.get("word") or row.get("note") or row.get("title")
        formatted = _item(title, index, row.get("url", ""))
        if formatted:
            items.append(formatted)
    if not items:
        raise RuntimeError(f"side/hotSearch 格式异常：{data}")
    return _dedupe(items)


def _from_hot_band(session):
    resp = _request(session, "https://weibo.com/ajax/statuses/hot_band", "https://weibo.com/")
    data = resp.json()
    rows = data.get("data", {}).get("band_list", [])
    items = []
    for index, row in enumerate(rows, start=1):
        formatted = _item(row.get("word") or row.get("note"), index)
        if formatted:
            items.append(formatted)
    if not items:
        raise RuntimeError(f"hot_band 格式异常：{data}")
    return _dedupe(items)


def _extract_from_html(html):
    titles = []
    patterns = [
        r'"word":"(.*?)"',
        r'"note":"(.*?)"',
        r"word=([^\"&]+)",
        r'td-02">.*?<a[^>]*>(.*?)</a>',
    ]
    for pattern in patterns:
        for match in re.findall(pattern, html, flags=re.S):
            text = re.sub(r"<.*?>", "", match)
            try:
                text = json.loads(f'"{text}"')
            except Exception:
                text = urllib.parse.unquote(text)
            title = _clean_title(text)
            if title and title not in titles and "微博" not in title:
                titles.append(title)
    return titles


def _from_search_summary(session):
    resp = _request(session, "https://s.weibo.com/top/summary?cate=realtimehot", "https://s.weibo.com/")
    titles = _extract_from_html(resp.text)
    items = []
    for index, title in enumerate(titles, start=1):
        formatted = _item(title, index)
        if formatted:
            items.append(formatted)
    if not items:
        raise RuntimeError("搜索热榜页面未解析到热搜")
    return _dedupe(items)


def get_weibo_hotspots():
    session = requests.Session()
    sources = [
        ("weibo side hotSearch", _from_side_hot_search),
        ("weibo hot band", _from_hot_band),
        ("s.weibo.com summary", _from_search_summary),
    ]
    errors = []
    for name, loader in sources:
        try:
            items = loader(session)
            print(f"成功通过 {name} 获取 {len(items)} 条热搜")
            return items
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            print(f"热搜源不可用：{name}：{exc}")
    print("所有微博热搜源均不可用：")
    for error in errors:
        print(f"- {error}")
    return []

