import pandas as pd
from pathlib import Path

DATA_PATH = "data/readings.csv"
OUT_PATH = Path("public/index.html")

def main() -> None:
    df = pd.read_csv(DATA_PATH)

    # Derived power (3-phase approx)
    df["power_kw"] = df["voltage"] * df["current"] * 1.732 / 1000

    summary = (
        df.groupby("equipment_id")
          .agg(
              current_mean=("current", "mean"),
              current_max=("current", "max"),
              temp_mean=("temperature", "mean"),
              temp_max=("temperature", "max"),
              power_kw_mean=("power_kw", "mean"),
          )
          .round(2)
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUT_PATH.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Equipment Health Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    table {{ border-collapse: collapse; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>Equipment Health Report</h1>

  <h2>Summary</h2>
  {summary.to_html()}

  <h2>Latest Readings</h2>
  {df.tail(50).to_html(index=False)}
</body>
</html>
""", encoding="utf-8")

    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
