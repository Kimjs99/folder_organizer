import logging
from pathlib import Path
from datetime import datetime

def setup_logger():
    log_dir = Path.home() / ".organizer" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today_str}.log"
    
    logger = logging.getLogger("folder_organizer")
    logger.setLevel(logging.INFO)
    
    # Remove all handlers if any exist to prevent duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    
    return logger

logger = logging.getLogger("folder_organizer")
if not logger.handlers:
    logger = setup_logger()
