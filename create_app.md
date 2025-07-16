# macOS 앱 만들기 가이드

## 방법 1: Automator로 앱 만들기

1. **Automator 실행**
   - Spotlight에서 "Automator" 검색 → 실행

2. **새 문서 만들기**
   - "애플리케이션" 선택

3. **셸 스크립트 실행 추가**
   - 왼쪽에서 "유틸리티" → "셸 스크립트 실행"을 오른쪽으로 드래그

4. **스크립트 내용 입력**
   ```bash
   #!/bin/bash
   cd "/Users/swoonge/Documents/English_study"
   python3 main.py
   ```

5. **앱 저장**
   - 파일 → 저장
   - 이름: "단어시험"
   - 위치: 응용 프로그램 폴더

6. **완료**
   - 이제 Spotlight에서 "단어시험"으로 검색하면 나타납니다!

## 방법 2: 실행 스크립트 만들기

1. 실행 스크립트 생성
2. 스크립트에 실행 권한 부여
3. Spotlight 인덱싱 확인
