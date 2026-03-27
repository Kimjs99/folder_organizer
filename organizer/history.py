import json
from pathlib import Path
from datetime import datetime

class HistoryManager:
    def __init__(self):
        self.history_dir = Path.home() / ".organizer"
        self.history_dir.mkdir(exist_ok=True)
        self.file_path = self.history_dir / "history.json"
        
    def load(self):
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
            
    def save(self, history):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
    def add_record(self, command_name, moves):
        if not moves:
            return
        history = self.load()
        record = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command_name,
            "moves": moves
        }
        history.append(record)
        self.save(history)
        
    def get_latest_record(self):
        history = self.load()
        return history[-1] if history else None
        
    def remove_record(self, record_id):
        history = self.load()
        history = [r for r in history if r["id"] != record_id]
        self.save(history)
