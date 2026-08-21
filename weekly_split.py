#!/usr/bin/env python3
"""
weekly_split.py — 拆分 Safari 导出的 AI 周报高清 PNG

用法：
  npm run weekly:split -- "/Users/name/Desktop/CSAIA - AI 一周要闻.png"

处理流程：
  1. 自动识别并裁掉 Safari 导出的右侧空白
  2. 优先读取页面右侧的模块/新闻安全裁切标记
  3. 兼容没有标记的旧图：检测低内容密度的水平间隙
  4. 动态规划出高度均衡的分页，绝不固定每张长度
  5. 后续页补充期数页眉，并同步生成微信配文
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

from weekly_publish import caption_text, latest_weekly_json, load_week


MAX_PAGE_HEIGHT = 3800
MIN_PAGE_HEIGHT = 2200
TARGET_PAGE_HEIGHT = 3100
HEADER_HEIGHT = 140

DARK = (33, 26, 20)
GOLD = (201, 168, 106)
CREAM = (245, 232, 206)


@dataclass(frozen=True)
class Candidate:
    y: int
    priority: int  # 3=模块边界，2=新闻边界，1=图片留白


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="智能拆分 Safari 导出的 AI 周报长图")
    parser.add_argument("image", type=Path, help="Safari 导出的完整 PNG")
    parser.add_argument(
        "--weekly-json",
        type=Path,
        help="对应周报 JSON，默认使用 weekly/ 下最新一期",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="输出目录，默认在母图旁创建同名文件夹",
    )
    parser.add_argument("--max-height", type=int, default=MAX_PAGE_HEIGHT)
    parser.add_argument("--min-height", type=int, default=MIN_PAGE_HEIGHT)
    return parser.parse_args()


def detect_content_width(image: Image.Image) -> int:
    """利用顶部深色封面识别实际周报宽度，排除 Safari 右侧空白。"""
    sample_height = min(image.height, 900)
    pixels = image.load()
    active = []
    for x in range(image.width):
        dark = 0
        for y in range(0, sample_height, 8):
            red, green, blue = pixels[x, y]
            if red < 90 and green < 90 and blue < 90:
                dark += 1
        if dark >= 10:
            active.append(x)
    if not active:
        return image.width
    right = max(active) + 1
    if right < image.width * 0.35:
        return image.width
    return right


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return sum(abs(a[index] - b[index]) for index in range(3))


def grouped_centers(rows: list[int], max_gap: int = 3) -> list[int]:
    if not rows:
        return []
    groups = [[rows[0]]]
    for value in rows[1:]:
        if value - groups[-1][-1] <= max_gap:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(sum(group) / len(group)) for group in groups]


def marker_candidates(image: Image.Image) -> tuple[list[Candidate], int | None]:
    """扫描最右侧分页轨道，返回安全边界和轨道左边界。"""
    scan_width = max(16, round(image.width * 0.02))
    start_x = image.width - scan_width
    section_color = (35, 178, 109)
    story_color = (224, 167, 46)
    section_rows = []
    story_rows = []
    marker_xs = []

    pixels = image.load()
    for y in range(image.height):
        section_hit = False
        story_hit = False
        for x in range(start_x, image.width):
            pixel = pixels[x, y]
            if color_distance(pixel, section_color) < 70:
                section_hit = True
                marker_xs.append(x)
            elif color_distance(pixel, story_color) < 70:
                story_hit = True
                marker_xs.append(x)
        if section_hit:
            section_rows.append(y)
        elif story_hit:
            story_rows.append(y)

    candidates = [
        *(Candidate(y, 3) for y in grouped_centers(section_rows)),
        *(Candidate(y, 2) for y in grouped_centers(story_rows)),
    ]
    rail_left = min(marker_xs) if marker_xs else None
    return sorted(candidates, key=lambda item: item.y), rail_left


def whitespace_candidates(image: Image.Image) -> list[Candidate]:
    """旧母图没有分页轨道时，从足够宽的水平留白带中寻找备用边界。"""
    gray = image.convert("L")
    left = round(image.width * 0.04)
    right = round(image.width * 0.96)
    sample_width = right - left
    safe_rows = []

    for y in range(80, image.height - 80, 3):
        row = gray.crop((left, y, right, y + 1))
        values = list(row.get_flattened_data())
        dark_ratio = sum(value < 225 for value in values) / sample_width
        mean = ImageStat.Stat(row).mean[0]
        if dark_ratio < 0.008 and mean > 246:
            safe_rows.append(y)

    if not safe_rows:
        return []

    groups = [[safe_rows[0]]]
    for value in safe_rows[1:]:
        if value - groups[-1][-1] <= 6:
            groups[-1].append(value)
        else:
            groups.append([value])

    candidates = []
    for group in groups:
        band_height = group[-1] - group[0] + 3
        if band_height < 84:
            continue
        center = round(sum(group) / len(group))
        # 栏目之间的留白通常比卡片之间更宽。
        priority = 3 if band_height >= 118 else 2
        candidates.append(Candidate(center, priority))
    return candidates


def choose_breaks(
    height: int,
    candidates: list[Candidate],
    min_height: int,
    max_height: int,
) -> list[int]:
    """
    在安全边界上做动态规划：
    - 页高必须落在允许区间
    - 优先模块边界
    - 各页高度尽量接近目标值
    """
    points = [Candidate(0, 3)]
    points.extend(
        candidate
        for candidate in candidates
        if min_height * 0.65 < candidate.y < height - min_height * 0.65
    )
    points.append(Candidate(height, 3))
    points = sorted({point.y: point for point in points}.values(), key=lambda item: item.y)

    count = len(points)
    costs = [math.inf] * count
    previous = [-1] * count
    costs[0] = 0

    for end in range(1, count):
        for start in range(end):
            segment = points[end].y - points[start].y
            is_last = end == count - 1
            lower = min_height * (0.72 if is_last else 1)
            if segment < lower or segment > max_height:
                continue
            balance = ((segment - TARGET_PAGE_HEIGHT) / TARGET_PAGE_HEIGHT) ** 2 * 100
            boundary_bonus = (3 - points[end].priority) * 18 if not is_last else 0
            candidate_cost = costs[start] + balance + boundary_bonus
            if candidate_cost < costs[end]:
                costs[end] = candidate_cost
                previous[end] = start

    if previous[-1] == -1:
        # 极端情况下放宽范围，再从目标位置附近选择最近安全点。
        cuts = [0]
        cursor = 0
        while height - cursor > max_height:
            options = [
                point
                for point in points
                if cursor + min_height * 0.7 <= point.y <= cursor + max_height
            ]
            if not options:
                cuts.append(min(height, cursor + max_height))
            else:
                preferred = max(options, key=lambda point: (point.priority, point.y))
                cuts.append(preferred.y)
            cursor = cuts[-1]
        cuts.append(height)
        return cuts

    cuts = []
    cursor = count - 1
    while cursor >= 0:
        cuts.append(points[cursor].y)
        cursor = previous[cursor]
    return list(reversed(cuts))


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for path in [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    ]:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size, index=1 if bold else 0)
            except Exception:
                pass
    return ImageFont.load_default()


def page_header(width: int, week_data: dict, page: int, total: int) -> Image.Image:
    scale = width / 1200
    header_height = max(110, round(HEADER_HEIGHT * scale))
    header = Image.new("RGB", (width, header_height), DARK)
    draw = ImageDraw.Draw(header)
    margin = round(42 * scale)
    draw.text(
        (margin, round(24 * scale)),
        "AI 一周要闻",
        fill=CREAM,
        font=font(max(28, round(38 * scale)), bold=True),
    )
    draw.text(
        (margin, round(78 * scale)),
        f"{week_data['week']}  ·  {week_data.get('date_range', '')}",
        fill=GOLD,
        font=font(max(16, round(20 * scale))),
    )
    page_text = f"{page:02d} / {total:02d}"
    page_font = font(max(19, round(24 * scale)), bold=True)
    box = draw.textbbox((0, 0), page_text, font=page_font)
    draw.text(
        (width - margin - (box[2] - box[0]), round(50 * scale)),
        page_text,
        fill=GOLD,
        font=page_font,
    )
    draw.line(
        (margin, header_height - 2, width - margin, header_height - 2),
        fill=GOLD,
        width=max(1, round(2 * scale)),
    )
    return header


def export_pages(
    image: Image.Image,
    cuts: list[int],
    output_dir: Path,
    week_data: dict,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    total = len(cuts) - 1
    paths = []

    for index, (top, bottom) in enumerate(zip(cuts, cuts[1:]), start=1):
        page = image.crop((0, top, image.width, bottom))
        if index > 1:
            header = page_header(image.width, week_data, index, total)
            combined = Image.new(
                "RGB",
                (image.width, header.height + page.height),
                (255, 254, 252),
            )
            combined.paste(header, (0, 0))
            combined.paste(page, (0, header.height))
            page = combined

        path = output_dir / f"CSAIA-AI周报-{week_data['week']}-{index:02d}.png"
        page.save(path, "PNG", optimize=True)
        paths.append(path)
    return paths


def main() -> None:
    args = parse_args()
    image_path = args.image.expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    week_path = (args.weekly_json or latest_weekly_json()).resolve()
    week_data = load_week(week_path)
    output_dir = (
        args.output
        or image_path.parent / f"{image_path.stem}-拆分"
    ).expanduser().resolve()

    source = Image.open(image_path).convert("RGB")
    content_width = detect_content_width(source)
    source = source.crop((0, 0, content_width, source.height))

    markers, rail_left = marker_candidates(source)
    if rail_left is not None:
        source = source.crop((0, 0, rail_left, source.height))
        candidates = markers
        mode = "页面安全标记"
    else:
        candidates = whitespace_candidates(source)
        mode = "图片留白识别（兼容旧图）"

    cuts = choose_breaks(
        source.height,
        candidates,
        args.min_height,
        args.max_height,
    )
    pages = export_pages(source, cuts, output_dir, week_data)

    caption = caption_text(week_data, len(pages))
    caption_path = output_dir / "AI周报文案.txt"
    caption_path.write_text(caption, encoding="utf-8")

    print(f"\n✓ 母图：{image_path.name}  {Image.open(image_path).size}")
    print(f"✓ 内容区：{source.width}×{source.height}")
    print(f"✓ 边界识别：{mode}，发现 {len(candidates)} 个候选位置")
    print(f"✓ 动态拆分：{len(pages)} 张")
    for page in pages:
        with Image.open(page) as exported:
            print(f"  - {page.name}  {exported.width}×{exported.height}")
    print(f"✓ 文案：{caption_path}")


if __name__ == "__main__":
    main()
