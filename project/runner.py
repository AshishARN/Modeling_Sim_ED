# runner.py
import simpy
import random
import numpy as np
from environment_setup import setup_ed
from config import SIMULATION_TIME, RANDOM_SEED, SIM_MODE

def run_single_simulation(seed, sim_time=None):
    """Run a single simulation run."""
    random.seed(seed)
    np.random.seed(seed)
    env = simpy.Environment()
    results_log = []
    env.process(setup_ed(env, results_log))

    # Default simulation time based on mode
    sim_time = sim_time or SIMULATION_TIME

    print(f"Running {SIM_MODE.upper()} simulation for {sim_time} minutes with seed {seed}")
    env.run(until=sim_time)
    return results_log

def run_replications(n_replications=5 if SIM_MODE == "test" else 30):
    """Run multiple replications for stability."""
    all_results = []
    for i in range(n_replications):
        run_data = run_single_simulation(RANDOM_SEED + i)
        all_results.append(run_data)
    return [p for run in all_results for p in run]
