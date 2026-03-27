# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# 의존성 설치
pip install -r requirements.txt

# CLI 실행
python organizer.py --help
python organizer.py clean-desktop
python organizer.py clean-downloads --days 7
python organizer.py sort --source ~/Desktop --dry-run
python organizer.py status
python organizer.py undo

# 테스트 실행
pytest tests/
pytest tests/test_classifier.py::test_classifier_extensions  # 단일 테스트
```

## Architecture

진입점은 `organizer.py` 하나이며, Click CLI 커맨드 그룹으로 구성됩니다. 핵심 로직은 `organizer/` 패키지에 분리되어 있습니다.

### 파일 처리 흐름

```
CLI 커맨드 (organizer.py)
  └─ collect_files_recursive()   # rglob으로 수집, 정리함·숨김파일 제외
  └─ Classifier.classify()       # 연도 폴더 + 주제 폴더 결정
  └─ move_file()                 # 실제 이동, 충돌 시 _1 suffix 처리
  └─ HistoryManager.add_record() # ~/.organizer/history.json에 이동 기록 저장
```

### 분류 로직 (`organizer/classifier.py`)

- **연도**: 파일의 mtime 기준. `archive_before` 연도 미만이면 `_Archive/`로
- **주제**: `config.yaml`의 `rules` 순서대로 매칭 (확장자 우선, 그 다음 파일명 키워드)
- 매칭 없으면 `default_destination`으로

### 건너뛰는 파일 (`organizer/mover.py`)

- `.lnk`, `.alias` (바탕화면 바로가기)
- 숨김 파일(`.`으로 시작)
- 심볼릭 링크, 디렉토리
- OneDrive 플레이스홀더 (WinError 362) — 로컬에 내려받히지 않은 클라우드 파일

### 설정 (`config.yaml`)

- `root`: 정리함 루트 경로 (기본 `~/Documents/정리함`)
- `rules`: 이름·확장자·키워드 목록, 위에서 아래로 우선순위 적용
- `archive_before`: 이 연도 미만 파일은 `_Archive/`로
- `default_destination`: 분류 미매칭 파일의 기본 목적지

설정 파일 탐색 순서: `프로젝트루트/config.yaml` → `~/.organizer/config.yaml` (없으면 자동 생성)

### `process_directory()` 반환값

`(success_count, skip_count, error_count, moves)` — 4개 튜플. `moves`는 undo 이력용 딕셔너리 리스트.

### 히스토리 / Undo

`~/.organizer/history.json`에 이동 기록을 누적 저장. `undo` 커맨드는 기본적으로 마지막 작업을 되돌리며, `--id`로 특정 작업 지정 가능.

### Windows 경로 처리

바탕화면·다운로드·문서 경로는 `get_windows_path()`로 winreg에서 읽음 (OneDrive 이동 등 비표준 경로 대응). 실패 시 `~/Desktop` 등으로 폴백.
