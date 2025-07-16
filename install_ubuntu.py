#!/usr/bin/env python3
"""
우분투/리눅스 배포용 설치 스크립트
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_system():
    """시스템 호환성을 확인합니다."""
    print(f"🔍 시스템 정보: {platform.system()} {platform.release()}")
    print(f"🐍 Python 버전: {sys.version}")
    
    # Python 버전 확인
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 이상이 필요합니다.")
        return False
    
    return True

def install_system_dependencies():
    """시스템 레벨 의존성을 설치합니다."""
    print("🔧 시스템 의존성 확인 중...")
    
    if platform.system() == "Linux":
        try:
            # tkinter 및 관련 의존성 확인
            print("📦 tkinter 의존성 확인 중...")
            subprocess.run(["python3", "-c", "import tkinter"], check=True, capture_output=True)
            print("✅ tkinter가 이미 설치되어 있습니다.")
        except subprocess.CalledProcessError:
            print("⚠️  tkinter가 설치되지 않았습니다.")
            print("다음 명령으로 설치하세요:")
            print("Ubuntu/Debian: sudo apt-get install python3-tk")
            print("CentOS/RHEL: sudo yum install tkinter")
            print("Fedora: sudo dnf install python3-tkinter")
            return False
        
        try:
            # 클립보드 기능을 위한 의존성 확인
            print("📋 클립보드 의존성 확인 중...")
            subprocess.run(["which", "xclip"], check=True, capture_output=True)
            print("✅ xclip이 이미 설치되어 있습니다.")
        except subprocess.CalledProcessError:
            print("⚠️  xclip이 설치되지 않았습니다.")
            print("다음 명령으로 설치하세요:")
            print("Ubuntu/Debian: sudo apt-get install xclip")
            print("CentOS/RHEL: sudo yum install xclip")
            print("Fedora: sudo dnf install xclip")
            return False
    
    return True

def install_python_dependencies():
    """Python 의존성을 설치합니다."""
    print("🐍 Python 패키지 설치 중...")
    
    try:
        # pip 업그레이드
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # requirements.txt에서 패키지 설치
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Python 패키지 설치가 완료되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Python 패키지 설치 실패: {e}")
        return False

def create_desktop_entry():
    """데스크톱 엔트리를 생성합니다 (리눅스용)."""
    if platform.system() != "Linux":
        return
    
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    current_dir = Path.cwd()
    python_exec = sys.executable
    
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=영어 단어 시험
Comment=AI 기반 영어 단어 시험 프로그램
Exec={python_exec} {current_dir}/main.py
Icon={current_dir}/icon.png
Path={current_dir}
Terminal=false
StartupNotify=true
Categories=Education;Languages;
"""
    
    desktop_file = desktop_dir / "english-word-test.desktop"
    try:
        with open(desktop_file, 'w', encoding='utf-8') as f:
            f.write(desktop_content)
        
        # 실행 권한 부여
        os.chmod(desktop_file, 0o755)
        
        print(f"✅ 데스크톱 엔트리가 생성되었습니다: {desktop_file}")
    except Exception as e:
        print(f"⚠️  데스크톱 엔트리 생성 실패: {e}")

def create_launcher_script():
    """실행 스크립트를 생성합니다."""
    current_dir = Path.cwd()
    python_exec = sys.executable
    
    # bash 스크립트 생성
    launcher_content = f"""#!/bin/bash
cd "{current_dir}"
{python_exec} main.py "$@"
"""
    
    launcher_file = current_dir / "run.sh"
    try:
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # 실행 권한 부여
        os.chmod(launcher_file, 0o755)
        
        print(f"✅ 실행 스크립트가 생성되었습니다: {launcher_file}")
        print(f"   터미널에서 './run.sh'로 실행할 수 있습니다.")
    except Exception as e:
        print(f"⚠️  실행 스크립트 생성 실패: {e}")

def main():
    """메인 설치 함수"""
    print("🚀 영어 단어 시험 프로그램 우분투 설치 시작")
    print("=" * 50)
    
    # 시스템 확인
    if not check_system():
        sys.exit(1)
    
    # 시스템 의존성 확인
    if not install_system_dependencies():
        print("\n⚠️  시스템 의존성을 수동으로 설치한 후 다시 실행해주세요.")
        sys.exit(1)
    
    # Python 의존성 설치
    if not install_python_dependencies():
        sys.exit(1)
    
    # 데스크톱 엔트리 생성
    create_desktop_entry()
    
    # 실행 스크립트 생성
    create_launcher_script()
    
    print("\n" + "=" * 50)
    print("🎉 설치가 완료되었습니다!")
    print("\n실행 방법:")
    print("1. 터미널: ./run.sh")
    print("2. Python: python3 main.py")
    print("3. 데스크톱: 응용프로그램 메뉴에서 '영어 단어 시험' 검색")

if __name__ == "__main__":
    main()
