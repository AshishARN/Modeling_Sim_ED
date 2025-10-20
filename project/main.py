# main.py
import os, sys
# ensure local directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import pandas as pd
from runner import run_replications
from config import SIM_MODE, EXPERIMENT_MODE, SIMULATION_TIME

if __name__ == "__main__":
    print(f"--- Starting ED Simulation ({SIM_MODE.upper()} MODE) ---")
    print(f"Simulation duration: {SIMULATION_TIME} minutes")

    if EXPERIMENT_MODE is None:
        print("Running baseline simulation (Steps 1 & 2)...")
        results = run_replications()
        df = pd.DataFrame(results)
        df.to_csv(f"simulation_results_{SIM_MODE}.csv", index=False)

        print(f"\nSimulation complete! Mode: {SIM_MODE}")
        print(f"Total patients logged: {len(df)}")
        print("Sample Output:\n", df.head())

        # ---------- Step 5: Call analysis from results_analysis ----------
        from results_analysis import analyze_and_plot_baseline
        analyze_and_plot_baseline(df)

    else:
        import experiments
        if EXPERIMENT_MODE == "variance":
            experiments.run_variance_experiment()
        elif EXPERIMENT_MODE == "staffing":
            experiments.run_staffing_experiment()
        elif EXPERIMENT_MODE == "stress":
            experiments.run_stress_experiment()
        else:
            print("Invalid EXPERIMENT_MODE in config.py")
