#!/usr/bin/env python3
"""
gen_caption.py — 根据当日新闻 JSON 生成小红书/朋友圈文案
用法：python3 gen_caption.py [data/YYYY-MM-DD.json]
不传参数时自动取 data/ 目录下最新的 JSON 文件
输出：~/Desktop/AI快讯文案.txt
"""

import json
import sys
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
OUT_PATH = Path.home() / "Desktop" / "AI快讯文案.txt"

FOOTER = "更多热点见图 👆\n图中扫码关注CSAIA，获取一手行业资讯及活动信息"


def latest_json() -> Path:
    files = sorted(DATA_DIR.glob("????-??-??.json"))
    if not files:
        raise FileNotFoundError(f"data/ 目录下没有找到 JSON 文件")
    return files[-1]


def dot_date(iso: str) -> str:
    """'2026-04-03' → '2026.4.3'（月日不补零）"""
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.year}.{d.month}.{d.day}"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_json()

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    date_str = dot_date(data["date"])

    criticals = [
        item["title"]
        for item in data["news"]
        if item.get("importance") == "critical"
    ]

    if not criticals:
        print("⚠  没有 critical 级别的新闻，文案未生成")
        sys.exit(1)

    headlines = "; ".join(criticals)

    caption = f"⚡ AI 闪电快讯｜{date_str}\n\n{headlines}\n\n{FOOTER}"

    OUT_PATH.write_text(caption, encoding="utf-8")
    print(f"✓ 已生成: {OUT_PATH}")
    print("─" * 40)
    print(caption)


if __name__ == "__main__":
    main()
