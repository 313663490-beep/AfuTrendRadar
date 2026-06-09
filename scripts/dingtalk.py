import base64
import hashlib
import hmac
import time
import urllib.parse

import requests


def send_markdown(webhook_url, secret, title, text):
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    signed_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text,
        },
    }
    resp = requests.post(signed_url, json=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("errcode") != 0:
        raise RuntimeError(f"钉钉发送失败：{result}")
    print(f"钉钉发送成功：{title}")

