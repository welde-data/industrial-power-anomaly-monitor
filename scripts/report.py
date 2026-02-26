import pandas as pd
from pathlib import Path

DATA_PATH = "data/readings.csv"
OUT_PATH = Path("public/index.html")

# Thresholds (tune later to your real world)
WARN_CURRENT = 20
CRIT_CURRENT = 25
WARN_TEMP = 70
CRIT_TEMP = 80

def classify_row(row) -> str:
    if row["current"] > CRIT_CURRENT or row["temperature"] > CRIT_TEMP:
        return "CRITICAL"
    if row["current"] > WARN_CURRENT or row["temperature"] > WARN_TEMP:
        return "WARNING"
    return "NORMAL"

def worst_status(status_series: pd.Series) -> str:
    order = {"NORMAL": 0, "WARNING": 1, "CRITICAL": 2}
    inv = {0: "NORMAL", 1: "WARNING", 2: "CRITICAL"}
    return inv[int(status_series.map(order).max())]

def main() -> None:
    df = pd.read_csv(DATA_PATH)

    # Derived power (3-phase approx)
    df["power_kw"] = df["voltage"] * df["current"] * 1.732 / 1000

    # Row-level status
    df["status"] = df.apply(classify_row, axis=1)

    # Equipment-level summary + worst status
    summary = (
        df.groupby("equipment_id")
          .agg(
              status=("status", worst_status),
              current_mean=("current", "mean"),
              current_max=("current", "max"),
              temp_mean=("temperature", "mean"),
              temp_max=("temperature", "max"),
              power_kw_mean=("power_kw", "mean"),
          )
          .round(2)
          .reset_index()
          .sort_values(["status", "equipment_id"], ascending=[False, True])
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUT_PATH.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Equipment Health Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    table {{ border-collapse: collapse; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ text-align: left; background: #f6f6f6; }}
    .NORMAL {{ font-weight: bold; }}
    .WARNING {{ font-weight: bold; }}
    .CRITICAL {{ font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Equipment Health Report</h1>

  <h2>Fleet Summary</h2>
  {summary.to_html(index=False, escape=False)}

  <h2>Latest Readings</h2>
  {df.tail(50).to_html(index=False)}
</body>
</html>
""", encoding="utf-8")

    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
