#!/bin/bash

# macOS 앱 번들 생성 스크립트 (사용자 디렉토리 버전)
# 영어 단어 시험 프로그램을 실제 .app 파일로 만듭니다.

APP_NAME="단어시험"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_APPS_DIR="$HOME/Applications"
APP_DIR="$USER_APPS_DIR/$APP_NAME.app"

echo "📱 macOS 앱 번들 생성 중..."

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

# Info.plist 생성
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
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSEnvironment</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# 실행 스크립트 생성
cat > "$APP_DIR/Contents/MacOS/단어시험" << EOF
#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:\$PATH"
cd "$SCRIPT_DIR"
python3 main.py
EOF

# 실행 권한 부여
chmod +x "$APP_DIR/Contents/MacOS/단어시험"

echo "✅ 앱 생성 완료!"
echo "📍 위치: $APP_DIR"
echo "🔍 이제 Spotlight에서 '단어시험' 또는 '영어 단어 시험'으로 검색할 수 있습니다!"

# Spotlight 인덱스 갱신 (사용자 디렉토리)
echo "🔄 Spotlight 인덱스 갱신 중..."
mdimport "$USER_APPS_DIR"

echo "🎉 설정 완료! 잠시 후 Spotlight에서 검색해보세요."
echo "💡 팁: ⌘+Space 누르고 '단어시험' 입력하세요!"
