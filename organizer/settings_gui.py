import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import yaml
import sys
import os

def _get_config_path():
    base_dir = Path(__file__).parent.parent.resolve()
    if getattr(sys, 'frozen', False):
        config_path = Path.home() / ".organizer" / "config.yaml"
    else:
        config_path = base_dir / "config.yaml"
        if not config_path.exists():
            config_path = Path.home() / ".organizer" / "config.yaml"
    return config_path

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ 분류 규칙 설정")
        self.geometry("700x500")
        
        self.config_path = _get_config_path()
        
        from organizer.config_loader import load_config
        self.config_data = load_config(self.config_path)
        self.rules = self.config_data.get("rules", [])
        
        # To make it modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkLabel(self, text="분류된 파일이 들어갈 하위 폴더와 조건을 설정합니다.", font=ctk.CTkFont(size=14))
        header.grid(row=0, column=0, pady=(15, 5))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        
        # Column headers
        self.scroll_frame.grid_columnconfigure(0, weight=2)
        self.scroll_frame.grid_columnconfigure(1, weight=3)
        self.scroll_frame.grid_columnconfigure(2, weight=3)
        self.scroll_frame.grid_columnconfigure(3, weight=1)
        
        lbl_folder = ctk.CTkLabel(self.scroll_frame, text="폴더명", font=ctk.CTkFont(weight="bold"))
        lbl_folder.grid(row=0, column=0, sticky="w", padx=5)
        
        lbl_kw = ctk.CTkLabel(self.scroll_frame, text="키워드", font=ctk.CTkFont(weight="bold"))
        lbl_kw.grid(row=0, column=1, sticky="w", padx=5)
        
        lbl_ext = ctk.CTkLabel(self.scroll_frame, text="확장자", font=ctk.CTkFont(weight="bold"))
        lbl_ext.grid(row=0, column=2, sticky="w", padx=5)
        
        self.rule_rows = []
        self.refresh_list()
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=15, padx=15, sticky="ew")
        
        add_btn = ctk.CTkButton(btn_frame, text="➕ 규칙 추가", command=self.add_rule)
        add_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(btn_frame, text="✔️ 저장 및 닫기", command=self.save_and_close)
        save_btn.pack(side="right", padx=5)
        
    def refresh_list(self):
        # Clear existing rows
        for row in self.rule_rows:
            for widget in row:
                widget.destroy()
        self.rule_rows.clear()
        
        for idx, rule in enumerate(self.rules):
            folder = ctk.CTkLabel(self.scroll_frame, text=rule.get("name", ""))
            folder.grid(row=idx+1, column=0, sticky="w", padx=5, pady=5)
            
            kws = ", ".join(rule.get("keywords", []))
            # limit length for display
            if len(kws) > 30: kws = kws[:27] + "..."
            kw_lbl = ctk.CTkLabel(self.scroll_frame, text=kws)
            kw_lbl.grid(row=idx+1, column=1, sticky="w", padx=5, pady=5)
            
            e_str = ", ".join(rule.get("extensions", []))
            if len(e_str) > 30: e_str = e_str[:27] + "..."
            ext_lbl = ctk.CTkLabel(self.scroll_frame, text=e_str)
            ext_lbl.grid(row=idx+1, column=2, sticky="w", padx=5, pady=5)
            
            del_f = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            del_f.grid(row=idx+1, column=3, pady=5)
            
            up_btn = ctk.CTkButton(del_f, text="↑", width=30, command=lambda i=idx: self.move_rule(i, -1))
            up_btn.pack(side="left", padx=2)
            down_btn = ctk.CTkButton(del_f, text="↓", width=30, command=lambda i=idx: self.move_rule(i, 1))
            down_btn.pack(side="left", padx=2)
            del_btn = ctk.CTkButton(del_f, text="❌", width=30, fg_color="#D9534F", hover_color="#C9302C", command=lambda i=idx: self.delete_rule(i))
            del_btn.pack(side="left", padx=2)
            
            self.rule_rows.append((folder, kw_lbl, ext_lbl, del_f, up_btn, down_btn, del_btn))
            
    def move_rule(self, idx, direction):
        new_idx = idx + direction
        if 0 <= new_idx < len(self.rules):
            self.rules[idx], self.rules[new_idx] = self.rules[new_idx], self.rules[idx]
            self.refresh_list()

    def add_rule(self):
        dlg = RuleEditDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.rules.append(dlg.result)
            self.refresh_list()
            
    def delete_rule(self, idx):
        if messagebox.askyesno("확인", "해당 규칙을 삭제하시겠습니까?"):
            del self.rules[idx]
            self.refresh_list()
            
    def save_and_close(self):
        self.config_data["rules"] = self.rules
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f, allow_unicode=True, sort_keys=False)
        messagebox.showinfo("완료", "분류 규칙이 저장되었습니다.")
        self.destroy()

class RuleEditDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("새 규칙 추가")
        self.geometry("400x350")
        self.result = None
        
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="폴더명 (예: 업무/보고서):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(20, 5), padx=20, sticky="w")
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.name_var, width=350).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        ctk.CTkLabel(self, text="키워드 (쉼표 구분):", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, pady=(5, 5), padx=20, sticky="w")
        self.kw_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.kw_var, width=350, placeholder_text="예: 보고서, 결과, 기획").grid(row=3, column=0, padx=20, pady=(0, 15), sticky="w")
        
        ctk.CTkLabel(self, text="확장자 (쉼표 구분):", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, pady=(5, 5), padx=20, sticky="w")
        self.ext_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.ext_var, width=350, placeholder_text="예: .pdf, .docx, .hwp").grid(row=5, column=0, padx=20, pady=(0, 20), sticky="w")
        
        ctk.CTkButton(self, text="✔️ 확인 및 추가", command=self.on_ok).grid(row=6, column=0, pady=10)
        
    def on_ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("오류", "폴더명을 입력하세요.", parent=self)
            return
            
        keywords = [k.strip() for k in self.kw_var.get().split(",") if k.strip()]
        extensions = [e.strip().lower() for e in self.ext_var.get().split(",") if e.strip()]
        
        # Ensure extensions start with dot
        extensions = [e if e.startswith(".") else "." + e for e in extensions]
        
        self.result = {
            "name": name,
            "keywords": keywords,
            "extensions": extensions
        }
        self.destroy()

def open_settings_dialog(parent):
    SettingsDialog(parent)
