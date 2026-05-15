"""GitHub Releases API를 통한 자동 업데이트 체크 및 다운로드."""
import os
import sys
import threading
import tempfile
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from organizer.version import __version__

GITHUB_REPO = "Kimjs99/folder_organizer"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def _parse_version(tag: str) -> tuple[int, ...]:
    tag = tag.lstrip("v")
    parts = tag.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0,)


def check_for_updates(callback):
    """백그라운드 스레드에서 업데이트 확인 후 callback(tag, download_url) 호출."""
    def _check():
        try:
            req = Request(API_URL, headers={"User-Agent": "folder-organizer-updater"})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())

            latest_tag = data.get("tag_name", "")
            current = _parse_version(__version__)
            latest = _parse_version(latest_tag)

            if latest > current:
                # exe asset URL 탐색
                assets = data.get("assets", [])
                dl_url = next(
                    (a["browser_download_url"] for a in assets if a["name"].endswith(".exe")),
                    None,
                )
                if dl_url:
                    callback(latest_tag, dl_url)
        except (URLError, Exception):
            pass  # 네트워크 오류는 조용히 무시

    t = threading.Thread(target=_check, daemon=True)
    t.start()


def download_and_update(download_url: str, progress_callback=None):
    """exe를 다운로드하고 배치 스크립트로 자기 자신을 교체한다."""
    if not getattr(sys, "frozen", False):
        return  # 개발 환경에서는 실행하지 않음

    current_exe = Path(sys.executable)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=current_exe.parent)
    tmp_exe = Path(tmp_path)

    try:
        req = Request(download_url, headers={"User-Agent": "folder-organizer-updater"})
        with urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with os.fdopen(tmp_fd, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        progress_callback(downloaded / total)
    except Exception as e:
        try:
            os.close(tmp_fd)
        except OSError:
            pass
        tmp_exe.unlink(missing_ok=True)
        raise RuntimeError(f"다운로드 실패: {e}") from e

    # 배치 스크립트로 exe 교체 후 재실행
    bat_fd, bat_path = tempfile.mkstemp(suffix=".bat", dir=current_exe.parent)
    bat = Path(bat_path)
    script = (
        "@echo off\n"
        "timeout /t 2 /nobreak >nul\n"
        f'move /Y "{tmp_exe}" "{current_exe}"\n'
        f'start "" "{current_exe}"\n'
        'del "%~f0"\n'
    )
    with os.fdopen(bat_fd, "w", encoding="mbcs") as f:
        f.write(script)

    subprocess.Popen(
        ["cmd.exe", "/C", str(bat)],
        creationflags=subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )
    sys.exit(0)
