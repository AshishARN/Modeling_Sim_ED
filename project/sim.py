import simpy
import numpy as np
import random

# --- 1. Define Model Parameters based on Research Paper ---
# (Parameters remain the same)
RANDOM_SEED = 42
SIMULATION_TIME = 30 * 24 * 60  # Simulate for 30 days (in minutes)
PATIENT_INTERARRIVAL_TIME = 20.0
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

# ### NEW ### - Data structure to hold patient-specific information
class Patient:
    """ A class to represent a patient and store their journey timestamps. """
    def __init__(self, patient_id):
        self.id = patient_id
        self.priority = PRIORITY_NON_CRITICAL  # Default priority
        self.patient_type = "Non-Critical"     # To store PICU/ICU/CCU etc.
        self.timestamps = {
            'arrival': 0.0,
            'reg_start': 0.0,
            'reg_end': 0.0,
            'triage_start': 0.0,
            'triage_end': 0.0,
            'doc_start': 0.0,
            'doc_end': 0.0,
            'lab_start': 0.0,
            'lab_end': 0.0,
            'rad_start': 0.0,
            'rad_end': 0.0,
            'depart': 0.0,
        }
        self.wait_times = {}

    def record_time(self, event, time):
        """ Records a timestamp for a specific event. """
        self.timestamps[event] = time

    # ### NEW ### - A method to store a calculated wait time
    def record_wait(self, stage, wait_duration):
        """ Records the waiting time for a specific stage. """
        self.wait_times[stage] = wait_duration

# --- 3. The Expanded Patient Process ---
# ### MODIFIED ### - Patient lifecycle now uses the Patient class for data collection
def patient_lifecycle(env, patient, resources, results_log):
    """Defines the journey of a patient, recording timestamps at each step."""

    # Unpack resources
    registration_desk = resources['registration_desk']
    triage_nurse = resources['triage_nurse']
    doctor = resources['doctor']
    lab = resources['lab']
    radiology = resources['radiology']

    # Record arrival time
    patient.record_time('arrival', env.now)

    # Step 1: Registration
    time_enter_reg_q = env.now
    with registration_desk.request() as req:
        yield req
        patient.record_time('reg_start', env.now) # MOVED HERE
        wait_reg = env.now - time_enter_reg_q
        patient.record_wait('registration', wait_reg) # <-- STORE THE WAIT TIME

        reg_time = random.uniform(*REGISTRATION_TIME)
        yield env.timeout(reg_time)
        patient.record_time('reg_end', env.now)

    # Step 2: Triage
    time_enter_triage_q = env.now
    with triage_nurse.request() as req:
        yield req
        patient.record_time('triage_start', env.now)
        wait_triage = env.now - time_enter_triage_q
        patient.record_wait('triage', wait_triage) # <-- STORE THE WAIT TIME

        triage_time = random.triangular(*TRIAGE_TIME)
        yield env.timeout(triage_time)
        patient.record_time('triage_end', env.now)

    # Step 2.5: Assign Priority and Type AFTER Triage
    patient_type_rand = random.random()
    if patient_type_rand < PROB_PICU + PROB_ICU + PROB_CCU:
        patient.priority = PRIORITY_CRITICAL
        # Also store the specific type for more detailed analysis later
        if patient_type_rand < PROB_PICU:
            patient.patient_type = "PICU"
        elif patient_type_rand < PROB_PICU + PROB_ICU:
            patient.patient_type = "ICU"
        else:
            patient.patient_type = "CCU"
    else:
        patient.priority = PRIORITY_NON_CRITICAL # This is the default, but good to be explicit
        patient.patient_type = "Non-Critical"

    # Step 3: Doctor Consultation / First Aid
    time_enter_doc_q = env.now
    with doctor.request(priority=patient.priority) as req:
        yield req
        patient.record_time('doc_start', env.now)
        # We can now calculate the true wait time for the doctor
        wait_doc = env.now - time_enter_doc_q
        patient.record_wait('doctor', wait_doc)
        
        # Determine treatment time
        if patient.priority == PRIORITY_CRITICAL:
            if patient.patient_type == "PICU":
                treatment_time = random.uniform(*FIRST_AID_PICU_TIME)
            elif patient.patient_type == "ICU":
                treatment_time = random.uniform(*FIRST_AID_ICU_TIME)
            else: # CCU
                treatment_time = random.uniform(*FIRST_AID_CCU_TIME)
        else: # Non-critical
            treatment_time = random.uniform(*COMPLEMENTARY_TREATMENT_TIME)
            #treatment_time = np.random.exponential(35.0)
        
        yield env.timeout(treatment_time)
        patient.record_time('doc_end', env.now)

    # Step 4: Tests (run concurrently if both are needed)
    lab_process = None
    rad_process = None

    if random.random() < PROB_NEED_LAB:
        def do_lab():
            time_enter_lab_q = env.now
            with lab.request() as req:
                yield req
                patient.record_time('lab_start', env.now)
                wait_lab = env.now - time_enter_lab_q
                patient.record_wait('lab', wait_lab)

                lab_time = random.triangular(*LAB_TEST_TIME)
                yield env.timeout(lab_time)
                patient.record_time('lab_end', env.now)
        lab_process = env.process(do_lab())

    if random.random() < PROB_NEED_RADIOLOGY:
        def do_rad():
            time_enter_radio_q = env.now
            with radiology.request() as req:
                yield req
                patient.record_time('rad_start', env.now)
                wait_radio = env.now - time_enter_radio_q
                patient.record_wait('radiology', wait_radio)

                rad_time = random.triangular(*RADIOLOGY_TEST_TIME)
                yield env.timeout(rad_time)
                patient.record_time('rad_end', env.now)
        rad_process = env.process(do_rad())
    
    # Wait for both tests to complete if they were started
    if lab_process: yield lab_process
    if rad_process: yield rad_process

    # Record departure time and log the patient's data
    patient.record_time('depart', env.now)
    results_log.append(patient)

# --- 4. The Setup / Generator Function ---
# ### MODIFIED ### - The generator now creates Patient objects
def setup_ed(env, results_log, capacities):
    """Creates the ED environment, resources, and a patient generator."""
    
    resources = {
        'registration_desk': simpy.Resource(env, capacity=capacities['registration_desk']),
        'triage_nurse': simpy.Resource(env, capacity=capacities['triage_nurse']),
        'doctor': simpy.PriorityResource(env, capacity=capacities['doctor']),
        'lab': simpy.Resource(env, capacity=capacities['lab']),
        'radiology': simpy.Resource(env, capacity=capacities['radiology'])
    }

    patient_number = 0
    while True:
        # Create a new Patient object
        patient = Patient(f"Patient-{patient_number}")
        # Pass the patient object and the results log to the lifecycle process
        env.process(patient_lifecycle(env, patient, resources, results_log))
        
        next_arrival_time = np.random.exponential(PATIENT_INTERARRIVAL_TIME)
        yield env.timeout(next_arrival_time)
        patient_number += 1


def run_simulation(capacities, rand_seed=RANDOM_SEED):
    """
    Runs a single simulation with a given set of resource capacities.
    Returns the complete list of patient data objects.
    """
    random.seed(rand_seed)
    np.random.seed(rand_seed)

    results_log = []
    env = simpy.Environment()
    env.process(setup_ed(env, results_log, capacities))
    env.run(until=SIMULATION_TIME)

    # The function now returns the key data structure instead of a calculated metric
    return results_log

# ### MODIFIED ### - Main block now separates simulation from analysis

# if __name__ == '__main__':
#     print("--- Starting ED Simulation with Data Collection ---")
#     random.seed(RANDOM_SEED)
#     np.random.seed(RANDOM_SEED)

#     # This list will hold all the completed patient objects
#     results_log = []

#     env = simpy.Environment()
#     # Pass the results_log list to the setup process
#     env.process(setup_ed(env, results_log))
#     env.run(until=SIMULATION_TIME)

#     print(f"\n--- Simulation finished. Analyzing {len(results_log)} patient records. (for {SIMULATION_TIME/(60*24)} day(s))---")

#     # --- NEW ANALYSIS SECTION ---
#     # We can now collect waits from every stage
#     total_system_times = []
    
#     # Dictionaries to hold the lists of wait times for each stage
#     wait_times_by_stage = {
#         'registration': [],
#         'triage': [],
#         'doctor_crit': [],
#         'doctor_non_crit': [],
#         'lab': [],
#         'radiology': []
#     }
    
#     for p in results_log:
#         # Calculate total time in system (Length of Stay)
#         los = p.timestamps['depart'] - p.timestamps['arrival']
#         total_system_times.append(los)

#         # Append wait times from the patient record
#         wait_times_by_stage['registration'].append(p.wait_times.get('registration', 0))
#         wait_times_by_stage['triage'].append(p.wait_times.get('triage', 0))
#         wait_times_by_stage['lab'].append(p.wait_times.get('lab', 0))
#         wait_times_by_stage['radiology'].append(p.wait_times.get('radiology', 0))

#         # Separate doctor waits by priority
#         if p.priority == PRIORITY_CRITICAL:
#             wait_times_by_stage['doctor_crit'].append(p.wait_times.get('doctor', 0))
#         else:
#             wait_times_by_stage['doctor_non_crit'].append(p.wait_times.get('doctor', 0))

#     # --- Display Results ---
#     print("\n--- Key Performance Indicators ---")
#     print(f"Average Length of Stay: {np.mean(total_system_times):.2f} minutes")
#     print(f"95th Percentile LOS: {np.percentile(total_system_times, 95):.2f} minutes")

#     print("\n--- Average Wait Times by Stage ---")
#     print(f"Registration Queue: {np.mean(wait_times_by_stage['registration']):.2f} minutes")
#     print(f"Triage Queue:       {np.mean(wait_times_by_stage['triage']):.2f} minutes")
#     print(f"Lab Queue:          {np.mean(wait_times_by_stage['lab']):.2f} minutes")
#     print(f"Radiology Queue:    {np.mean(wait_times_by_stage['radiology']):.2f} minutes")
#     print(f"Doctor Queue (Crit):  {np.mean(wait_times_by_stage['doctor_crit']):.2f} minutes")
#     print(f"Doctor Queue (Non-Crit): {np.mean(wait_times_by_stage['doctor_non_crit']):.2f} minutes")


if __name__ == '__main__':
    print("--- Running a single test simulation from sim.py ---")
    
    default_capacities = {
        'registration_desk': 2, 'triage_nurse': 2, 'doctor': 4,
        'lab': 3, 'radiology': 2
    }

    # The function now returns a list of all patient objects
    all_patients_data = run_simulation(default_capacities)
    
    # We must now calculate the LOS from the returned data
    if all_patients_data:
        total_system_times = [
            p.timestamps['depart'] - p.timestamps['arrival'] for p in all_patients_data
        ]
        avg_los_result = np.mean(total_system_times)
    else:
        avg_los_result = 0.0

    print(f"\n--- Test Run Complete ---")
    print(f"Analyzed {len(all_patients_data)} patient records.")
    print(f"Overall Average Length of Stay: {avg_los_result:.2f} minutes")