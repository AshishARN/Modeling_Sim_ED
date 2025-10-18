# config.py
import numpy as np

# --- Simulation Mode ---
# Choose between: "test" or "full"
SIM_MODE = "full"

# --- Experiment Control ---
# Choose: None | "variance" | "staffing" | "stress" | "analysis"
EXPERIMENT_MODE = None

RANDOM_SEED = 42

# --- Simulation Settings ---
if SIM_MODE == "test":
    SIMULATION_TIME = 8 * 60          # 8 hours
    PATIENT_INTERARRIVAL_TIME = 3.0
    NUM_PATIENTS = 25
else:
    SIMULATION_TIME = 2 * 24 * 60     # 2 days
    PATIENT_INTERARRIVAL_TIME = 10.0
    NUM_PATIENTS = 300                # more data for analysis

# --- Resource Capacities ---
REGISTRATION_DESKS_CAPACITY = 2
TRIAGE_NURSES_CAPACITY = 1
DOCTORS_CAPACITY = 2
LAB_TECH_CAPACITY = 2
RADIOLOGY_TECH_CAPACITY = 1

# --- Probabilities ---
PROB_PICU = 0.05
PROB_ICU = 0.05
PROB_CCU = 0.05
PROB_NEED_LAB = 0.30
PROB_NEED_RADIOLOGY = 0.20

# --- Service Time Distributions ---
REGISTRATION_TIME = (3, 10)
TRIAGE_TIME = (5, 10, 15)
FIRST_AID_PICU_TIME = (10, 45)
FIRST_AID_ICU_TIME = (20, 60)
FIRST_AID_CCU_TIME = (30, 90)
COMPLEMENTARY_TREATMENT_TIME = (10, 60)
LAB_TEST_TIME = (15, 45, 90)
RADIOLOGY_TEST_TIME = (15, 45, 90)
