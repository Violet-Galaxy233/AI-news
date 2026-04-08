#!/usr/bin/env python3
"""
用法：python3 trim.py
裁剪桌面上 "CSAIA - AI 闪电快讯.png" 的白边，覆盖原文件。
"""

import os
from PIL import Image

PATH = os.path.expanduser("~/Desktop/CSAIA - AI 闪电快讯.png")


def trim(path):
    from PIL import ImageChops
    img = Image.open(path).convert("RGB")
    # 用左上角像素颜色作为背景色（Safari 存图的页面背景）
    bg_color = img.getpixel((0, 0))
    bg = Image.new("RGB", img.size, bg_color)
    diff = ImageChops.difference(img, bg)
    # 差值小于 15 的像素视为背景（处理抗锯齿边缘）
    diff = diff.point(lambda x: 0 if x < 15 else 255)
    bbox = diff.getbbox()
    if bbox:
        cropped = img.crop(bbox)
        cropped.save(path, "PNG")
        print(f"✓ 已裁剪: {img.size} → {cropped.size}")
        print(f"  背景色: {bg_color}，保存至: {path}")
    else:
        print("未检测到边框，图片未修改。")


trim(PATH)
