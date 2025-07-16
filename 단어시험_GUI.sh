#!/bin/bash

# GUI 환경에서 실행하기 위한 런처 스크립트
# Terminal.app을 통해 실행하여 로그를 볼 수 있도록 함

SCRIPT_DIR="/Users/swoonge/Documents/English_study"

# Terminal에서 실행
osascript -e "
tell application \"Terminal\"
    activate
    do script \"cd '$SCRIPT_DIR' && python3 main.py\"
end tell
"
