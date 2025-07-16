#!/usr/bin/osascript

# AppleScript로 단어시험 실행
# 이 방법은 권한 문제가 없습니다.

tell application "Terminal"
    activate
    do script "cd '/Users/swoonge/Documents/English_study' && python3 main.py"
end tell
