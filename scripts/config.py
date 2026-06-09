import os


DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_API_URL = os.environ.get(
    "DEEPSEEK_API_URL",
    "https://api.deepseek.com/v1/chat/completions",
)
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

DINGTALK_WEBHOOKS = [
    item.strip()
    for item in os.environ.get("DINGTALK_WEBHOOKS", "").split(",")
    if item.strip()
]
DINGTALK_SECRETS = [
    item.strip()
    for item in os.environ.get("DINGTALK_SECRETS", "").split(",")
    if item.strip()
]

WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "").strip()

SENT_TOPICS_FILE = os.environ.get("SENT_TOPICS_FILE", "data/sent_topics.json")
MAX_TOPICS = int(os.environ.get("MAX_TOPICS", "8"))
MIN_SCORE = int(os.environ.get("MIN_SCORE", "60"))

