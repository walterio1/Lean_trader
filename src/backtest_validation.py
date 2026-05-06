import json
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    # Choose groups of series to plot together
    vectors2plot = [["VIX Slope - Value 1", "VIX Slope - Value 2", "VIX Slope - State"], ["SMA", "price"]]

    # Load result.json
    with open("custom-data_buy-sma/backtests/2026-05-06_23-23-19/1864429098.json") as f:
        data = json.load(f)

    # Extract all series under SMA Chart
    chart = data.get("charts", {}).get("SMA Chart", {}).get("series", {})
    if not chart:
        raise ValueError("No series found under 'SMA Chart' in the result file")

    def get_series_points(series_values):
        points = [(datetime.fromtimestamp(point[0]), point[1]) for point in series_values]
        x = [point[0] for point in points]
        y = [point[1] for point in points]
        return x, y

    for group_index, group_tokens in enumerate(vectors2plot, start=1):
        group_series = []
        group_label = ", ".join(group_tokens)

        for series_name, series_data in chart.items():
            series_name_lower = series_name.lower()
            if any(token.lower() in series_name_lower for token in group_tokens):
                values = series_data.get("values", [])
                if not values:
                    continue
                group_series.append((series_name, values))

        if not group_series:
            continue

        plt.figure(figsize=(12, 6))
        for series_name, values in group_series:
            x, y = get_series_points(values)
            plt.plot(x, y, label=series_name)

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        plt.title(f"SMA Chart - Group {group_index}: {group_label}")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()