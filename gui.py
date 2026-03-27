import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import os
from pathlib import Path

try:
    import organizer.settings_gui
except ImportError:
    pass

# 현재 스크립트 위치 저장
BASE_DIR = Path(__file__).parent.resolve()

# 초기 테마 설정
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OrganizerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📁 폴더 정리 자동화 프로그램 (프리미엄)")
        self.geometry("750x600")
        
        # Grid weight config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        # 상단 설정 바 (테마 선택 영역 포함)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(header_frame, text="✨ Folder Organizer", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # 테마 선택기
        self.theme_var = ctk.StringVar(value="모던 다크 모드 (글래스 블루/퍼플 테마)")
        theme_menu = ctk.CTkOptionMenu(
            header_frame, 
            values=[
                "모던 다크 모드 (글래스 블루/퍼플 테마)", 
                "라이트 Fluent 디자인 (윈도우 11 느낌)",
                "전문가용 하이테크 대시보드 (네온 그린/민트 테마)"
            ],
            variable=self.theme_var,
            command=self.change_theme,
            width=300
        )
        theme_menu.grid(row=0, column=1, sticky="e")
        
        self.colored_buttons = []
        self.theme_option_menu = theme_menu
        
        # 단축 버튼 프레임
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(btn_frame, text="✅ 단축 액션", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5), columnspan=6)
        
        actions = [
            ("📂 1. 초기화", ["init"]),
            ("🖥️ 바탕화면 정리", ["clean-desktop"]),
            ("⬇️ 다운로드 정리", ["clean-downloads"]),
            ("📊 결과 확인", ["status"]),
            ("↩️ 작업 실행취소", ["undo"])
        ]
        
        for idx, (text, cmd) in enumerate(actions):
            btn = ctk.CTkButton(btn_frame, text=text, command=lambda c=cmd: self.run_command(c), width=120)
            btn.grid(row=1, column=idx, padx=5, pady=(0, 15))
            self.colored_buttons.append(btn)
            
        settings_btn = ctk.CTkButton(
            btn_frame, text="⚙️ 분류 규칙 설정", 
            command=self.open_settings, 
            width=120, 
            fg_color="transparent", 
            border_width=2, 
            text_color=("gray10", "#DCE4EE")
        )
        settings_btn.grid(row=1, column=5, padx=5, pady=(0, 15))
        
        # 특정 폴더 선택 프레임
        custom_frame = ctk.CTkFrame(self)
        custom_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(custom_frame, text="🎯 특정 폴더 선택하여 정리", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5), columnspan=3)
        
        self.path_var = ctk.StringVar()
        path_entry = ctk.CTkEntry(custom_frame, textvariable=self.path_var, width=450, placeholder_text="폴더 경로를 입력하거나 찾아보기를 누르세요...")
        path_entry.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        
        browse_btn = ctk.CTkButton(custom_frame, text="폴더 찾아보기...", command=self.browse_folder, width=120)
        browse_btn.grid(row=1, column=1, padx=5, pady=5)
        self.colored_buttons.append(browse_btn)
        
        self.in_place_var = ctk.BooleanVar(value=False)
        in_place_check = ctk.CTkCheckBox(custom_frame, text="폴더 내부에서 자체 정리하기 (정리함으로 보내지 않음)", variable=self.in_place_var)
        in_place_check.grid(row=2, column=0, padx=10, pady=10, sticky="w", columnspan=2)
        
        action_subframe = ctk.CTkFrame(custom_frame, fg_color="transparent")
        action_subframe.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))
        
        preview_btn = ctk.CTkButton(action_subframe, text="🔍 미리보기 (안전 모드)", command=lambda: self.run_sort(True), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        preview_btn.pack(side="left", padx=5)
        
        run_btn = ctk.CTkButton(action_subframe, text="🚀 선택 폴더 정리 시작", command=lambda: self.run_sort(False))
        run_btn.pack(side="left", padx=5)
        self.colored_buttons.append(run_btn)
        
        # 하단 출력 프레임
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(log_frame, text="터미널 로그", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, state='disabled', font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # 하단 상태창
        self.status_var = ctk.StringVar(value="대기 중...")
        status_label = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", font=ctk.CTkFont(size=11))
        status_label.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="ew")

    def apply_color_theme(self, color_theme):
        # 동적으로 색상 강제 적용 (customtkinter의 한계 보완)
        if color_theme == "blue":
            fg = ["#3a7ebf", "#1f538d"]
            hover = ["#325882", "#14375e"]
        elif color_theme == "green":
            fg = ["#2CC985", "#2FA572"]
            hover = ["#0C955A", "#106A43"]
            
        for btn in self.colored_buttons:
            btn.configure(fg_color=fg, hover_color=hover)
            
        self.theme_option_menu.configure(fg_color=fg, button_color=hover, button_hover_color=fg)

    def change_theme(self, choice):
        if choice == "모던 다크 모드 (글래스 블루/퍼플 테마)":
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme("blue")
            self.apply_color_theme("blue")
            self.configure(fg_color=("gray92", "gray14")) # Re-trigger background update
        elif choice == "라이트 Fluent 디자인 (윈도우 11 느낌)":
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")
            self.apply_color_theme("blue")
            self.configure(fg_color=("gray92", "gray14"))
        elif choice == "전문가용 하이테크 대시보드 (네온 그린/민트 테마)":
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme("green")
            self.apply_color_theme("green")
            self.configure(fg_color=("#1a1a1a", "#0d0d0d")) # Slightly darker background for tech theme
            
        self.append_log(f"🎨 테마 변경 완료: {choice}")
    def append_log(self, text):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="정리할 폴더를 선택하세요")
        if folder_selected:
            # 윈도우 경로 구분자 정규화
            self.path_var.set(os.path.normpath(folder_selected))

    def open_settings(self):
        try:
            from organizer.settings_gui import open_settings_dialog
            open_settings_dialog(self)
        except Exception as e:
            messagebox.showerror("오류", f"설정 창을 열 수 없습니다:\n{e}")

    def run_sort(self, dry_run=False):
        folder = self.path_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("경고", "먼저 유효한 폴더를 선택해주세요!")
            return
            
        args = ["sort", "--source", folder]
        if dry_run:
            args.append("--dry-run")
        if self.in_place_var.get():
            args.append("--in-place")
        self.run_command(args)

    def _execute_in_thread(self, command_args):
        try:
            if getattr(sys, 'frozen', False):
                cmd = [sys.executable, "--cli"] + command_args
            else:
                cmd = [sys.executable, str(BASE_DIR / "organizer.py")] + command_args
            
            # rich 라이브러리의 ANSI 색상 코드 출력을 방지하여 깔끔한 텍스트만 가져오기 위함
            env = os.environ.copy()
            env["NO_COLOR"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                env=env,
                # Create no window flag on Windows (prevents blank console popup)
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.after(0, self.append_log, line.rstrip())
                
            process.wait()
            self.after(0, self.status_var.set, f"명령어 완료: {' '.join(command_args)}")
            self.after(0, lambda: self.append_log("-" * 40))
        except Exception as e:
            self.after(0, self.append_log, f"\n오류 발생: {e}")
            self.after(0, self.status_var.set, "실행 중 오류 발생")

    def run_command(self, args):
        self.append_log(f"\n▶ 준비 중... : {' '.join(args)}")
        self.status_var.set(f"실행 중... : {' '.join(args)}")
        
        # 백그라운드 스레드에서 실행하여 UI 멈춤 방지
        thread = threading.Thread(target=self._execute_in_thread, args=(args,))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    if getattr(sys, 'frozen', False) and len(sys.argv) > 1 and sys.argv[1] == "--cli":
        import organizer
        sys.argv.pop(1)  # Remove '--cli'
        organizer.cli.main(args=sys.argv[1:], prog_name="폴더정리_자동화")
        sys.exit(0)
        
    app = OrganizerGUI()
    app.mainloop()
