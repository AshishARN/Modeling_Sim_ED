# main.py
from runner import run_replications
import pandas as pd
from config import SIM_MODE

if __name__ == "__main__":
    print(f"--- Starting ED Simulation ({SIM_MODE.upper()} MODE) ---")
    results = run_replications()
    df = pd.DataFrame(results)
    df.to_csv(f"simulation_results_{SIM_MODE}.csv", index=False)

    print(f"\nSimulation complete! Mode: {SIM_MODE}")
    print(f"Total patients logged: {len(df)}")
    print("Sample Output:\n", df.head())
