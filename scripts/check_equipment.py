import pandas as pd
import sys

DATA_PATH = "data/readings.csv"

# Typical sanity limits (adjust later)
MIN_VOLTAGE = 300
MAX_CURRENT = 25
MAX_TEMP = 80

def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)

def main() -> None:
    df = pd.read_csv(DATA_PATH)

    required_cols = {"timestamp", "equipment_id", "voltage", "current", "temperature"}
    missing = required_cols - set(df.columns)
    if missing:
        fail(f"Missing columns: {sorted(missing)}")

    if (df["voltage"] < MIN_VOLTAGE).any():
        fail(f"Voltage below {MIN_VOLTAGE}V detected")

    if (df["current"] < 0).any():
        fail("Negative current detected")

    if (df["temperature"] < -20).any():
        fail("Temperature unrealistically low detected")

    # Derived power (3-phase approx)
    df["power_kw"] = df["voltage"] * df["current"] * 1.732 / 1000

    if (df["current"] > MAX_CURRENT).any():
        fail(f"Overcurrent anomaly detected (> {MAX_CURRENT}A)")

    if (df["temperature"] > MAX_TEMP).any():
        fail(f"Overtemperature anomaly detected (> {MAX_TEMP}°C)")

    print("✅ Equipment operating within normal range")

if __name__ == "__main__":
    main()
