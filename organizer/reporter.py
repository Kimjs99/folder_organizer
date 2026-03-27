from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys

# Windows에서 이모지 출력을 위해 강제로 utf-8 사용 (파이썬 3.7+ 표준 I/O 변경)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

console = Console()

def print_summary(success_count: int, skip_count: int, error_count: int):
    table = Table(title="처리 결과 요약")
    table.add_column("분류", justify="center", style="cyan")
    table.add_column("개수", justify="right", style="magenta")
    
    table.add_row("이동 완료", str(success_count))
    table.add_row("건너뜀", str(skip_count))
    if error_count > 0:
        table.add_row("오류", str(error_count), style="red")
    else:
        table.add_row("오류", str(error_count))
        
    console.print(table)

def print_status(years_stats: dict, desktop_count: int, downloads_count: int, downloads_oldest: str):
    table = Table(title="정리함 상태 리포트")
    table.add_column("연도", justify="center", style="cyan")
    table.add_column("파일 수", justify="right", style="magenta")
    table.add_column("용량", justify="right", style="green")
    
    for year, stats in years_stats.items():
        # stats: {"count": 10, "size": 1024}
        size_mb = stats["size"] / (1024 * 1024)
        if size_mb > 1024:
            size_str = f"{size_mb / 1024:.1f} GB"
        else:
            size_str = f"{size_mb:.1f} MB"
            
        table.add_row(year, str(stats["count"]), size_str)
        
    console.print(table)
    
    status_text = f"바탕화면: {desktop_count}개 항목 | 다운로드: {downloads_count}개 항목 (가장 오래된: {downloads_oldest})"
    console.print(status_text)

def print_success(msg: str):
    console.print(f"[bold green]✅ {msg}[/bold green]")

def print_info(msg: str):
    console.print(f"[bold blue]ℹ️ {msg}[/bold blue]")

def print_preview(src: str, dest: str):
    console.print(f"[yellow][미리보기][/yellow] {src} → {dest}")

def print_error(msg: str):
    console.print(f"[bold red]❌ {msg}[/bold red]")
