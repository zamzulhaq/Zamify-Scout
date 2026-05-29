import pandas as pd
from rich.panel import Panel
from ui.terminal_theme import sentinel_theme
from rich.console import Console

console = Console(theme=sentinel_theme)

class MarketAnalyzer:
    @staticmethod
    def analyze(keyword: str, data: list, platform_statuses: dict = None):
        platform_statuses = platform_statuses or {}
        
        status_lines = []
        platforms = list(platform_statuses.keys()) or sorted(
            {str(item.get("platform", "tokopedia")).lower() for item in data}
        ) or ["tokopedia"]

        for plat in platforms:
            status = platform_statuses.get(plat, "success")
            if status == "blocked":
                status_lines.append(f"{plat.title()}:\n  blocked")
            else:
                count = sum(1 for d in data if d.get("platform", "").lower() == plat) if data else 0
                status_lines.append(f"{plat.title()}:\n  {count} products")
        
        status_text = "\n\n".join(status_lines)
        
        if not data:
            console.print("[error]No data to analyze.[/error]")
            report = (
                f"[info]Keyword:[/info] {keyword}\n\n"
                f"[info]Platform Status:[/info]\n{status_text}\n\n"
                f"[warning]Analysis skipped due to lack of data.[/warning]"
            )
            console.print(Panel(report, title="[bold accent]MULTI-PLATFORM MARKET ANALYSIS REPORT[/bold accent]", border_style="accent"))
            return
            
        df = pd.DataFrame(data)
        
        # Overall metrics
        avg_price = df['price'].mean()
        min_price = df['price'].min()
        max_price = df['price'].max()
        
        # Platform metrics
        platform_counts = df['platform'].value_counts()
        most_active_platform = platform_counts.idxmax().title() if not platform_counts.empty else "N/A"
        
        # Group by platform for price insights
        avg_by_platform = df.groupby('platform')['price'].mean()
        cheapest_platform = avg_by_platform.idxmin().title() if not avg_by_platform.empty else "N/A"
        
        # Determine trend insight
        if avg_price > 100000:
            trend = f"Premium {keyword} market. Good margin potential."
        else:
            trend = f"Mass market for {keyword}. Compete on volume."
            
        rec_min = int(avg_price * 0.9)
        rec_max = int(avg_price * 1.1)
        
        report = (
            f"[info]Keyword:[/info] {keyword}\n\n"
            f"[info]Platform Status:[/info]\n{status_text}\n\n"
            f"[info]Overall Market:[/info]\n"
            f"  Average Price: Rp{int(avg_price):,}\n"
            f"  Lowest Price: Rp{int(min_price):,}\n"
            f"  Highest Price: Rp{int(max_price):,}\n\n"
            f"[info]Platform Comparison:[/info]\n"
            f"  Most Active Platform: {most_active_platform}\n"
            f"  Cheapest Platform (Avg): {cheapest_platform}\n\n"
            f"[info]Recommendation:[/info]\n"
        )
        
        report += (
            f"  Trend: {trend}\n"
            f"  Price: Rp{rec_min:,} - Rp{rec_max:,}"
        )
        
        console.print(Panel(report, title="[bold accent]MULTI-PLATFORM MARKET ANALYSIS REPORT[/bold accent]", border_style="accent"))
