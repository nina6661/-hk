#!/bin/bash

# 打开新终端窗口并运行服务器
osascript << 'EOF'
tell application "Terminal"
    activate
    do script "cd /Users/didi/dchat-workplace/hk-border-stats && python3 run.py"
end tell
EOF
