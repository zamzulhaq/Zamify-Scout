import pandas as pd
from rich.panel import Panel
from ui.terminal_theme import sentinel_theme
from rich.console import Console

console = Console(theme=sentinel_theme)

class MarketAnalyzer:
    @staticmethod
    def analyze(keyword: str, data: list):
        if not data:
            console.print("[error]No data to analyze.[/error]")
            return
            
        df = pd.DataFrame(data)
        
        avg_price = df['price'].mean()
        min_price = df['price'].min()
        max_price = df['price'].max()
        
        # Determine trend insight (mocked logic for MVP based on price)
        if avg_price > 100000:
            trend = f"Premium {keyword} market. Good margin potential."
        else:
            trend = f"Mass market for {keyword}. Compete on volume."
            
        rec_min = int(avg_price * 0.9)
        rec_max = int(avg_price * 1.1)
        
        report = (
            f"[info]Keyword:[/info] {keyword}\n\n"
            f"[info]Average Price:[/info] Rp{int(avg_price):,}\n"
            f"[info]Lowest Price:[/info] Rp{int(min_price):,}\n"
            f"[info]Highest Price:[/info] Rp{int(max_price):,}\n\n"
            f"[info]Most Active Platform:[/info] Tokopedia (Current Default)\n\n"
            f"[info]Trend Insight:[/info]\n{trend}\n\n"
            f"[info]Recommended Selling Price:[/info]\nRp{rec_min:,} - Rp{rec_max:,}"
        )
        
        console.print(Panel(report, title="[bold accent]MARKET ANALYSIS REPORT[/bold accent]", border_style="accent"))
