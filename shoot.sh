#!/bin/zsh
# shoot.sh — AI News 全流程自动化
# 流程：npm run dev → Safari File>Save As PNG → npm run trim → 关闭服务器

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
URL="http://localhost:5173"

# ── 1. 启动开发服务器 ──────────────────────────────────────────────────────────
print "\n[1/4] 启动开发服务器..."
npm --prefix "$PROJECT_DIR" run dev &
DEV_PID=$!
trap 'print "\n🔴 关闭开发服务器"; kill $DEV_PID 2>/dev/null; wait $DEV_PID 2>/dev/null' EXIT

# ── 2. 等待服务器就绪 ──────────────────────────────────────────────────────────
print "[2/4] 等待服务器就绪..."
for i in {1..30}; do
    if curl -sf "$URL" > /dev/null 2>&1; then
        print "  ✓ 服务器就绪"
        break
    fi
    if [[ $i -eq 30 ]]; then
        print "  ✗ 超时，端口 5173 未响应"
        exit 1
    fi
    sleep 1
done

# ── 3. Safari 打开并通过 File > Save As 保存为 PNG ────────────────────────────
print "[3/4] Safari 保存页面..."

osascript << 'ASEOF'

-- 1. 打开 Safari 并导航到页面
tell application "Safari"
    activate
    if (count of windows) is 0 then
        make new document
    end if
    set URL of current tab of front window to "http://localhost:5173"
end tell

delay 4.5  -- 等待 Vue 渲染完成

-- 2. 用 Cmd+S 触发 Save As 对话框
tell application "System Events"
    tell process "Safari"
        keystroke "s" using {command down}
    end tell
end tell

-- 3. 等待 Save 对话框出现（最多 8 秒）
set dlgFound to false
repeat 16 times
    try
        tell application "System Events"
            tell process "Safari"
                if (count of windows) > 0 then
                    if (count of sheets of window 1) > 0 then
                        set dlgFound to true
                        exit repeat
                    end if
                end if
            end tell
        end tell
    end try
    delay 0.5
end repeat

if not dlgFound then
    error "Save As 对话框未出现，请检查 Safari 是否已获得辅助功能权限"
end if

-- 4. 操作对话框
tell application "System Events"
    tell process "Safari"
        set dlg to sheet 1 of window 1

        -- 跳转到桌面
        keystroke "d" using {command down, shift down}
        delay 0.4

        -- 遍历所有下拉菜单，尝试选择 PNG 格式
        repeat with aPopup in (every pop up button of dlg)
            click aPopup
            delay 0.4
            tell menu 1 of aPopup
                if exists menu item "PNG" then
                    click menu item "PNG"
                    delay 0.3
                else
                    key code 53  -- Escape，关闭弹出菜单
                    delay 0.2
                end if
            end tell
        end repeat

        -- 点击 Save / 存储
        repeat with b in (every button of dlg)
            if name of b is "Save" or name of b is "存储" then
                click b
                exit repeat
            end if
        end repeat
        delay 1.0

        -- 处理"文件已存在"确认框
        if (count of sheets of window 1) > 0 then
            set confirmDlg to sheet 1 of window 1
            repeat with b in (every button of confirmDlg)
                if name of b is "Replace" or name of b is "替换" then
                    click b
                    exit repeat
                end if
            end repeat
        end if

    end tell
end tell

ASEOF

# 给 Safari 一点时间写入磁盘
sleep 1.5

# ── 4. 裁剪白边 ───────────────────────────────────────────────────────────────
print "[4/4] 裁剪白边..."
npm --prefix "$PROJECT_DIR" run trim

print "\n✅ 全部完成！"
