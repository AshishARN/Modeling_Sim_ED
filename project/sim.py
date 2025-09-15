import simpy
import numpy as np
import random

# --- 1. Define Model Parameters based on Research Paper ---
# (Parameters remain the same)
RANDOM_SEED = 42
SIMULATION_TIME = 24 * 60  # Simulate for 24 hours
PATIENT_INTERARRIVAL_TIME = 24.0
REGISTRATION_TIME = (3, 10)
TRIAGE_TIME = (5, 10, 15)
FIRST_AID_PICU_TIME = (10, 45)
FIRST_AID_ICU_TIME = (20, 60)
FIRST_AID_CCU_TIME = (30, 90)
COMPLEMENTARY_TREATMENT_TIME = (10, 60)
LAB_TEST_TIME = (15, 45, 90)
RADIOLOGY_TEST_TIME = (15, 45, 90)

# --- 2. Define Assumptions for System Capacity and Routing ---
# (Capacities remain the same)
REGISTRATION_DESKS_CAPACITY = 2
TRIAGE_NURSES_CAPACITY = 2
DOCTORS_CAPACITY = 4
LAB_TECH_CAPACITY = 3
RADIOLOGY_TECH_CAPACITY = 2

# (Probabilities remain the same)
PROB_PICU = 0.05
PROB_ICU = 0.05
PROB_CCU = 0.05
PROB_NEED_LAB = 0.30
PROB_NEED_RADIOLOGY = 0.20

# ### NEW ### Define Priority Levels (Lower number is higher priority)
PRIORITY_CRITICAL = 1
PRIORITY_NON_CRITICAL = 2

# --- 3. The Expanded Patient Process ---
def patient_lifecycle(env, patient_name, resources):
    """Defines the complete journey of a patient through the ED with priority."""
    
    # Unpack resources for easier access
    registration_desk = resources['registration_desk']
    triage_nurse = resources['triage_nurse']
    doctor = resources['doctor']
    lab = resources['lab']
    radiology = resources['radiology']

    print(f"{env.now:7.2f}: Patient '{patient_name}' has arrived.")

    # Step 1: Registration (Unchanged)
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

    # ### NEW ### Step 2.5: Assign Priority and Type AFTER Triage
    patient_type_rand = random.random()
    if patient_type_rand < PROB_PICU + PROB_ICU + PROB_CCU:
        patient_priority = PRIORITY_CRITICAL
        print(f"{env.now:7.2f}: Patient '{patient_name}' ASSIGNED PRIORITY: CRITICAL.")
    else:
        patient_priority = PRIORITY_NON_CRITICAL
        print(f"{env.now:7.2f}: Patient '{patient_name}' ASSIGNED PRIORITY: Non-Critical.")

    # Step 3: Doctor Consultation / First Aid
    # ### NEW ### Request a doctor using the assigned priority
    with doctor.request(priority=patient_priority) as req:
        yield req
        print(f"{env.now:7.2f}: Patient '{patient_name}' (Priority {patient_priority}) is seeing a doctor.")
        
        # Determine treatment time based on the type we already assigned
        if patient_priority == PRIORITY_CRITICAL:
            # We can further differentiate within critical cases if needed, but for now we group them
            if patient_type_rand < PROB_PICU:
                treatment_time = random.uniform(*FIRST_AID_PICU_TIME)
            elif patient_type_rand < PROB_PICU + PROB_ICU:
                treatment_time = random.uniform(*FIRST_AID_ICU_TIME)
            else:
                treatment_time = random.uniform(*FIRST_AID_CCU_TIME)
        else: # Non-critical case
            treatment_time = random.uniform(*COMPLEMENTARY_TREATMENT_TIME)
        
        yield env.timeout(treatment_time)
        print(f"{env.now:7.2f}: Patient '{patient_name}' has finished doctor consultation.")

    # Step 4: Tests (Unchanged)
    if random.random() < PROB_NEED_LAB:
        with lab.request() as req:
            yield req
            lab_time = random.triangular(*LAB_TEST_TIME)
            yield env.timeout(lab_time)

    if random.random() < PROB_NEED_RADIOLOGY:
        with radiology.request() as req:
            yield req
            rad_time = random.triangular(*RADIOLOGY_TEST_TIME)
            yield env.timeout(rad_time)

    print(f"{env.now:7.2f}: Patient '{patient_name}' has completed their visit and is departing.")

# --- 4. The Setup / Generator Function ---
def setup_ed(env):
    """Creates the ED environment, resources, and a patient generator."""
    
    # ### NEW ### Create a PriorityResource for doctors
    resources = {
        'registration_desk': simpy.Resource(env, capacity=REGISTRATION_DESKS_CAPACITY),
        'triage_nurse': simpy.Resource(env, capacity=TRIAGE_NURSES_CAPACITY),
        'doctor': simpy.PriorityResource(env, capacity=DOCTORS_CAPACITY),
        'lab': simpy.Resource(env, capacity=LAB_TECH_CAPACITY),
        'radiology': simpy.Resource(env, capacity=RADIOLOGY_TECH_CAPACITY)
    }

    patient_number = 0
    while True:
        env.process(patient_lifecycle(env, f"Patient-{patient_number}", resources))
        next_arrival_time = np.random.exponential(PATIENT_INTERARRIVAL_TIME)
        yield env.timeout(next_arrival_time)
        patient_number += 1

# --- 5. Main Execution Block ---
if __name__ == '__main__':
    print("--- Starting ED Simulation with PRIORITY QUEUING ---")
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    env = simpy.Environment()
    env.process(setup_ed(env))
    env.run(until=SIMULATION_TIME)

    print(f"\n--- Simulation finished after {SIMULATION_TIME / 60} hours ---")