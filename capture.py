#!/usr/bin/env python3
"""
capture.py — AI 新闻截图自动化
用法：python3 capture.py  或  npm run capture

流程：
  1. 启动 npm run dev
  2. Safari 打开 localhost:5173，等待渲染完成
  3. 获取完整页面高度，调整 Safari 窗口使整页可见
  4. screencapture 截取整个 Safari 窗口（含工具栏）
  5. 自动裁掉工具栏，保存到 ~/Desktop/CSAIA - AI 闪电快讯.png
  6. 运行 npm run trim（去除白边）
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# ─── 配置 ─────────────────────────────────────────────────────────────────────

PROJECT_DIR  = Path(__file__).parent
OUTPUT_PATH  = Path.home() / "Desktop" / "CSAIA - AI 闪电快讯.png"
TEMP_PATH    = Path.home() / "Desktop" / ".capture_temp.png"
URL          = "http://localhost:5173"
PAGE_BG      = (245, 245, 245)   # #F5F5F5 页面背景色
BG_TOLERANCE = 18                # 与背景色的允许偏差
WINDOW_WIDTH = 560               # Safari 内容区宽度（逻辑像素）

# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def wait_for_server(url: str, timeout: int = 30) -> bool:
    import urllib.request
    print("  ⏳ 等待服务器", end="", flush=True)
    for _ in range(timeout):
        try:
            urllib.request.urlopen(url, timeout=2)
            print(" ✓")
            return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(1)
    print(" ✗")
    return False


def run_applescript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript 错误: {result.stderr.strip()}")
    return result.stdout.strip()


def open_safari(url: str) -> None:
    run_applescript(f'''
tell application "Safari"
    activate
    if (count of windows) is 0 then
        make new document
    end if
    set URL of current tab of front window to "{url}"
end tell
''')
    time.sleep(3.5)   # 等待 Vue 渲染完成


def get_page_height() -> int:
    """通过 JS 获取完整页面高度（含折叠内容）"""
    result = run_applescript('''
tell application "Safari"
    do JavaScript "document.body.scrollHeight" in current tab of front window
end tell
''')
    try:
        return int(result)
    except ValueError:
        return 1800   # 无法获取时的默认值


def get_safari_bounds() -> tuple[int, int, int, int]:
    """返回 Safari 窗口 (x, y, w, h) 逻辑点坐标"""
    raw = run_applescript('''
tell application "Safari"
    tell front window
        return bounds
    end tell
end tell
''')
    x1, y1, x2, y2 = (int(v.strip()) for v in raw.split(","))
    return x1, y1, x2 - x1, y2 - y1


def get_toolbar_height() -> int:
    """通过窗口高度与 innerHeight 的差值计算工具栏高度（逻辑像素）"""
    _, _, _, win_h = get_safari_bounds()
    inner_h_str = run_applescript('''
tell application "Safari"
    do JavaScript "window.innerHeight" in current tab of front window
end tell
''')
    try:
        inner_h = int(inner_h_str)
        toolbar = win_h - inner_h
        return max(toolbar, 0)
    except ValueError:
        return 88   # 常见 Safari 工具栏高度回退值


def resize_safari_window(page_h_logical: int, toolbar_h: int) -> None:
    """将 Safari 窗口调整为能显示完整页面的高度，起点固定在屏幕顶部"""
    total_h = page_h_logical + toolbar_h + 20   # 小缓冲
    run_applescript(f'''
tell application "Safari"
    activate
    set bounds of front window to {{0, 0, {WINDOW_WIDTH}, {total_h}}}
end tell
''')
    time.sleep(0.8)   # 等待窗口重绘


def get_quartz_window_id() -> int | None:
    """用 Quartz 获取 Safari 主窗口的 CGWindowID（screencapture -l 需要）"""
    try:
        import Quartz
        windows = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly |
            Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID,
        )
        candidates = [
            w for w in windows
            if w.get("kCGWindowOwnerName") == "Safari"
            and w.get("kCGWindowLayer") == 0
            and w.get("kCGWindowBounds", {}).get("Width", 0) > 400
        ]
        if candidates:
            best = max(candidates,
                       key=lambda w: (w.get("kCGWindowBounds", {}).get("Width", 0) *
                                      w.get("kCGWindowBounds", {}).get("Height", 0)))
            return best.get("kCGWindowNumber")
    except ImportError:
        pass
    return None


def take_screenshot(out: Path) -> None:
    """截取 Safari 窗口，优先使用窗口 ID（可捕获屏幕外区域）"""
    wid = get_quartz_window_id()
    if wid:
        print(f"  使用窗口 ID {wid}（screencapture -l）")
        subprocess.run(["screencapture", f"-l{wid}", "-x", str(out)], check=True)
    else:
        # 回退：截取窗口所在屏幕区域
        print("  回退：使用窗口坐标截图")
        x, y, w, h = get_safari_bounds()
        subprocess.run(["screencapture", "-R", f"{x},{y},{w},{h}", "-x", str(out)], check=True)


def crop_toolbar(img_path: Path, out_path: Path) -> None:
    """检测并裁掉截图顶部的 Safari 工具栏"""
    from PIL import Image
    img = Image.open(str(img_path)).convert("RGB")
    w, h = img.size

    def is_page_bg(px: tuple) -> bool:
        return all(abs(px[i] - PAGE_BG[i]) <= BG_TOLERANCE for i in range(3))

    # 如果左上角已是页面背景色，无需裁切
    if is_page_bg(img.getpixel((0, 0))):
        print("  ✓ 无工具栏需裁切")
        img.save(str(out_path), "PNG")
        return

    # 从顶部逐行扫描，找到页面背景开始的行
    sample_xs = [int(w * 0.25 + i * (w * 0.5 / 9)) for i in range(10)]
    top_y = 0
    for y in range(h):
        hits = sum(1 for x in sample_xs if is_page_bg(img.getpixel((x, y))))
        if hits >= 7:
            top_y = y
            break

    if top_y > 0:
        img = img.crop((0, top_y, w, h))
        print(f"  ✓ 裁掉工具栏 {top_y}px（原图 {h}px → {h - top_y}px）")
    else:
        print("  ⚠  未检测到工具栏边界，使用原图")

    img.save(str(out_path), "PNG")

# ─── 主流程 ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n🖼  AI 新闻截图自动化\n" + "─" * 40)

    # 1. 启动开发服务器
    print("\n[1/5] 启动开发服务器")
    dev_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(PROJECT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not wait_for_server(URL):
            print("❌ 服务器启动超时（30s），请检查端口 5173 是否被占用")
            sys.exit(1)

        # 2. 打开 Safari
        print("\n[2/5] Safari 加载页面（等待 3.5s 渲染）")
        open_safari(URL)
        print("  ✓ 页面加载完成")

        # 3. 调整窗口高度以显示完整页面
        print("\n[3/5] 调整窗口以显示完整页面")
        page_h   = get_page_height()
        toolbar  = get_toolbar_height()
        print(f"  页面高度: {page_h}px  工具栏: {toolbar}px")
        resize_safari_window(page_h, toolbar)
        time.sleep(0.5)   # 等待窗口稳定后再截图

        # 4. 截图 + 裁切工具栏
        print("\n[4/5] 截图")
        take_screenshot(TEMP_PATH)
        crop_toolbar(TEMP_PATH, OUTPUT_PATH)
        if TEMP_PATH.exists():
            TEMP_PATH.unlink()
        print(f"  ✓ 已保存: {OUTPUT_PATH}")

        # 5. 运行 trim
        print("\n[5/5] 裁切白边（npm run trim）")
        result = subprocess.run(
            ["npm", "run", "trim"],
            cwd=str(PROJECT_DIR),
            capture_output=True, text=True,
        )
        for line in result.stdout.splitlines():
            print(f"  {line}")

        print("\n✅ 全部完成！\n")

    finally:
        print("🔴 关闭开发服务器")
        dev_proc.terminate()
        try:
            dev_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            dev_proc.kill()


if __name__ == "__main__":
    main()
