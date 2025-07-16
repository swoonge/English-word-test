#!/bin/bash

# Automator 앱 생성 도우미 스크립트
# 이 스크립트는 Automator 앱을 만드는 과정을 안내합니다.

echo "🤖 Automator로 '단어시험' 앱 만들기"
echo "================================================"
echo ""
echo "📋 단계별 가이드:"
echo ""
echo "1️⃣  Spotlight 열기 (⌘+Space) → 'Automator' 검색 → 실행"
echo ""
echo "2️⃣  '새로운 도큐먼트 만들기'에서 '애플리케이션' 선택"
echo ""
echo "3️⃣  왼쪽에서 '유틸리티' → '셸 스크립트 실행'을 오른쪽으로 드래그"
echo ""
echo "4️⃣  셸 스크립트 내용을 다음으로 교체:"
echo "================================================"
echo "#!/bin/bash"
echo "cd \"/Users/swoonge/Documents/English_study\""
echo "python3 main.py"
echo "================================================"
echo ""
echo "5️⃣  파일 → 저장"
echo "    - 이름: 단어시험"
echo "    - 위치: 응용 프로그램 (Applications)"
echo ""
echo "6️⃣  완료! 이제 Spotlight에서 '단어시험' 검색 가능!"
echo ""
echo "💡 이 방법이 가장 안전하고 확실합니다!"
echo ""

# 자동으로 Automator 실행
read -p "지금 Automator를 실행하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Automator 실행 중..."
    open -a Automator
    echo "✅ Automator가 실행되었습니다. 위의 단계를 따라하세요!"
else
    echo "👍 나중에 직접 실행하시면 됩니다!"
fi
