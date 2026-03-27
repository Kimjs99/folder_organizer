# Changelog

All notable changes to this project will be documented in this file.

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
