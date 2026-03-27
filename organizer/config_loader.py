import yaml
from pathlib import Path

def load_config(config_path=None):
    if not config_path:
        config_path = Path(__file__).parent.parent / "config.yaml"
    else:
        config_path = Path(config_path)
        
    if not config_path.exists():
        # Fallback to ~/.organizer/config.yaml
        home_config = Path.home() / ".organizer" / "config.yaml"
        if home_config.exists():
            config_path = home_config
        else:
            # Create default config in ~/.organizer/
            home_config.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                "root": "~/Documents/정리함",
                "rules": [
                    {"name": "문서", "extensions": [".txt", ".md", ".pdf", ".doc", ".docx", ".hwp", ".xls", ".xlsx", ".ppt", ".pptx"], "keywords": ["문서", "기획", "보고서"]},
                    {"name": "이미지", "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"], "keywords": ["사진", "이미지", "캡처", "스크린샷"]},
                    {"name": "미디어", "extensions": [".mp4", ".avi", ".mkv", ".mov", ".mp3", ".wav"], "keywords": ["영상", "음원", "녹음", "비디오"]},
                    {"name": "압축파일", "extensions": [".zip", ".tar", ".gz", ".7z", ".rar"], "keywords": ["압축"]},
                    {"name": "설치파일", "extensions": [".exe", ".msi", ".apk", ".dmg"], "keywords": ["설치", "setup", "install"]}
                ],
                "archive_before": 2024,
                "default_destination": "04_참고자료/다운로드_정리"
            }
            with open(home_config, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
            config_path = home_config

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
