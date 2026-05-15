import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import os
from pathlib import Path

from organizer.version import __version__

try:
    import organizer.settings_gui
except ImportError:
    pass

# 현재 스크립트 위치 저장
BASE_DIR = Path(__file__).parent.resolve()

# 초기 테마 설정
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class HelpWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📖 도움말 — 폴더 정리 자동화")
        self.geometry("620x520")
        self.resizable(False, False)
        self.grab_set()
        self.lift()
        self.focus_force()

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=16, pady=16)

        self._build_quickstart(tabs.add("🚀 빠른 시작"))
        self._build_buttons(tabs.add("🔘 버튼 안내"))
        self._build_rules(tabs.add("📋 분류 규칙"))
        self._build_settings(tabs.add("⚙️ 설정 안내"))

        ctk.CTkButton(self, text="닫기", command=self.destroy, width=100).pack(pady=(0, 12))

    # ── 탭 내용 ──────────────────────────────────────────────

    def _build_quickstart(self, frame):
        items = [
            ("1️⃣  초기화",         "처음 사용 시 [📂 1. 초기화]를 눌러\n~/Documents/정리함/ 폴더 구조를 생성하세요."),
            ("2️⃣  미리보기 확인",   "[🔍 미리보기 (안전 모드)]로 파일이 어디로\n이동될지 먼저 확인할 수 있습니다. 실제 이동은 없습니다."),
            ("3️⃣  정리 실행",       "폴더를 선택하거나 단축 버튼으로 정리를 시작합니다.\n파일은 정리함 안 연도별·주제별 폴더로 이동됩니다."),
            ("4️⃣  결과 확인",       "[📊 결과 확인]으로 정리함 현황과\n바탕화면·다운로드 상태를 확인하세요."),
            ("5️⃣  실행취소",        "이동이 잘못됐다면 [↩️ 작업 실행취소]로\n마지막 정리 작업 전체를 되돌릴 수 있습니다."),
        ]
        sf = ctk.CTkScrollableFrame(frame)
        sf.pack(fill="both", expand=True)
        for title, desc in items:
            ctk.CTkLabel(sf, text=title, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(10, 0))
            ctk.CTkLabel(sf, text=desc, anchor="w", justify="left", wraplength=540).pack(fill="x", padx=24, pady=(0, 4))

    def _build_buttons(self, frame):
        rows = [
            ("📂 1. 초기화",           "~/Documents/정리함/ 아래 연도별·주제별 폴더 구조를 생성합니다.\n바탕화면에 바로가기도 함께 만들어집니다."),
            ("🖥️ 바탕화면 정리",       "바탕화면의 파일을 규칙에 따라 정리함으로 이동합니다."),
            ("⬇️ 다운로드 정리",       "다운로드 폴더에서 7일 이상 된 파일을 정리합니다.\n(--days 옵션은 CLI에서 변경 가능)"),
            ("📊 결과 확인",            "정리함 폴더별 파일 수·용량, 바탕화면·다운로드 현황을 출력합니다."),
            ("↩️ 작업 실행취소",        "가장 최근 정리 작업을 취소하고 파일을 원래 위치로 복구합니다.\n이력은 ~/.organizer/history.json 에 저장됩니다."),
            ("⚙️ 분류 규칙 설정",       "config.yaml을 GUI에서 편집할 수 있는 설정 창을 엽니다."),
            ("🎯 특정 폴더 선택",       "정리할 폴더를 직접 지정합니다.\n'폴더 내부에서 자체 정리' 옵션 체크 시 정리함이 아닌\n해당 폴더 내부에서만 파일을 재배치합니다."),
            ("🔍 미리보기 (안전 모드)", "선택된 폴더 기준 dry-run을 실행합니다.\n실제 파일은 이동되지 않으며 예정 결과만 로그에 표시됩니다."),
        ]
        sf = ctk.CTkScrollableFrame(frame)
        sf.pack(fill="both", expand=True)
        for btn_name, desc in rows:
            ctk.CTkLabel(sf, text=btn_name, font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(10, 0))
            ctk.CTkLabel(sf, text=desc, anchor="w", justify="left", wraplength=540).pack(fill="x", padx=24, pady=(0, 4))

    def _build_rules(self, frame):
        content = (
            "파일은 두 단계로 분류됩니다.\n\n"
            "① 연도 폴더\n"
            "  파일의 마지막 수정 날짜(mtime)를 기준으로 연도 폴더에 배치됩니다.\n"
            "  설정의 archive_before 연도보다 오래된 파일은 _Archive/ 로 이동합니다.\n\n"
            "② 주제 폴더\n"
            "  config.yaml 의 rules 목록을 위에서 아래 순서로 확인합니다.\n"
            "  확장자(extensions)를 먼저 비교하고, 그 다음 파일명 키워드(keywords)를 확인합니다.\n"
            "  두 조건 모두 매칭되지 않으면 default_destination 폴더로 이동합니다.\n\n"
            "건너뛰는 파일\n"
            "  • 바탕화면 바로가기 (.lnk, .alias)\n"
            "  • 숨김 파일 (파일명이 . 으로 시작)\n"
            "  • 심볼릭 링크, 디렉토리\n"
            "  • 로컬에 내려받히지 않은 OneDrive 클라우드 파일\n\n"
            "정리함 구조 예시\n"
            "  ~/Documents/정리함/\n"
            "    2026년/\n"
            "      01_학교업무/생기부·세특/\n"
            "      02_개발·IT/웹개발_프로젝트/\n"
            "      04_참고자료/이미지·영상/\n"
            "    _Archive/  ← archive_before 이전 파일"
        )
        sf = ctk.CTkScrollableFrame(frame)
        sf.pack(fill="both", expand=True)
        ctk.CTkLabel(sf, text=content, anchor="w", justify="left", wraplength=560,
                     font=ctk.CTkFont(family="Consolas", size=12)).pack(padx=12, pady=10, fill="x")

    def _build_settings(self, frame):
        content = (
            "설정 파일 위치\n"
            "  프로그램 폴더의 config.yaml 을 우선 사용하며,\n"
            "  없으면 ~/.organizer/config.yaml 을 자동으로 생성합니다.\n\n"
            "주요 항목\n\n"
            "  root\n"
            "    정리함의 루트 경로입니다.\n"
            "    기본값: ~/Documents/정리함\n\n"
            "  archive_before\n"
            "    이 연도 미만의 파일은 _Archive/ 로 이동합니다.\n"
            "    기본값: 2024\n\n"
            "  default_destination\n"
            "    어떤 규칙에도 매칭되지 않은 파일의 기본 목적지입니다.\n"
            "    기본값: 04_참고자료/다운로드_정리\n\n"
            "  rules  (위에서 아래 순서로 우선순위 적용)\n"
            "    - name: 01_학교업무/생기부·세특   ← 정리함 내 하위 폴더 경로\n"
            "      keywords: [세특, 생기부]         ← 파일명에 포함된 단어\n"
            "      extensions: [.docx, .hwp]        ← 파일 확장자\n\n"
            "규칙 편집\n"
            "  [⚙️ 분류 규칙 설정] 버튼으로 GUI 편집 창을 열거나,\n"
            "  텍스트 편집기로 config.yaml 을 직접 수정할 수 있습니다."
        )
        sf = ctk.CTkScrollableFrame(frame)
        sf.pack(fill="both", expand=True)
        ctk.CTkLabel(sf, text=content, anchor="w", justify="left", wraplength=560,
                     font=ctk.CTkFont(family="Consolas", size=12)).pack(padx=12, pady=10, fill="x")


class OrganizerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"📁 폴더 정리 자동화 v{__version__}")
        self.geometry("750x620")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)  # log_frame

        self._update_frame = None  # 업데이트 배너 (숨김 상태로 시작)

        self.setup_ui()
        self._schedule_update_check()

    def setup_ui(self):
        # 상단 설정 바 (테마 선택 영역 포함)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(header_frame, text="✨ Folder Organizer", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")

        help_btn = ctk.CTkButton(
            header_frame, text="❓ 도움말", command=self.open_help,
            width=90, fg_color="transparent", border_width=1,
            text_color=("gray10", "#DCE4EE")
        )
        help_btn.grid(row=0, column=1, sticky="e", padx=(0, 8))

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
        theme_menu.grid(row=0, column=2, sticky="e")
        
        self.colored_buttons = []
        self.theme_option_menu = theme_menu

        # 업데이트 배너 (row 1, 초기에는 숨김)
        self._update_frame = ctk.CTkFrame(self, fg_color=("#d4edda", "#1e3a2a"), corner_radius=8)
        self._update_label = ctk.CTkLabel(self._update_frame, text="", anchor="w")
        self._update_label.pack(side="left", padx=12, pady=6, fill="x", expand=True)
        self._update_btn = ctk.CTkButton(self._update_frame, text="업데이트", width=90,
                                          fg_color="#28a745", hover_color="#1e7e34",
                                          command=self._start_update)
        self._update_btn.pack(side="right", padx=(0, 6), pady=6)
        dismiss_btn = ctk.CTkButton(self._update_frame, text="✕", width=30,
                                     fg_color="transparent", border_width=0,
                                     command=lambda: self._update_frame.grid_remove())
        dismiss_btn.pack(side="right", padx=0, pady=6)
        # 배너는 그리드에 추가하되 숨겨 둠
        self._update_frame.grid(row=1, column=0, padx=20, pady=(0, 4), sticky="ew")
        self._update_frame.grid_remove()

        # 단축 버튼 프레임
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
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
        custom_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
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
        log_frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(log_frame, text="터미널 로그", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, state='disabled', font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # 하단 상태창
        self.status_var = ctk.StringVar(value="대기 중...")
        status_label = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", font=ctk.CTkFont(size=11))
        status_label.grid(row=5, column=0, padx=20, pady=(0, 5), sticky="ew")

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

    def open_help(self):
        HelpWindow(self)

    def _schedule_update_check(self):
        try:
            from organizer.updater import check_for_updates
            check_for_updates(self._on_update_found)
        except Exception:
            pass

    def _on_update_found(self, tag: str, download_url: str):
        self._pending_download_url = download_url
        self.after(0, self._show_update_banner, tag)

    def _show_update_banner(self, tag: str):
        self._update_label.configure(text=f"🔄 새 버전 {tag} 업데이트가 있습니다!")
        self._update_frame.grid()

    def _start_update(self):
        url = getattr(self, "_pending_download_url", None)
        if not url:
            return
        if not getattr(sys, "frozen", False):
            messagebox.showinfo("업데이트", "개발 환경에서는 자동 업데이트가 지원되지 않습니다.\n직접 최신 버전을 받아 주세요.")
            return
        self._update_btn.configure(state="disabled", text="다운로드 중...")
        def _do():
            try:
                from organizer.updater import download_and_update
                def _progress(p):
                    self.after(0, self._update_btn.configure, {"text": f"{int(p*100)}%"})
                download_and_update(url, _progress)
            except Exception as e:
                self.after(0, messagebox.showerror, "업데이트 실패", str(e))
                self.after(0, self._update_btn.configure, {"state": "normal", "text": "업데이트"})
        threading.Thread(target=_do, daemon=True).start()

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
        # cli 는 organizer 패키지(organizer/cli.py) 안에 정의되어 있으므로
        # organizer.py 스크립트와의 이름 충돌 없이 안전하게 import 가능하다.
        from organizer.cli import cli
        sys.argv.pop(1)  # Remove '--cli'
        cli.main(args=sys.argv[1:], prog_name="폴더정리_자동화")
        sys.exit(0)
        
    app = OrganizerGUI()
    app.mainloop()
