# 🚀 macOS Spotlight에서 "단어시험" 실행하기

## 📋 방법 요약

### 🥇 방법 1: macOS 앱 만들기 (가장 추천!)

```bash
# 1. 앱 생성 스크립트 실행
./create_macos_app.sh

# 2. 완료! 이제 Spotlight에서 "단어시험" 검색
```

### 🥈 방법 2: Automator 사용 (GUI 방식)

1. **Automator** 실행 (Spotlight에서 "Automator" 검색)
2. **"애플리케이션"** 선택
3. **"셸 스크립트 실행"** 액션 추가
4. 다음 스크립트 입력:
   ```bash
   #!/bin/bash
   cd "/Users/swoonge/Documents/English_study"
   python3 main.py
   ```
5. **파일 → 저장** → 이름: "단어시험" → 위치: 응용 프로그램

### 🥉 방법 3: 터미널 스크립트 (간단)

```bash
# 직접 실행
./단어시험.sh

# 또는 GUI 버전
./단어시험_GUI.sh
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
