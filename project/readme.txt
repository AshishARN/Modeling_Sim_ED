🏥 Emergency Department (ED) Simulation Project — Full Guide

This project models patient flow in a hospital emergency department (ED) using Discrete Event Simulation (DES) with SimPy.
It captures realistic queueing, patient routing, and resource bottlenecks based on the Al-Zahraa Hospital study.

⚙️ Project Purpose

The goal is to simulate, analyze, and optimize hospital workflow through five structured steps:

Step	Objective
Step 1:	Build data-logging patient flow simulation
Step 2:	Establish reliable baseline via replication
Step 3:	Validate with queuing-theory variance test
Step 4:	Run “what-if” scenarios (staffing & stress)
Step 5:	Visualize results and produce managerial insights
📁 File-by-File Explanation
1️⃣ config.py

Central configuration file for all parameters.

Contains simulation mode (test / full), experiment mode (variance, staffing, stress, analysis),
and all constants (interarrival times, service distributions, staff counts, etc.).

Changing these values controls the entire simulation behavior.

Key settings:

SIM_MODE = "full"         # "test" (quick) or "full" (2-day run)
EXPERIMENT_MODE = None    # "variance" | "staffing" | "stress" | "analysis"

2️⃣ patient.py

Defines the Patient class.

Each patient stores:

timestamps → when they start each process

wait_times → how long they waited at each stage

Ensures every patient logs 5 stages (Registration, Triage, Doctor, Lab, Radiology) so no NaN values appear.

3️⃣ process.py

Core SimPy process logic describing each patient’s journey.

Uses random distributions for service times (Uniform, Triangular, Exponential).

Handles queues automatically with:

with resource.request() as req:
    yield req
    wait = env.now - t_in
    patient.record_wait(stage, wait)
    yield env.timeout(service_time)


Determines patient type (PICU, ICU, CCU, Non-critical) and optional lab/radiology routing.

4️⃣ environment_setup.py

Builds the simulation environment and resources (doctors, nurses, lab techs, etc.).

Generates a limited number of patients (NUM_PATIENTS from config.py) instead of infinite arrivals.

Starts each patient process at exponentially distributed arrival times.

5️⃣ runner.py

Manages execution and replications:

run_single_simulation() → runs one SimPy environment

run_replications() → repeats multiple runs (e.g., 30) for stable averages

Returns a combined list of all patients’ records for analysis.

6️⃣ experiments.py

Implements Step 3 & 4 experiments automatically.

Variance Experiment (Step 3):
Compares uniform vs exponential doctor service time → tests queuing theory.

Staffing Experiment (Step 4A):
Runs scenarios with 3, 4, 5 doctors to find optimal capacity.

Stress Test (Step 4B):
Varies patient arrival rate (20 → 12 min) to identify system saturation point.

Each experiment runs multiple replications and saves results to CSV files:

results_variance_experiment.csv
results_staffing_experiment.csv
results_stress_experiment.csv

7️⃣ results_analysis.py

Implements Step 5 – Visualization and Reporting.

Reads CSV outputs and computes averages.

Provides quick plotting functions:

Bar chart → Doctor count vs Wait

Line chart → Interarrival vs Total Wait (hockey-stick curve)

Box plot → Doctor wait by patient type

Example:

python -c "import results_analysis as ra; ra.plot_bar_staffing()"

8️⃣ main.py

The entry point for running everything.

Reads EXPERIMENT_MODE from config.py and routes accordingly:

if EXPERIMENT_MODE == "variance":
    experiments.run_variance_experiment()
elif EXPERIMENT_MODE == "staffing":
    experiments.run_staffing_experiment()
elif EXPERIMENT_MODE == "stress":
    experiments.run_stress_experiment()
else:
    results = run_replications()


Saves output CSVs and prints summary statistics.

🧠 How the Files Align (Flow Diagram)
config.py  →  environment_setup.py
              ↓
patient.py   process.py
     ↘         ↙
       runner.py  →  experiments.py
             ↓
       results_analysis.py
             ↓
           main.py


Flow Meaning:

main.py starts the simulation using configs.

runner.py launches patient processes defined in process.py.

patient.py tracks each patient’s timestamps.

environment_setup.py creates resources and spawns patients.

Results saved → experiments.py runs experiments.

results_analysis.py reads & visualizes outputs.