# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.1] - 2026-05-15

### 🐛 Bug Fixes
- **[BUG-001]** `AttributeError: module 'organizer' has no attribute 'cli'` 수정
  - PyInstaller 빌드 실행 파일에서 `--cli` 인수로 진입 시 `import organizer` 가 `organizer.py` 대신 `organizer/` 패키지를 로드하여 발생
  - `gui.py`: `importlib.util.spec_from_file_location` 으로 `organizer.py` 를 경로 기반으로 직접 로드하도록 변경
  - `폴더정리 자동화.spec`: `organizer.py` 를 `datas` 에 추가하여 빌드 시 `sys._MEIPASS` 에 포함

### 📝 Documentation
- CLAUDE.md 추가 — Claude Code 작업 가이드 및 아키텍처 설명 (8bb0390)
- CHANGELOG.md 초기 작성 — v0.1.0 릴리스 내역 (dce11dd)

## [v0.1.0] - 2026-03-27

### ✨ Features
- 바탕화면 파일 자동 분류 및 정리 (`clean-desktop`) (4908bc0)
- 다운로드 폴더 정리, 오래된 파일 기준 필터링 지원 (`clean-downloads --days`) (4908bc0)
- config.yaml 기반 키워드·확장자 규칙 분류기 (4908bc0)
- 파일 이동 히스토리 기록 및 실행 취소(`undo`) 지원 (4908bc0)
- dry-run 모드 지원 (4908bc0)
- OneDrive 플레이스홀더 파일 자동 감지 및 스킵 (WinError 362) (4908bc0)
- GUI 설정 화면 (`settings_gui`) (4908bc0)

### 🐛 Bug Fixes
- `clean-desktop`: `process_directory` 반환값 4개를 3개로 언패킹하던 오류 수정 (4908bc0)
- `clean-downloads`: 동일한 언패킹 오류 수정 (4908bc0)
