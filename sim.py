import simpy
import numpy as np
import random

# --- 1. Define Model Parameters based on Research Paper ---
# Source: "Modeling and simulation of patient flow at the emergency services: 
#          Case of Al-Zahraa Hospital University Medical Center in Lebanon"

RANDOM_SEED = 42
SIMULATION_TIME = 24 * 60  # Simulate for 24 hours

# Patient arrival parameters from paper
PATIENT_INTERARRIVAL_TIME = 24.0  # Mean time between arrivals is 24 minutes

# Service time parameters from paper (min, mode, max OR min, max)
REGISTRATION_TIME = (3, 10)         # Uniform(3, 10)
TRIAGE_TIME = (5, 10, 15)           # Triangular(5, 10, 15)
FIRST_AID_PICU_TIME = (10, 45)      # Uniform(10, 45) for Pediatric
FIRST_AID_ICU_TIME = (20, 60)       # Uniform(20, 60) for Intensive Care
FIRST_AID_CCU_TIME = (30, 90)       # Uniform(30, 90) for Cardiac Care
COMPLEMENTARY_TREATMENT_TIME = (10, 60) # Uniform(10, 60) for non-critical cases
LAB_TEST_TIME = (15, 45, 90)        # Triangular(15, 45, 90)
RADIOLOGY_TEST_TIME = (15, 45, 90)  # Triangular(15, 45, 90)

# --- 2. Define Assumptions for System Capacity and Routing ---
# Resource capacities (number of servers)
REGISTRATION_DESKS_CAPACITY = 2
TRIAGE_NURSES_CAPACITY = 2
DOCTORS_CAPACITY = 4
LAB_TECH_CAPACITY = 3
RADIOLOGY_TECH_CAPACITY = 2

# Patient routing probabilities
# Patient type assigned after triage
PROB_PICU = 0.05
PROB_ICU = 0.05
PROB_CCU = 0.05
# The remaining (1 - sum of above) will be non-critical

# Test probabilities after seeing a doctor
PROB_NEED_LAB = 0.30
PROB_NEED_RADIOLOGY = 0.20


# --- 3. The Expanded Patient Process ---
def patient_lifecycle(env, patient_name, resources):
    """Defines the complete journey of a patient through the ED."""
    
    # Unpack resources for easier access
    registration_desk = resources['registration_desk']
    triage_nurse = resources['triage_nurse']
    doctor = resources['doctor']
    lab = resources['lab']
    radiology = resources['radiology']

    print(f"{env.now:7.2f}: Patient '{patient_name}' has arrived.")

    # Step 1: Registration
    with registration_desk.request() as req:
        yield req
        reg_time = random.uniform(*REGISTRATION_TIME)
        yield env.timeout(reg_time)
        print(f"{env.now:7.2f}: Patient '{patient_name}' has finished registration.")

    # Step 2: Triage
    with triage_nurse.request() as req:
        yield req
        triage_time = random.triangular(*TRIAGE_TIME)
        yield env.timeout(triage_time)
        print(f"{env.now:7.2f}: Patient '{patient_name}' has finished triage.")

    # Step 3: Doctor Consultation / First Aid
    with doctor.request() as req:
        yield req
        print(f"{env.now:7.2f}: Patient '{patient_name}' is seeing a doctor.")
        
        # Determine patient type and corresponding treatment time
        patient_type_rand = random.random()
        if patient_type_rand < PROB_PICU:
            treatment_time = random.uniform(*FIRST_AID_PICU_TIME)
            print(f"{env.now:7.2f}: Patient '{patient_name}' is a PICU case.")
        elif patient_type_rand < PROB_PICU + PROB_ICU:
            treatment_time = random.uniform(*FIRST_AID_ICU_TIME)
            print(f"{env.now:7.2f}: Patient '{patient_name}' is an ICU case.")
        elif patient_type_rand < PROB_PICU + PROB_ICU + PROB_CCU:
            treatment_time = random.uniform(*FIRST_AID_CCU_TIME)
            print(f"{env.now:7.2f}: Patient '{patient_name}' is a CCU case.")
        else:
            treatment_time = random.uniform(*COMPLEMENTARY_TREATMENT_TIME)
            print(f"{env.now:7.2f}: Patient '{patient_name}' is a Non-Critical case.")
        
        yield env.timeout(treatment_time)
        print(f"{env.now:7.2f}: Patient '{patient_name}' has finished doctor consultation.")

    # Step 4: Decision for tests and potential tests
    if random.random() < PROB_NEED_LAB:
        with lab.request() as req:
            yield req
            print(f"{env.now:7.2f}: Patient '{patient_name}' is undergoing lab tests.")
            lab_time = random.triangular(*LAB_TEST_TIME)
            yield env.timeout(lab_time)
            print(f"{env.now:7.2f}: Patient '{patient_name}' has finished lab tests.")

    if random.random() < PROB_NEED_RADIOLOGY:
        with radiology.request() as req:
            yield req
            print(f"{env.now:7.2f}: Patient '{patient_name}' is undergoing radiology.")
            rad_time = random.triangular(*RADIOLOGY_TEST_TIME)
            yield env.timeout(rad_time)
            print(f"{env.now:7.2f}: Patient '{patient_name}' has finished radiology.")

    print(f"{env.now:7.2f}: Patient '{patient_name}' has completed their visit and is departing.")


# --- 4. The Setup / Generator Function ---
def setup_ed(env):
    """Creates the ED environment, resources, and a patient generator."""
    
    # Create all the resources
    resources = {
        'registration_desk': simpy.Resource(env, capacity=REGISTRATION_DESKS_CAPACITY),
        'triage_nurse': simpy.Resource(env, capacity=TRIAGE_NURSES_CAPACITY),
        'doctor': simpy.Resource(env, capacity=DOCTORS_CAPACITY),
        'lab': simpy.Resource(env, capacity=LAB_TECH_CAPACITY),
        'radiology': simpy.Resource(env, capacity=RADIOLOGY_TECH_CAPACITY)
    }

    patient_number = 0
    # This loop runs indefinitely, creating patients throughout the simulation
    while True:
        # Create a new patient process
        env.process(patient_lifecycle(env, f"Patient-{patient_number}", resources))

        # Wait for the next patient to arrive
        next_arrival_time = np.random.exponential(PATIENT_INTERARRIVAL_TIME)
        yield env.timeout(next_arrival_time)

        patient_number += 1


# --- 5. Main Execution Block ---
if __name__ == '__main__':
    print("--- Starting ED Simulation based on Al-Zahraa Hospital study ---")
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # Create a SimPy environment
    env = simpy.Environment()

    # Start the setup process
    env.process(setup_ed(env))

    # Run the simulation
    env.run(until=SIMULATION_TIME)

    print(f"\n--- Simulation finished after {SIMULATION_TIME / 60} hours ---")