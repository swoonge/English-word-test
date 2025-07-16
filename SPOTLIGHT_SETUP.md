# 🚀 macOS Spotlight에서 "단어시험" 실행하기

## ⚠️ 권한 오류 해결 방법

**"권한이 없습니다" 오류가 발생한다면:**

### � 방법 1: Automator 사용 (가장 안전!)

1. **Spotlight 열기** (⌘+Space) → **"Automator"** 검색 → 실행
2. **"새로운 도큐먼트 만들기"** → **"애플리케이션"** 선택
3. 왼쪽에서 **"유틸리티"** → **"셸 스크립트 실행"**을 오른쪽으로 드래그
4. 셸 스크립트 내용을 다음으로 교체:
   ```bash
   #!/bin/bash
   cd "/Users/swoonge/Documents/English_study"
   python3 main.py
   ```
5. **파일 → 저장** → 이름: **"단어시험"** → 위치: **응용 프로그램**

### 🥈 방법 2: 기존 앱 권한 수정

```bash
# 1. 확장 속성 제거
xattr -cr "$HOME/Applications/단어시험.app"

# 2. 앱 다시 생성
./create_automator_app.sh
```

### 🥉 방법 3: 터미널에서 직접 실행

```bash
# 바로 실행
./단어시험.sh

# GUI 버전 (터미널 창 열림)
./단어시험_GUI.sh
```

---

## 📋 방법 요약

### 🤖 Automator 방법 (권장!)

```bash
# 도우미 실행
./create_automator_app.sh
```

### 🛠️ 자동 스크립트 방법

```bash
# 1. 보안 개선 버전 시도
./create_secure_app.sh

# 2. 권한 오류 시 Automator 사용
./create_automator_app.sh
```

---

## 🔧 생성된 파일들

- `create_macos_app.sh` - macOS 앱 번들 생성기
- `단어시험.sh` - 터미널 실행 스크립트  
- `단어시험_GUI.sh` - GUI 터미널 실행 스크립트
- `create_icon.sh` - 앱 아이콘 생성기 (선택사항)
- `create_app.md` - 상세 가이드

---

## 🎯 추천 사용법

**가장 좋은 방법은 `./create_macos_app.sh`를 실행하는 것입니다!**

실행 후:
1. ⌘ + Space (Spotlight 열기)
2. "단어시험" 또는 "영어 단어 시험" 검색
3. Enter로 실행! 🚀

---

## 🔍 Spotlight 검색 키워드

앱 생성 후 다음 키워드들로 검색 가능:
- `단어시험`
- `영어 단어 시험`
- `word test`
- `English`

---

## 🛠️ 문제 해결

### Spotlight에서 찾을 수 없는 경우:
```bash
# Spotlight 인덱스 재구성
sudo mdutil -E /Applications
sudo mdutil -i on /Applications
```

### 권한 문제:
```bash
# 스크립트 실행 권한 확인
chmod +x *.sh
```

### Python 경로 문제:
```bash
# Python 경로 확인
which python3
```

---

**🎉 이제 macOS에서 "단어시험"을 쉽게 실행할 수 있습니다!**
