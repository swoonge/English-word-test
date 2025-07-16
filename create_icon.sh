#!/bin/bash

# 간단한 텍스트 아이콘 생성 스크립트
# macOS의 sips 명령어를 사용하여 아이콘 생성

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_NAME="단어시험_icon"

echo "🎨 앱 아이콘 생성 중..."

# 임시 이미지 생성 (텍스트 기반)
cat > /tmp/icon.svg << 'EOF'
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" fill="#4A90E2" rx="80"/>
  <text x="256" y="200" text-anchor="middle" fill="white" font-size="120" font-family="Arial, sans-serif" font-weight="bold">📚</text>
  <text x="256" y="320" text-anchor="middle" fill="white" font-size="48" font-family="Arial, sans-serif" font-weight="bold">단어</text>
  <text x="256" y="380" text-anchor="middle" fill="white" font-size="48" font-family="Arial, sans-serif" font-weight="bold">시험</text>
</svg>
EOF

# SVG를 PNG로 변환 (macOS에 기본 설치된 도구 사용)
if command -v rsvg-convert &> /dev/null; then
    rsvg-convert -w 512 -h 512 /tmp/icon.svg -o "$SCRIPT_DIR/icon.png"
    echo "✅ 아이콘 생성 완료: icon.png"
else
    echo "⚠️  rsvg-convert가 설치되어 있지 않습니다."
    echo "💡 Homebrew로 설치: brew install librsvg"
    echo "📝 수동으로 아이콘을 만들거나 기본 아이콘을 사용하세요."
fi

# 임시 파일 정리
rm -f /tmp/icon.svg

echo "🎯 아이콘 파일이 준비되었습니다!"
