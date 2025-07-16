# 영어 단어 시험 프로그램 v2.0 🚀

마크다운 파일에서 영어 단어를 추출하여 시험을 진행하고, GPT를 통해 자동 채점하는├── words/                  # 📚 단어 파일들
├── results/               # 📈 시험 결과들
├── logs/                  # 📋 로그 파일들
├── legacy/               # 🗃️ 레거시 파일 백업 (git 제외)
├── .env                   # 🔑 환경 변수 (git 제외)
├── config.json           # ⚙️ 설정 파일 (git 제외)
├── .env.example          # 📋 환경 변수 템플릿
├── config.json.example   # 📋 설정 파일 템플릿
└── requirements.txt      # 📦 의존성 패키지 목록
```

## 🚀 사용 방법

### 1. 프로그램 실행 (권장) ⭐
```bash
python main.py
```

### 2. 호환성 실행 (구버전 사용자용)## ✨ 주요 기능

- 📝 **마크다운 테이블 자동 파싱**: 2열/4열 형식 지원
- 🎯 **드래그 앤 드롭 지원**: 간편한 파일 선택
- 📂 **자유로운 파일 관리**: 어디서든 파일 열기/저장 가능
- 🕒 **최근 파일 기록**: 자주 사용하는 파일 빠른 접근
- 🤖 **GPT 기반 자동 채점**: 맞춤법 오류도 관대하게 처리
- 🎨 **다크/라이트 테마**: 사용자 선호에 맞는 UI
- 💾 **다양한 저장 형식**: 마크다운, 텍스트, HTML 지원
- 📊 **상세 통계**: 점수, 틀린 문제 분석
- ⚙️ **GUI 설정 관리**: 폴더 경로, API 키 등 설정
- 🔒 **보안**: 환경 변수를 통한 API 키 관리
- ⌨️ **키보드 단축키**: 빠른 작업을 위한 단축키 지원

## 📦 설치 방법

### 1. Git 클론 및 설치
```bash
# 프로젝트 클론
git clone <your-repository-url>
cd English_study

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 OPENAI_API_KEY에 실제 API 키 입력

# 설정 파일 설정
cp config.json.example config.json
# config.json 파일을 필요에 따라 수정

# 패키지 설치
pip install -r requirements.txt
```

### 2. 수동 설치 (기존 사용자)
```bash
# 1. 필요한 패키지 설치
pip install -r requirements.txt

# 2. 디렉토리 생성
mkdir words results

# 3. 환경 변수 설정
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## � 프로젝트 구조

```
English_study/
├── main.py                 # 🚀 메인 진입점 (권장)
├── run.py                  # 🔄 호환성 실행 스크립트
├── daily_word_test.py      # 📜 레거시 단일 파일 (참고용)
├── src/                    # 📦 모듈화된 소스 코드
│   ├── core/              # 🧠 핵심 비즈니스 로직
│   │   ├── models.py      # 📊 데이터 모델 (WordPair, TestResult)
│   │   └── config.py      # ⚙️ 설정 관리
│   ├── services/          # 🔧 외부 서비스 연동
│   │   └── openai_service.py # 🤖 OpenAI API 서비스
│   ├── utils/             # 🛠️ 유틸리티 함수들
│   │   ├── markdown_parser.py # 📝 마크다운 파싱
│   │   └── theme_manager.py   # 🎨 테마 관리
│   └── ui/                # 🖼️ 사용자 인터페이스
│       ├── base_window.py     # 🏗️ 기본 UI 클래스
│       ├── main_window.py     # 🏠 메인 창
│       ├── test_window.py     # 📝 시험 창
│       ├── result_window.py   # 📊 결과 창
│       └── settings_window.py # ⚙️ 설정 창
├── words/                  # 📚 단어 파일들
├── results/               # 📈 시험 결과들
├── logs/                  # 📋 로그 파일들
├── .env                   # 🔑 환경 변수 (git 제외)
├── config.json           # ⚙️ 설정 파일 (git 제외)
├── .env.example          # 📋 환경 변수 템플릿
├── config.json.example   # 📋 설정 파일 템플릿
└── requirements.txt      # 📦 의존성 패키지 목록
```

## �🚀 사용 방법

### 1. 프로그램 실행 (권장)
```bash
python main.py
```

### 2. 호환성 실행
```bash
python run.py
```

### 3. 설정
- 메뉴 → 설정 → 환경 설정에서 API 키 및 테마 설정
- 또는 프로그램 내 설정 버튼 클릭

### 3. 시험 진행
1. **파일 선택 방법:**
   - 드래그 앤 드롭: 파일을 프로그램 창에 끌어다 놓기
   - 파일 열기: "📂 파일 열기" 버튼 클릭 또는 Ctrl+O
   - 최근 파일: 메뉴 → 파일 → 최근 파일에서 선택
   
2. **시험 진행:**
   - 영어 단어를 보고 한국어 의미 입력
   - Enter 키 또는 "제출" 버튼으로 제출
   
3. **결과 확인:**
   - GPT 자동 채점 결과 및 점수 확인
   - 색상으로 구분된 정답/오답 표시
   - 📊 통계 보기로 상세 분석
   
4. **결과 저장:**
   - 💾 저장: 기본 위치에 저장
   - 📁 다른 이름으로 저장: 원하는 위치/형식 선택
   - 📋 복사: 클립보드에 마크다운 표 복사

### 🎯 키보드 단축키
- `Ctrl+O`: 파일 열기
- `Ctrl+Q`: 프로그램 종료  
- `Ctrl+,`: 설정 열기
- `Enter`: 시험 제출

## 📋 마크다운 파일 형식

### 2열 형식 (기본)
```markdown
| 영어 | 한국어 |
|------|--------|
| apple | 사과 |
| book | 책 |
| computer | 컴퓨터 |
```

### 4열 형식 (고밀도)
```markdown
| 영어1 | 한국어1 | 영어2 | 한국어2 |
|-------|--------|-------|--------|
| apple | 사과 | book | 책 |
| cat | 고양이 | dog | 개 |
```

## 🛠️ 고급 기능

### 설정 파일 (config.json)
```json
{
  "ui": {
    "theme": "dark",
    "font_family": "Arial",
    "font_size": 12,
    "window_geometry": {
      "main": "500x350",
      "test": "600x800",
      "result": "900x700"
    }
  },
  "openai": {
    "model": "gpt-4o",
    "temperature": 0.1,
    "max_tokens": 2000
  },
  "paths": {
    "results_folder": "results",
    "words_folder": "words"
  }
}
```

### 로그 파일
- 프로그램 실행 로그는 `word_test.log`에 저장됩니다.

## 🔧 문제 해결

### 파일 관련 문제

1. **"파일을 찾을 수 없습니다" 오류**
   - 파일 경로에 한글이나 특수문자가 있는지 확인
   - 파일이 실제로 존재하는지 확인
   - 최근 파일 목록에서 제거: 메뉴 → 파일 → 최근 파일 → 목록 지우기

2. **드래그 앤 드롭이 작동하지 않음**
   - tkinterdnd2 모듈 재설치: `pip install --upgrade tkinterdnd2`
   - 관리자 권한으로 실행 시도

3. **마크다운 파싱 실패**
   - 테이블 형식이 올바른지 확인 (도움말 → 마크다운 형식 가이드 참조)
   - 파일 인코딩이 UTF-8인지 확인

### 저장 관련 문제

1. **저장 위치를 찾을 수 없음**
   - 설정 → 환경 설정에서 폴더 경로 재설정
   - "다른 이름으로 저장"으로 직접 위치 선택

2. **권한 오류로 저장 실패**
   - 다른 폴더 선택 (데스크톱, 문서 폴더 등)
   - 폴더 쓰기 권한 확인

### 일반적인 문제들

1. **tkinterdnd2 설치 오류**
   ```bash
   pip install tkinterdnd2
   ```

2. **OpenAI API 키 오류**
   - 설정 → 환경 설정에서 API 키 설정 및 테스트
   - API 키가 유효하고 잔액이 있는지 확인

3. **pyperclip 오류 (복사 기능)**
   ```bash
   pip install pyperclip
   ```

### 로그 확인
```bash
tail -f word_test.log
```

## 📁 프로젝트 구조

```
English_study/
├── daily_word_test.py    # 메인 프로그램
├── run.py               # 실행 스크립트
├── setup.py             # 설치 스크립트
├── requirements.txt     # 의존성 목록
├── config.json          # 설정 파일 (자동 생성)
├── .env                 # 환경 변수 (수동 생성)
├── word_test.log        # 로그 파일
├── words/               # 단어 파일 디렉토리
│   └── sample.md        # 샘플 단어 파일
└── results/             # 결과 파일 디렉토리
    └── *.md             # 시험 결과 파일들
```

## 🔧 Git 사용법

### 초기 설정 (이미 완료됨)
```bash
# Git 저장소 초기화
git init

# 기본 브랜치를 main으로 설정
git branch -M main

# 첫 번째 커밋
git add .
git commit -m "프로젝트 초기 커밋: 영어 단어 시험 프로그램 v2.0"
```

### 일반적인 Git 워크플로우
```bash
# 변경사항 확인
git status

# 파일 추가
git add .

# 커밋
git commit -m "기능 추가: 새로운 기능 설명"

# 원격 저장소에 푸시 (설정 후)
git push origin main
```

### 원격 저장소 연결
```bash
# GitHub/GitLab 등에서 저장소 생성 후
git remote add origin <your-repository-url>
git push -u origin main
```

### 브랜치 작업
```bash
# 새 브랜치 생성 및 이동
git checkout -b feature/new-feature

# 브랜치 푸시
git push -u origin feature/new-feature

# 메인 브랜치로 돌아가기
git checkout main

# 브랜치 병합
git merge feature/new-feature
```

## 🎯 개발자 정보

- **버전**: 2.0
- **개발**: AI Assistant
- **라이선스**: MIT
- **언어**: Python 3.7+

## 🔄 업데이트 내역

### v2.0 (현재)
- 🆕 클래스 기반 아키텍처로 완전 리팩토링
- 🆕 GUI 기반 설정 관리 (폴더 경로, API 키 등)
- 🆕 테마 시스템 (다크/라이트)
- 🆕 **자유로운 파일 관리**: 패키지 독립적 파일 열기/저장
- 🆕 **최근 파일 기록**: 자주 사용하는 파일 빠른 접근 (최대 10개)
- 🆕 **다양한 저장 형식**: 마크다운(.md), 텍스트(.txt), HTML(.html)
- 🆕 **"다른 이름으로 저장"**: 원하는 위치에 저장 가능
- 🆕 **상세 통계**: 점수, 틀린 문제 목록, 정답률 분석
- 🆕 **키보드 단축키**: Ctrl+O, Ctrl+Q, Ctrl+, 등
- 🆕 **폴더 빠른 열기**: 단어/결과 폴더를 탐색기에서 바로 열기
- 🆕 로깅 시스템
- 🆕 타입 힌트 추가
- 🆕 에러 핸들링 강화
- 🆕 메뉴바 추가 (파일, 설정, 도움말)
- 🆕 마크다운 형식 가이드 내장
- 🆕 Git 버전 관리 지원

### v1.0
- ✅ 기본 단어 시험 기능
- ✅ GPT 채점
- ✅ 드래그 앤 드롭 지원

## 📞 지원

문제가 발생하거나 개선 사항이 있으시면 이슈를 등록해주세요.

---

**Happy Learning! 📚✨**
