import click
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from rich.progress import track

from organizer.config_loader import load_config
from organizer.classifier import Classifier
from organizer.mover import move_file
from organizer import reporter

@click.group()
def cli():
    """📁 폴더 정리 자동화 프로그램"""
    pass

@cli.command()
def init():
    """정리함 폴더 구조 초기화 및 바탕화면 바로가기 생성"""
    config = load_config()
    root = Path(config["root"]).expanduser()
    archive_before = config.get("archive_before", 2024)
    rules = config.get("rules", [])
    
    current_year = datetime.now().year
    years = [current_year, current_year - 1, current_year - 2]
    
    created_folders = []
    
    root.mkdir(parents=True, exist_ok=True)
    
    for year in years:
        year_folder = root / f"{year}년"
        year_folder.mkdir(exist_ok=True)
        created_folders.append(f"{year}년/")
        
        for rule in rules:
            folder_path = year_folder / rule["name"]
            folder_path.mkdir(parents=True, exist_ok=True)
            
    archive_folder = root / "_Archive"
    archive_folder.mkdir(exist_ok=True)
    created_folders.append("_Archive/")
    
    # Create desktop shortcut
    desktop = get_default_path("Desktop")
    if desktop and desktop.exists():
        shortcut_path = desktop / "정리함 바로가기.lnk"
        try:
            import subprocess
            ps_script = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{root}'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True)
            reporter.print_success(f"원활한 접근을 위해 바탕화면에 바로가기를 생성했습니다.")
        except Exception as e:
            reporter.print_error(f"바로가기 생성 실패: {e}")
            
    reporter.print_success(f"정리함 폴더 구조를 생성했습니다: {root}/")
    reporter.print_info(f"📁 {' ... '.join(created_folders)}")

def collect_files_recursive(source_dir: Path, root_dir: Path, min_days: int = 0) -> list:
    """하위 폴더까지 포함해 파일 수집. 정리함(root_dir) 안의 파일은 제외."""
    root_resolved = root_dir.resolve()
    files = []
    for f in source_dir.rglob("*"):
        if not f.is_file():
            continue
        if f.name.startswith("."):
            continue
        # 정리함 안에 있는 파일은 제외 (문서 폴더 스캔 시 정리함 자체 제외)
        try:
            if root_resolved in f.parents or f.parent == root_resolved:
                continue
        except (ValueError, OSError):
            pass
        if min_days > 0:
            threshold = datetime.now() - timedelta(days=min_days)
            if datetime.fromtimestamp(f.stat().st_mtime) >= threshold:
                continue
        files.append(f)
    return files


def process_directory(source_dir: Path, classifier: Classifier, config: dict, dry_run: bool = False, min_days: int = 0, in_place: bool = False):
    if not source_dir.exists():
        reporter.print_error(f"경로를 찾을 수 없습니다: {source_dir}")
        return 0, 0, 0, []
        
    if in_place:
        root_dir = source_dir
    else:
        root_dir = Path(config["root"]).expanduser()
    
    success_count = 0
    skip_count = 0
    error_count = 0
    moves = []
    
    # 하위 폴더 포함 재귀 수집 (정리함 내부 파일 제외)
    files = collect_files_recursive(source_dir, root_dir, min_days=min_days)

    if not files:
        reporter.print_info(f"{source_dir} 에 정리할 파일이 없습니다.")
        return 0, 0, 0, []
    
    # Process files
    for filepath in track(files, description=f"{source_dir.name} 정리 중..."):
        dest_rel_path = classifier.classify(filepath)
        dest_dir = root_dir / dest_rel_path
        
        if dry_run:
            reporter.print_preview(filepath.name, f"{dest_rel_path}/")
            success_count += 1
            continue
            
        success, msg, new_path = move_file(filepath, dest_dir, dry_run=False)
        if success and new_path:
            success_count += 1
            moves.append({
                "original_src": str(filepath.resolve()),
                "new_dest": str(new_path.resolve())
            })
        elif msg in ["system or hidden file", "symlink", "directory", "cloud file not downloaded locally"]:
            skip_count += 1
        else:
            error_count += 1
            reporter.print_error(f"Failed to move {filepath.name}: {msg}")
            
    return success_count, skip_count, error_count, moves

def get_windows_path(folder_id):
    import ctypes.wintypes
    CSIDL_DESKTOP = 0x0000
    CSIDL_PERSONAL = 0x0005 # My Documents
    CSIDL_DOWNLOADS = "{374DE290-123F-4565-9164-39C4925E467B}"
    
    # We use a simple fallback if ctypes fails
    # This is a robust way to get Windows known folders
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        
        if folder_id == "Desktop":
            val, _ = winreg.QueryValueEx(key, "Desktop")
        elif folder_id == "Downloads":
            val, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
        elif folder_id == "Documents":
            val, _ = winreg.QueryValueEx(key, "Personal")
        else:
            return None
            
        winreg.CloseKey(key)
        
        # Expand environment variables like %USERPROFILE%
        import os
        return Path(os.path.expandvars(val))
    except Exception:
        return None

def get_default_path(folder_name):
    if os.name == 'nt':
        win_path = get_windows_path(folder_name)
        if win_path and win_path.exists():
            return win_path
    
    # Fallback
    if folder_name == "Desktop":
        return Path.home() / "Desktop"
    elif folder_name == "Downloads":
        return Path.home() / "Downloads"
    elif folder_name == "Documents":
        return Path.home() / "Documents"
    return Path.home() / folder_name

@cli.command()
@click.option('--source', multiple=True, help='정리 대상 경로 (기본값: 바탕화면, 다운로드)')
@click.option('--dry-run', is_flag=True, help='실제 이동 없이 출력만 수행')
@click.option('--verbose', is_flag=True, help='상세 출력')
@click.option('--in-place', is_flag=True, help='정리함으로 이동하지 않고 해달 폴더 안에서 하위 규칙대로 정리')
def sort(source, dry_run, verbose, in_place):
    """지정된 폴더의 파일을 분류·이동"""
    config = load_config()
    classifier = Classifier(config)
    
    if not source:
        sources = [get_default_path("Desktop"), get_default_path("Documents"), get_default_path("Downloads")]
    else:
        sources = []
        for s in source:
            s_expanded = Path(s).expanduser()
            # If the user exactly types ~/Desktop, map to the true Desktop
            if s_expanded == Path.home() / "Desktop":
                sources.append(get_default_path("Desktop"))
            elif s_expanded == Path.home() / "Downloads":
                sources.append(get_default_path("Downloads"))
            elif s_expanded == Path.home() / "Documents":
                sources.append(get_default_path("Documents"))
            else:
                sources.append(s_expanded)
        
    total_success, total_skip, total_error = 0, 0, 0
    all_moves = []
    
    for s in sources:
        success, skip, error, moves = process_directory(s, classifier, config, dry_run=dry_run, in_place=in_place)
        total_success += success
        total_skip += skip
        total_error += error
        
    if dry_run:
        reporter.print_info(f"총 {total_success}개 파일 이동 예정 | {total_skip}개 건너뜀")
    else:
        reporter.print_success(f"완료: {total_success}개 이동 | {total_skip}개 건너뜀 | {total_error}개 오류")

@cli.command()
@click.option('--dry-run', is_flag=True, help='실제 이동 없이 출력만 수행')
def clean_desktop(dry_run):
    """바탕화면의 파일을 정리"""
    config = load_config()
    classifier = Classifier(config)
    
    desktop = get_default_path("Desktop")
    success, skip, error, _ = process_directory(desktop, classifier, config, dry_run=dry_run)
    
    if dry_run:
        reporter.print_info(f"총 {success}개 파일 이동 예정 | {skip}개 건너뜀")
    else:
        reporter.print_success(f"완료: {success}개 이동 | {skip}개 건너뜀 | {error}개 오류")
        
    # 남은 파일 리스트 출력
    left_files = [f.name for f in desktop.iterdir() if f.is_file() and not f.name.startswith(".")]
    if left_files:
        reporter.print_info(f"바탕화면에 남은 항목: {', '.join(left_files[:5])}" + ("..." if len(left_files) > 5 else ""))

@cli.command()
@click.option('--days', default=7, help='정리 기준 일수 (기본값: 7일)')
@click.option('--dry-run', is_flag=True, help='실제 이동 없이 출력만 수행')
def clean_downloads(days, dry_run):
    """다운로드 폴더 정리 (오래된 파일)"""
    config = load_config()
    classifier = Classifier(config)
    
    downloads = get_default_path("Downloads")
    success, skip, error, _ = process_directory(downloads, classifier, config, dry_run=dry_run, min_days=days)
    
    if set_remove := False: # Delete logic is explicitly forbidden for now based on spec: "삭제 기능 없음: 파일을 삭제하지 않는다."
        pass
        
    if dry_run:
        reporter.print_info(f"총 {success}개 파일 이동 예정 (기준: {days}일 이상) | {skip}개 건너뜀")
    else:
        reporter.print_success(f"완료: {success}개 이동 | {skip}개 건너뜀 | {error}개 오류")

def get_dir_size(path: Path) -> tuple[int, int]:
    count = 0
    size = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = Path(root) / f
            if fp.is_file() and not f.startswith("."):
                count += 1
                size += fp.stat().st_size
    return count, size

@cli.command()
@click.option('--list', 'show_list', is_flag=True, help='최근 작업 목록 보기')
@click.option('--id', 'record_id', default=None, help='특정 작업 ID 번호로 되돌리기')
def undo(show_list, record_id):
    """이전 정리 작업을 되돌림 (Undo)"""
    from organizer.history import HistoryManager
    import shutil
    
    hm = HistoryManager()
    history = hm.load()
    
    if not history:
        reporter.print_info("되돌릴 작업 내역이 없습니다.")
        return
        
    if show_list:
        reporter.print_info("=== 최근 작업 내역 ===")
        for i, r in enumerate(reversed(history)):
            reporter.print_info(f"[{i}] ID: {r['id']} | 시간: {r['timestamp']} | 명령: {r['command']} | 이동된 파일 수: {len(r['moves'])}개")
            if i >= 9:
                break
        return
        
    if record_id:
        record = next((r for r in history if r["id"] == record_id), None)
        if not record:
            reporter.print_error(f"주어진 ID({record_id})를 가진 내역을 찾을 수 없습니다.")
            return
    else:
        record = history[-1]
        
    reporter.print_info(f"[{record['timestamp']}] 에 실행된 '{record['command']}' 작업을 되돌립니다... ({len(record['moves'])}개 파일)")
    
    success, error = 0, 0
    for move in record["moves"]:
        src = Path(move["original_src"])
        dest = Path(move["new_dest"])
        
        if dest.exists():
            try:
                src.parent.mkdir(parents=True, exist_ok=True)
                # handle collisions on revert
                if src.exists():
                    from organizer.mover import get_unique_path
                    src = get_unique_path(src)
                shutil.move(str(dest), str(src))
                success += 1
            except Exception as e:
                reporter.print_error(f"되돌리기 실패: {dest.name} -> {src.name} ({e})")
                error += 1
        else:
            reporter.print_error(f"파일을 찾을 수 없습니다: {dest}")
            error += 1
            
    reporter.print_success(f"되돌리기 완료: {success}개 복구됨, {error}개 오류")
    hm.remove_record(record["id"])

@cli.command()
def status():
    """정리함 상태 리포트 출력"""
    config = load_config()
    root = Path(config["root"]).expanduser()
    
    years_stats = {}
    if root.exists():
        for item in root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                count, size = get_dir_size(item)
                years_stats[item.name] = {"count": count, "size": size}
                
    desktop = get_default_path("Desktop")
    downloads = get_default_path("Downloads")
    
    desktop_count = 0
    if desktop and desktop.exists():
        desktop_count = len([f for f in desktop.iterdir() if f.is_file() and not f.name.startswith(".")])
        
    downloads_count = 0
    downloads_oldest = "N/A"
    if downloads and downloads.exists():
        files = [f for f in downloads.iterdir() if f.is_file() and not f.name.startswith(".")]
        downloads_count = len(files)
        if files:
            oldest_file = min(files, key=lambda x: x.stat().st_mtime)
            mtime = datetime.fromtimestamp(oldest_file.stat().st_mtime)
            downloads_oldest = mtime.strftime("%Y-%m-%d")
            
    reporter.print_status(years_stats, desktop_count, downloads_count, downloads_oldest)

if __name__ == '__main__':
    cli()
