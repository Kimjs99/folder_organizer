# 📁 폴더 정리 자동화 프로그램 (Folder Organizer)

바탕화면, 문서 폴더, 다운로드 폴더에 파일이 무분별하게 쌓이는 문제를 해결하기 위한 CLI 자동화 도구입니다.

## 주요 기능
- **`init`**: 미리 정의된 연도별, 주제별 폴더 구조를 자동 생성합니다.
- **`sort`**: 대상을 지정하여 파일을 주제 및 연도에 맞게 자동 분류하고 이동합니다.
- **`clean-desktop`**: 바탕화면 공간을 빠르게 정리합니다.
- **`clean-downloads`**: 다운로드 폴더의 오래된 파일(기본 7일 이상)을 정리합니다.
- **`status`**: 정리함의 현재 상태와 용량, 바탕화면/다운로드 폴더의 상태를 보고합니다.

## 설치 및 실행
```bash
# 의존성 설치 (pip 사용)
pip install click rich pyyaml

# CLI 도우미 실행
python organizer.py --help
```

## 사용법

**1. 초기화**
```bash
python organizer.py init
```

**2. 파일 분류 (안전 확인형)**
```bash
python organizer.py sort --source ~/Desktop --dry-run
```

**3. 바탕화면 정리 적용**
```bash
python organizer.py clean-desktop
```

**4. 다운로드 정리 (7일 이상 된 파일)**
```bash
python organizer.py clean-downloads --days 7
```

**5. 상태 확인**
```bash
python organizer.py status
```
