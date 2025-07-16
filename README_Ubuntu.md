# 영어 단어 시험 프로그램 - 우분투 설치 가이드

## 🚀 우분투에서 설치하기

### 필수 요구사항

#### 시스템 요구사항
- Ubuntu 18.04 LTS 이상 (또는 Debian 기반 배포판)
- Python 3.7 이상
- 인터넷 연결 (OpenAI API 사용)

#### 시스템 패키지 설치

```bash
# 우분투/데비안
sudo apt update
sudo apt install python3 python3-pip python3-tk xclip

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip tkinter xclip  # Fedora
sudo yum install python3 python3-pip tkinter xclip  # CentOS/RHEL
```

### 📦 자동 설치 (권장)

1. **저장소 다운로드**
```bash
git clone <repository-url>
cd english-word-test
```

2. **자동 설치 실행**
```bash
python3 install_ubuntu.py
```

이 스크립트는 다음을 자동으로 수행합니다:
- 시스템 호환성 확인
- Python 패키지 설치
- 데스크톱 엔트리 생성
- 실행 스크립트 생성

### 🛠️ 수동 설치

#### 1단계: Python 패키지 설치
```bash
pip3 install -r requirements.txt
```

#### 2단계: 실행 권한 부여
```bash
chmod +x run.sh
```

#### 3단계: 데스크톱 엔트리 생성 (선택사항)
```bash
# 데스크톱 엔트리 디렉토리 생성
mkdir -p ~/.local/share/applications

# 데스크톱 엔트리 파일 생성
cat > ~/.local/share/applications/english-word-test.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=영어 단어 시험
Comment=AI 기반 영어 단어 시험 프로그램
Exec=$(which python3) $(pwd)/main.py
Path=$(pwd)
Terminal=false
StartupNotify=true
Categories=Education;Languages;
EOF

# 실행 권한 부여
chmod +x ~/.local/share/applications/english-word-test.desktop
```

## 🏃‍♂️ 실행하기

### 방법 1: 터미널에서 실행
```bash
./run.sh
```

### 방법 2: Python으로 직접 실행
```bash
python3 main.py
```

### 방법 3: 데스크톱에서 실행
응용프로그램 메뉴에서 "영어 단어 시험"을 검색하여 실행

## ⚙️ 설정

### OpenAI API 키 설정
1. 프로그램 실행 후 "⚙️ 설정" 버튼 클릭
2. OpenAI API 키 입력
3. "테스트" 버튼으로 연결 확인
4. "💾 저장" 클릭

또는 직접 `.env` 파일 생성:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 폴더 설정
- 단어 파일 폴더: 마크다운 단어 파일들을 저장할 폴더
- 결과 폴더: 시험 결과를 저장할 폴더

## 🐛 문제 해결

### 1. tkinter 관련 오류
```bash
# 우분투/데비안
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Fedora
sudo dnf install python3-tkinter
```

### 2. 클립보드 기능 오류
```bash
sudo apt install xclip  # 우분투/데비안
sudo yum install xclip  # CentOS/RHEL
sudo dnf install xclip  # Fedora
```

### 3. 드래그 앤 드롭 기능 비활성화
tkinterdnd2 패키지 설치 실패 시 드래그 앤 드롭이 비활성화됩니다.
"📂 파일 열기" 버튼을 사용하여 파일을 선택할 수 있습니다.

### 4. 폰트 관련 문제
프로그램이 시스템에 최적화된 폰트를 자동으로 선택합니다.
일반적인 리눅스 폰트들:
- DejaVu Sans
- Liberation Sans
- Ubuntu
- Noto Sans

### 5. 권한 문제
```bash
# 실행 권한 부여
chmod +x run.sh
chmod +x main.py

# 파일 접근 권한 확인
ls -la config.json .env
```

## 📊 시스템 호환성 확인

시스템 호환성 보고서 생성:
```bash
python3 -c "from src.utils.system_compatibility import SystemCompatibility; SystemCompatibility.print_system_report()"
```

## 🔄 업데이트

```bash
git pull origin main
pip3 install -r requirements.txt --upgrade
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Python 3.7+ 설치 확인: `python3 --version`
2. 필수 시스템 패키지 설치 확인
3. 로그 파일 확인: `logs/` 폴더
4. 시스템 호환성 보고서 생성

## 🌟 기능

- ✅ 시스템별 자동 폰트 선택
- ✅ 우분투/Debian 완전 호환
- ✅ 클립보드 기능 지원
- ✅ 데스크톱 통합
- ✅ 자동 설치 스크립트
- ⚠️ 드래그 앤 드롭 (선택적 지원)

## 📋 테스트된 환경

- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS  
- Debian 11
- Linux Mint 21
- Pop!_OS 22.04

---

더 자세한 정보는 메인 README.md를 참조하세요.
