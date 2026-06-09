import json
from pathlib import Path


def load_sent_topics(path):
    file_path = Path(path)
    if not file_path.exists():
        return set()
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("topics", []))


def save_sent_topics(path, topics):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump({"topics": sorted(topics)}, f, ensure_ascii=False, indent=2)

