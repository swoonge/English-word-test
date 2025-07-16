# 영어 단어 시험 프로그램 v2.0 🚀

> AI 기반 영어 단어 시험 프로그램 - 마크다운 파일을 시험으로, GPT로 자동 채점

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](README.md)

## 📖 프로그램 소개

마크다운 파일에서 영어 단어를 추출하여 시험을 진행하고, OpenAI GPT를 통해 자동 채점하는 교육용 프로그램입니다. 모든 기능이 직관적인 GUI로 제공되며, 다양한 플랫폼에서 사용할 수 있도록 최적화되었습니다.

### ✨ 주요 특징

- 🎯 **직관적인 GUI**: 모든 기능을 마우스 클릭으로 조작
- 📝 **마크다운 지원**: 2열/4열 테이블 형식 자동 인식
- 🤖 **AI 자동 채점**: GPT 기반으로 맞춤법 오류도 관대하게 처리
- 🎨 **테마 지원**: 다크/라이트 테마 즉시 전환
- 💾 **다양한 저장**: 마크다운, 텍스트, HTML 형식 지원
- 📊 **상세 통계**: 점수, 오답 분석, 진행률 추적
- 🔧 **시스템 최적화**: Windows, macOS, Linux 각각 최적화
- 🛡️ **보안**: 환경 변수 기반 API 키 관리

## 📁 프로젝트 구조

```
English_study/
│
├── main.py                # 🚀 메인 실행 파일
├── requirements.txt       # 📦 Python 의존성
├── config.json           # ⚙️ 사용자 설정 (자동 생성)
├── .env                  # 🔑 환경 변수 (사용자 생성)
│
├── src/                  # 📁 소스 코드
│   ├── core/            # 🧠 핵심 로직
│   │   ├── config.py    # 설정 관리
│   │   └── models.py    # 데이터 모델
│   ├── ui/              # 🎨 사용자 인터페이스
│   │   ├── main_window.py     # 메인 창
│   │   ├── settings_window.py # 설정 창
│   │   ├── test_window.py     # 시험 창
│   │   ├── result_window.py   # 결과 창
│   │   └── base_window.py     # 공통 UI
│   ├── services/        # 🛠️ 외부 서비스
│   │   └── openai_service.py  # OpenAI API
│   └── utils/           # 🔧 유틸리티
│       ├── theme_manager.py        # 테마 관리
│       ├── markdown_parser.py      # 마크다운 파싱
│       └── system_compatibility.py # 시스템 호환성
│
├── words/               # 📚 단어 파일들
│   ├── sample.md       # 샘플 파일
│   └── *.md            # 사용자 단어 파일
├── results/            # 📈 시험 결과들
├── logs/               # 📋 실행 로그들
└── legacy/             # 🗃️ 백업 파일들 (git 제외)
```

## 🚀 빠른 시작

### 1단계: 설치
```bash
# 저장소 클론
git clone <your-repository-url>
cd English_study

# Python 의존성 설치
pip install -r requirements.txt
```

### 2단계: API 키 설정
```bash
# 환경 변수 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3단계: 실행
```bash
python main.py
```

## 💻 플랫폼별 설치

### 🐧 Ubuntu/Linux
상세한 우분투 설치 가이드는 [README_Ubuntu.md](README_Ubuntu.md)를 참조하세요.

```bash
# 시스템 의존성 설치
sudo apt install python3-tk xclip

# 자동 설치 (권장)
python3 install_ubuntu.py
```

### 🪟 Windows
```bash
# Python 3.7+ 설치 필요
pip install -r requirements.txt
python main.py
```

### 🍎 macOS
```bash
# Homebrew를 통한 Python 설치 권장
brew install python-tk
pip3 install -r requirements.txt
python3 main.py
```

## 📖 사용 방법

### 1. 프로그램 실행
```bash
python main.py
```

### 2. 첫 실행 시 설정
1. **⚙️ 설정 버튼** 클릭
2. **OpenAI API 키** 입력 및 테스트
3. **폴더 경로** 설정 (선택사항)
4. **테마** 선택 (다크/라이트)
5. **💾 저장** 클릭

### 3. 단어 파일 준비
```markdown
# words/sample.md 형식

| 영어 | 한글 |
|------|------|
| apple | 사과 |
| book | 책 |

# 또는 4열 형식
| 영어 | 발음 | 한글 | 예문 |
|------|------|------|------|
| apple | [ˈæpl] | 사과 | I eat an apple |
```

### 4. 시험 진행
1. **📂 파일 열기** 또는 **드래그 앤 드롭**으로 파일 선택
2. **🎯 시험 시작** 클릭
3. 단어 시험 완료
4. **📊 결과 확인** 및 **💾 저장**

## ⚙️ 설정 옵션

### UI 설정
- **테마**: 다크/라이트 테마 전환
- **폰트**: 시스템별 최적화된 폰트 자동 선택
- **창 크기**: 각 창별 크기 자동 저장

### 폴더 설정
- **단어 파일 폴더**: 단어 파일들이 저장된 폴더
- **결과 폴더**: 시험 결과가 저장될 폴더

### OpenAI 설정
- **API 키**: OpenAI API 키 (필수)
- **모델**: GPT-4o (기본값)
- **온도**: 0.1 (일관된 채점을 위해)

## 🎯 주요 기능

### 📝 마크다운 파싱
- **2열 테이블**: `| 영어 | 한글 |`
- **4열 테이블**: `| 영어 | 발음 | 한글 | 예문 |`
- **자동 인식**: 테이블 형식 자동 감지

### 🤖 AI 채점
- **관대한 채점**: 맞춤법 오류 허용
- **의미 기반**: 문맥상 올바른 답안 인정
- **즉시 피드백**: 틀린 부분 상세 설명

### 📊 결과 분석
- **점수 계산**: 정답률 및 점수
- **오답 분석**: 틀린 문제 별도 표시
- **재시험 지원**: 틀린 문제만 다시 시험

### 💾 다양한 저장 형식
- **마크다운**: 구조화된 결과
- **텍스트**: 간단한 결과
- **HTML**: 웹에서 확인 가능

## 🔧 고급 사용법

### 키보드 단축키
- `Ctrl+O`: 파일 열기
- `Ctrl+S`: 결과 저장
- `Ctrl+,`: 설정 열기
- `Enter`: 다음 문제
- `Esc`: 창 닫기

### 배치 모드 (개발자용)
```python
from src.core.models import WordPair
from src.services.openai_service import OpenAIService

# 프로그래밍 방식으로 시험 생성
service = OpenAIService(config)
results = service.grade_test(answers, correct_words)
```

## 🐛 문제 해결

### 일반적인 문제들

#### 1. OpenAI API 오류
```
❌ API 키가 유효하지 않습니다
✅ 해결: 설정에서 올바른 API 키 입력
```

#### 2. tkinter 오류 (Linux)
```bash
sudo apt install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
```

#### 3. 클립보드 오류 (Linux)
```bash
sudo apt install xclip  # Ubuntu/Debian
```

#### 4. 드래그 앤 드롭 비활성화
```
⚠️ tkinterdnd2 설치 실패 시 자동 비활성화
✅ 📂 파일 열기 버튼 사용
```

### 로그 확인
```bash
# 로그 파일 위치
logs/english_word_test_YYYYMMDD.log

# 실시간 로그 확인
tail -f logs/english_word_test_$(date +%Y%m%d).log
```

## 🔄 업데이트

### Git을 통한 업데이트
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 설정 백업
```bash
# 업데이트 전 설정 백업
cp config.json config.json.backup
cp .env .env.backup
```

## 🤝 기여하기

### 개발 환경 설정
```bash
# 개발용 설치
git clone <repository>
cd English_study
pip install -r requirements.txt
pip install pytest black isort  # 개발 도구

# 코드 포맷팅
black src/
isort src/
```

### 버그 리포트
이슈를 발견하시면 다음 정보와 함께 GitHub Issues에 보고해주세요:
- OS 및 Python 버전
- 오류 메시지
- 재현 단계
- 로그 파일 (`logs/` 폴더)

## 🔄 버전 히스토리

### v2.0.0 (2025-07-17)
- 🆕 완전한 모듈화 아키텍처
- 🆕 GUI 기반 설정 관리
- 🆕 다크/라이트 테마 시스템
- 🆕 시스템별 호환성 최적화
- 🆕 우분투/리눅스 완전 지원
- 🆕 드래그 앤 드롭 기능
- 🆕 상세한 결과 분석
- 🆕 다양한 저장 형식
- 🆕 키보드 단축키
- 🆕 로깅 시스템

### v1.0.0
- ✅ 기본 단어 시험 기능
- ✅ GPT 채점
- ✅ 마크다운 파싱

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- **OpenAI**: GPT API 제공
- **tkinter**: GUI 프레임워크  
- **Python 커뮤니티**: 다양한 라이브러리들

---

## 📞 지원

- 🐛 **버그 리포트**: GitHub Issues
- 📖 **문서**: Wiki 페이지
- 🐧 **Ubuntu 사용자**: [README_Ubuntu.md](README_Ubuntu.md)

**즐거운 영어 공부 되세요! 🎉**
