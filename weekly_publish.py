#!/usr/bin/env python3
"""
weekly_publish.py — AI 周报微信图片与配文一键导出

用法：
  python3 weekly_publish.py
  python3 weekly_publish.py weekly/2026-W30.json
  python3 weekly_publish.py --input /path/to/full-page.png

默认流程：
  1. 读取最新一期 weekly/YYYY-Www.json
  2. 启动本地预览并用 Safari 截取周报专用页面
  3. 按新闻卡片边界拆成适合微信群阅读的多张长图
  4. 在 exports/YYYY-Www/ 下同步生成微信配文

如果已经有完整页面截图，可用 --input 跳过浏览器截图。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


PROJECT_DIR = Path(__file__).resolve().parent
WEEKLY_DIR = PROJECT_DIR / "weekly"
EXPORTS_DIR = PROJECT_DIR / "exports"
URL_ROOT = "http://localhost:5173"

CAPTURE_WIDTH_CSS = 600
TARGET_WIDTH = 1036
MAX_PAGE_HEIGHT = 3536
CONTINUATION_HEADER = 132
MIN_SLICE_HEIGHT = 1500

PAGE_BG = (255, 254, 252)
DARK = (33, 26, 20)
GOLD = (201, 168, 106)
CREAM = (245, 232, 206)


def latest_weekly_json() -> Path:
    files = sorted(WEEKLY_DIR.glob("????-W??.json"))
    if not files:
        raise FileNotFoundError("weekly/ 目录下没有周报 JSON")
    return files[-1]


def load_week(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not data.get("week") or not isinstance(data.get("stories"), list):
        raise ValueError(f"{path} 不是有效的周报文件")
    return data


def server_is_ready() -> bool:
    try:
        urllib.request.urlopen(URL_ROOT, timeout=1.5)
        return True
    except Exception:
        return False


def wait_for_server(timeout: int = 30) -> bool:
    for _ in range(timeout * 2):
        if server_is_ready():
            return True
        time.sleep(0.5)
    return False


def run_applescript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "AppleScript 执行失败")
    return result.stdout.strip()


def open_capture_page(week: str) -> None:
    url = f"{URL_ROOT}/weekly/{week}?capture=wechat"
    run_applescript(f'''
tell application "Safari"
    activate
    if (count of windows) is 0 then make new document
    set URL of current tab of front window to "{url}"
    set bounds of front window to {{0, 0, {CAPTURE_WIDTH_CSS}, 900}}
end tell
''')
    time.sleep(4)


def safari_js(script: str) -> str:
    escaped = script.replace("\\", "\\\\").replace('"', '\\"')
    return run_applescript(f'''
tell application "Safari"
    do JavaScript "{escaped}" in current tab of front window
end tell
''')


def page_layout() -> dict:
    script = """
JSON.stringify({
  height: document.documentElement.scrollHeight,
  width: document.documentElement.scrollWidth,
  boundaries: Array.from(document.querySelectorAll(
    '.weekly-story, .weekly-paper, .weekly-section > h2, .trend-section, .weekly-footer'
  )).map(el => Math.round(el.getBoundingClientRect().top + window.scrollY))
})
""".strip()
    return json.loads(safari_js(script))


def safari_toolbar_height() -> int:
    raw = run_applescript('''
tell application "Safari"
    tell front window to set windowHeight to (item 4 of bounds) - (item 2 of bounds)
    set innerHeightValue to do JavaScript "window.innerHeight" in current tab of front window
    return windowHeight - innerHeightValue
end tell
''')
    try:
        return max(0, int(float(raw)))
    except ValueError:
        return 88


def resize_safari(page_height: int, toolbar_height: int) -> None:
    total = page_height + toolbar_height + 8
    run_applescript(f'''
tell application "Safari"
    set bounds of front window to {{0, 0, {CAPTURE_WIDTH_CSS}, {total}}}
    activate
end tell
''')
    time.sleep(1.2)


def safari_window_id() -> int | None:
    try:
        import Quartz
    except ImportError:
        return None

    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly
        | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID,
    )
    candidates = [
        window
        for window in windows
        if window.get("kCGWindowOwnerName") == "Safari"
        and window.get("kCGWindowLayer") == 0
        and window.get("kCGWindowBounds", {}).get("Width", 0) >= 500
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda item: item.get("kCGWindowBounds", {}).get("Height", 0),
    ).get("kCGWindowNumber")


def capture_safari(output: Path) -> None:
    window_id = safari_window_id()
    if not window_id:
        raise RuntimeError("无法取得 Safari 窗口，请确认 Safari 已打开")
    subprocess.run(
        ["screencapture", f"-l{window_id}", "-x", str(output)],
        check=True,
    )


def crop_browser_chrome(path: Path, toolbar_css: int) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = image.width / CAPTURE_WIDTH_CSS
    toolbar_pixels = max(0, round(toolbar_css * scale))
    if toolbar_pixels and image.height > toolbar_pixels:
        image = image.crop((0, toolbar_pixels, image.width, image.height))

    background = Image.new("RGB", image.size, image.getpixel((0, 0)))
    difference = ImageChops.difference(image, background)
    difference = difference.point(lambda value: 0 if value < 12 else 255)
    box = difference.getbbox()
    if box:
        image = image.crop((box[0], 0, box[2], image.height))
    return image


def resize_for_wechat(image: Image.Image) -> Image.Image:
    if image.width == TARGET_WIDTH:
        return image
    height = round(image.height * TARGET_WIDTH / image.width)
    return image.resize((TARGET_WIDTH, height), Image.Resampling.LANCZOS)


def crop_capture_sides(image: Image.Image) -> Image.Image:
    """利用顶部深色周报封面识别正文宽度，移除浏览器视口两侧留白。"""
    sample_height = min(image.height, 360)
    sample = image.crop((0, 0, image.width, sample_height))
    pixels = sample.load()
    active_x = []
    for x in range(sample.width):
        dark_count = 0
        for y in range(0, sample.height, 4):
            red, green, blue = pixels[x, y]
            if red < 100 and green < 100 and blue < 100:
                dark_count += 1
        if dark_count >= 8:
            active_x.append(x)
    if not active_x:
        return image
    left = max(0, min(active_x))
    right = min(image.width, max(active_x) + 1)
    if right - left < image.width * 0.55:
        return image
    return image.crop((left, 0, right, image.height))


def mapped_boundaries(layout: dict, image_height: int) -> list[int]:
    page_height = max(1, int(layout.get("height", image_height)))
    ratio = image_height / page_height
    values = {
        max(0, min(image_height, round(int(value) * ratio)))
        for value in layout.get("boundaries", [])
    }
    values.update({0, image_height})
    return sorted(values)


def fallback_break(image: Image.Image, wanted: int, radius: int = 180) -> int:
    """在目标位置附近寻找视觉内容最少的横线。"""
    gray = image.convert("L")
    left = int(image.width * 0.05)
    right = int(image.width * 0.95)
    start = max(1, wanted - radius)
    end = min(image.height - 1, wanted + radius)
    best_y = wanted
    best_score = math.inf
    for y in range(start, end + 1, 4):
        row = gray.crop((left, y, right, y + 1))
        pixels = list(row.getdata())
        score = sum(abs(value - pixels[0]) for value in pixels[::8])
        if score < best_score:
            best_score = score
            best_y = y
    return best_y


def choose_slices(image: Image.Image, boundaries: list[int]) -> list[tuple[int, int]]:
    raw_limit = MAX_PAGE_HEIGHT - CONTINUATION_HEADER - 20
    cuts = [0]
    cursor = 0

    while image.height - cursor > raw_limit:
        candidates = [
            value
            for value in boundaries
            if cursor + MIN_SLICE_HEIGHT <= value <= cursor + raw_limit
        ]
        if candidates:
            cut = candidates[-1]
        else:
            cut = fallback_break(image, cursor + raw_limit)
        if cut <= cursor:
            cut = min(image.height, cursor + raw_limit)
        cuts.append(cut)
        cursor = cut

    cuts.append(image.height)

    if len(cuts) > 2 and cuts[-1] - cuts[-2] < MIN_SLICE_HEIGHT:
        previous_start = cuts[-3]
        candidates = [
            value
            for value in boundaries
            if previous_start + MIN_SLICE_HEIGHT <= value <= cuts[-1] - MIN_SLICE_HEIGHT
        ]
        if candidates:
            midpoint = (previous_start + cuts[-1]) / 2
            cuts[-2] = min(candidates, key=lambda value: abs(value - midpoint))

    return list(zip(cuts, cuts[1:]))


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size, index=1 if bold else 0)
            except Exception:
                continue
    return ImageFont.load_default()


def continuation_banner(week_data: dict, page: int, total: int) -> Image.Image:
    banner = Image.new("RGB", (TARGET_WIDTH, CONTINUATION_HEADER), DARK)
    draw = ImageDraw.Draw(banner)
    draw.text((44, 27), "AI 一周要闻", fill=CREAM, font=font(36, bold=True))
    draw.text(
        (44, 79),
        f"{week_data['week']}  ·  {week_data.get('date_range', '')}",
        fill=GOLD,
        font=font(18),
    )
    marker = f"{page:02d} / {total:02d}"
    marker_box = draw.textbbox((0, 0), marker, font=font(22, bold=True))
    marker_width = marker_box[2] - marker_box[0]
    draw.text(
        (TARGET_WIDTH - marker_width - 44, 50),
        marker,
        fill=GOLD,
        font=font(22, bold=True),
    )
    draw.line((44, CONTINUATION_HEADER - 2, TARGET_WIDTH - 44, CONTINUATION_HEADER - 2), fill=GOLD, width=2)
    return banner


def export_pages(
    image: Image.Image,
    slices: list[tuple[int, int]],
    week_data: dict,
    output_dir: Path,
) -> list[Path]:
    total = len(slices)
    paths = []
    for index, (top, bottom) in enumerate(slices, start=1):
        page_image = image.crop((0, top, image.width, bottom))
        if index > 1:
            banner = continuation_banner(week_data, index, total)
            combined = Image.new(
                "RGB",
                (TARGET_WIDTH, banner.height + page_image.height),
                PAGE_BG,
            )
            combined.paste(banner, (0, 0))
            combined.paste(page_image, (0, banner.height))
            page_image = combined

        path = output_dir / f"CSAIA-AI周报-{week_data['week']}-{index:02d}.png"
        page_image.save(path, "PNG", optimize=True)
        paths.append(path)
    return paths


def caption_text(week_data: dict, page_count: int) -> str:
    headlines = [
        story.get("title", "")
        for story in week_data.get("stories", [])
        if story.get("importance") == "critical"
    ]
    headline_line = "；".join(title for title in headlines if title)
    week_number = week_data["week"].replace("-W", " 年第 ") + " 周"
    paper_count = len(week_data.get("papers", []))
    selection_line = f"本周共精选 {len(week_data.get('stories', []))} 个重要主题"
    if paper_count:
        selection_line += f"与 {paper_count} 篇值得关注的 AI 论文"
    return (
        f"⚡ AI 一周要闻｜{week_number}\n\n"
        f"{headline_line}\n\n"
        f"{selection_line}，"
        f"完整内容见 {page_count} 张长图 👆\n"
        "图中扫码关注 CSAIA，获取一手行业资讯及活动信息"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导出 AI 周报微信长图和文案")
    parser.add_argument(
        "weekly_json",
        nargs="?",
        type=Path,
        help="周报 JSON，默认使用 weekly/ 下最新一期",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="使用已有完整页面截图，跳过 Safari 截图",
    )
    parser.add_argument(
        "--layout",
        type=Path,
        help="与 --input 配套的页面布局 JSON，用于按卡片边界分页",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="输出目录，默认 exports/YYYY-Www",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    json_path = (args.weekly_json or latest_weekly_json()).resolve()
    week_data = load_week(json_path)
    output_dir = (args.output or EXPORTS_DIR / week_data["week"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📚 导出 {week_data['week']} 微信周报")
    print(f"   内容：{json_path}")
    print(f"   输出：{output_dir}")

    temp_capture = output_dir / ".weekly-full-capture.png"
    layout_path = output_dir / ".weekly-layout.json"
    dev_process = None

    try:
        if args.input:
            image = Image.open(args.input).convert("RGB")
            if args.layout:
                layout = json.loads(args.layout.read_text(encoding="utf-8"))
            else:
                layout = {
                    "height": image.height,
                    "boundaries": [],
                }
        else:
            if not server_is_ready():
                dev_process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=PROJECT_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if not wait_for_server():
                    raise RuntimeError("本地预览启动超时")

            subprocess.run(
                ["npm", "run", "build-weekly-index"],
                cwd=PROJECT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            open_capture_page(week_data["week"])
            layout = page_layout()
            layout_path.write_text(
                json.dumps(layout, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            toolbar = safari_toolbar_height()
            resize_safari(int(layout["height"]), toolbar)
            capture_safari(temp_capture)
            image = crop_browser_chrome(temp_capture, toolbar)

        image = crop_capture_sides(image)
        image = resize_for_wechat(image)
        boundaries = mapped_boundaries(layout, image.height)
        slices = choose_slices(image, boundaries)
        pages = export_pages(image, slices, week_data, output_dir)

        caption = caption_text(week_data, len(pages))
        caption_path = output_dir / "AI周报文案.txt"
        caption_path.write_text(caption, encoding="utf-8")

        print(f"\n✓ 已生成 {len(pages)} 张微信群长图：")
        for page in pages:
            with Image.open(page) as exported:
                print(f"  - {page.name}  {exported.width}×{exported.height}")
        print(f"✓ 已生成文案：{caption_path.name}")
        print("\n" + "─" * 44)
        print(caption)
        print("─" * 44)
    finally:
        if temp_capture.exists():
            temp_capture.unlink()
        if layout_path.exists():
            layout_path.unlink()
        if dev_process and dev_process.poll() is None:
            dev_process.terminate()
            try:
                dev_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                dev_process.kill()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n❌ 导出失败：{error}", file=sys.stderr)
        sys.exit(1)
