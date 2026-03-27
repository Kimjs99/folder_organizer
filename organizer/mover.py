import shutil
import os
from pathlib import Path
from .logger import logger

SYSTEM_FILES = {".ds_store", "thumbs.db", ".localized"}

def is_hidden_or_system(filepath: Path) -> bool:
    name = filepath.name.lower()
    if name.startswith("."):
        return True
    if name in SYSTEM_FILES:
        return True
    # 단축아이콘: macOS .alias, Windows .lnk
    if name.endswith(".alias") or name.endswith(".lnk"):
        return True
    return False

def get_unique_path(dest_path: Path) -> Path:
    if not dest_path.exists():
        return dest_path
        
    stem = dest_path.stem
    ext = dest_path.suffix
    parent = dest_path.parent
    
    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1

def move_file(src: Path, dest_dir: Path, dry_run: bool = False) -> tuple[bool, str, Path | None]:
    """
    Moves file to dest_dir.
    Returns (success, message, new_path)
    """
    if is_hidden_or_system(src):
        return False, "system or hidden file", None
        
    if src.is_symlink():
        return False, "symlink", None

    # Do not move directories
    if src.is_dir():
        return False, "directory", None
        
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src.name
    
    dest_path = get_unique_path(dest_path)
    
    if not dry_run:
        try:
            shutil.move(str(src), str(dest_path))
            logger.info(f"MOVED: {src} -> {dest_path}")
            return True, "success", dest_path
        except OSError as e:
            if getattr(e, 'winerror', None) == 362:
                # WinError 362: The cloud file provider is not running.
                # This means the file is just a placeholder (OneDrive files On-Demand) and not physically on the disk.
                logger.warning(f"SKIPPED (Cloud File): {src}")
                return False, "cloud file not downloaded locally", None
            logger.error(f"ERROR moving {src} to {dest_path}: {e}")
            return False, f"error: {e}", None
        except Exception as e:
            logger.error(f"ERROR moving {src} to {dest_path}: {e}")
            return False, f"error: {e}", None
    else:
        return True, "dry-run", dest_path
