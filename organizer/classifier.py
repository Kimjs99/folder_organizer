import os
from pathlib import Path
from datetime import datetime

class Classifier:
    def __init__(self, config):
        self.config = config
        self.archive_before = self.config.get("archive_before", 2024)
        self.rules = self.config.get("rules", [])
        self.default_destination = self.config.get("default_destination", "04_참고자료/다운로드_정리")
        
    def get_year_folder(self, filepath: Path) -> str:
        stat = filepath.stat()
        mtime = stat.st_mtime
        year = datetime.fromtimestamp(mtime).year
        
        if year < self.archive_before:
            return "_Archive"
        return f"{year}년"
        
    def get_topic_folder(self, filepath: Path) -> str:
        filename = filepath.name.lower()
        ext = filepath.suffix.lower()
        
        for rule in self.rules:
            # Check extensions
            if ext and ext in rule.get("extensions", []):
                return rule["name"]
                
            # Check keywords
            for keyword in rule.get("keywords", []):
                if keyword.lower() in filename:
                    return rule["name"]
                    
        return self.default_destination

    def classify(self, filepath: Path) -> str:
        year_folder = self.get_year_folder(filepath)
        if year_folder == "_Archive":
            return year_folder
            
        topic_folder = self.get_topic_folder(filepath)
        return f"{year_folder}/{topic_folder}"
