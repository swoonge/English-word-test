#!/bin/bash

# macOS 앱 번들 생성 스크립트 (보안 문제 해결 버전)
# 영어 단어 시험 프로그램을 실제 .app 파일로 만듭니다.

APP_NAME="단어시험"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_APPS_DIR="$HOME/Applications"
APP_DIR="$USER_APPS_DIR/$APP_NAME.app"

echo "📱 macOS 앱 번들 생성 중 (보안 개선 버전)..."

# 사용자 Applications 디렉토리 생성 (없는 경우)
mkdir -p "$USER_APPS_DIR"

# 기존 앱이 있다면 삭제
if [ -d "$APP_DIR" ]; then
    echo "기존 앱 제거 중..."
    rm -rf "$APP_DIR"
fi

# 앱 번들 구조 생성
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Info.plist 생성 (개선된 버전)
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>단어시험</string>
    <key>CFBundleIdentifier</key>
    <string>com.swoonge.wordtest</string>
    <key>CFBundleName</key>
    <string>단어시험</string>
    <key>CFBundleDisplayName</key>
    <string>영어 단어 시험</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSEnvironment</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

# 실행 스크립트 생성 (개선된 버전)
cat > "$APP_DIR/Contents/MacOS/단어시험" << 'EOF'
#!/bin/bash

# 환경 변수 설정
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$PATH"

# 프로젝트 디렉토리로 이동
PROJECT_DIR="/Users/swoonge/Documents/English_study"
cd "$PROJECT_DIR" || {
    echo "프로젝트 디렉토리를 찾을 수 없습니다: $PROJECT_DIR"
    exit 1
}

# Python 실행 (여러 경로 시도)
PYTHON_PATHS=(
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3"
    "/usr/bin/python3"
    "python3"
)

for python_path in "${PYTHON_PATHS[@]}"; do
    if command -v "$python_path" >/dev/null 2>&1; then
        echo "Python 실행 중: $python_path"
        exec "$python_path" main.py
        exit 0
    fi
done

echo "Python3를 찾을 수 없습니다."
exit 1
EOF

# 실행 권한 부여
chmod +x "$APP_DIR/Contents/MacOS/단어시험"

# Gatekeeper 문제 해결을 위한 확장 속성 제거
echo "🔓 Gatekeeper 제한 해제 중..."
xattr -cr "$APP_DIR"

# 앱에 실행 권한 추가
echo "🔐 실행 권한 설정 중..."
spctl --add "$APP_DIR"
spctl --enable "$APP_DIR"

echo "✅ 앱 생성 완료!"
echo "📍 위치: $APP_DIR"

# 첫 실행을 통해 권한 설정
echo "🚀 첫 실행 테스트 중..."
open "$APP_DIR"

echo "🔍 이제 Spotlight에서 '단어시험' 또는 '영어 단어 시험'으로 검색할 수 있습니다!"

# Spotlight 인덱스 갱신
echo "🔄 Spotlight 인덱스 갱신 중..."
mdimport "$USER_APPS_DIR"

echo "🎉 설정 완료!"
echo "💡 팁: ⌘+Space 누르고 '단어시험' 입력하세요!"
EOF
