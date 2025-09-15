import simpy
import numpy as np

# --- 1. Define Model Parameters ---
RANDOM_SEED = 42
SIMULATION_TIME = 60      # Simulate for 60 minutes (1 hour)

# Resource parameters
NURSE_CAPACITY = 1        # There is only one triage nurse

# Patient arrival parameters
PATIENT_ARRIVAL_RATE = 10  # Average 10 patients per hour
# We need to convert this to minutes for our simulation time unit
# Time between arrivals = 60 mins / 10 patients = 6 mins/patient
PATIENT_INTERARRIVAL_TIME = 60.0 / PATIENT_ARRIVAL_RATE

# Patient process parameters
DESIRED_TRIAGE_MEAN_TIME = 5.0    # Average time for a triage assessment is 5 minutes
MINIMUM_TRIAGE_TIME = 1.0 # The "shift" value

# Calculate the mean for the underlying exponential distribution
EXP_MEAN_TIME = DESIRED_TRIAGE_MEAN_TIME - MINIMUM_TRIAGE_TIME

# --- 2. The Patient Process ---
# This function defines the lifecycle of a patient in our simulation.
# It's a Python "generator function" which can be paused and resumed by SimPy.
def patient_lifecycle(env, patient_name, triage_nurse):
    """A patient arrives, requests a nurse, gets triaged, and leaves."""
    
    print(f"{env.now:.2f}: Patient '{patient_name}' has arrived in the ED.")

    # Request a triage nurse. The 'with' statement is a neat way to handle this.
    # SimPy ensures the patient will wait here until a nurse is free.
    # It automatically requests the resource and releases it when the block is exited.
    with triage_nurse.request() as req:
        yield req  # Wait for the request to be granted (i.e., for the nurse to be free)

        # The patient has now acquired the nurse
        print(f"{env.now:.2f}: Patient '{patient_name}' is being seen by the triage nurse.")

        # Simulate the triage process time
        # We use numpy.random.exponential to model variability in service time
        triage_time = np.random.exponential(EXP_MEAN_TIME) + MINIMUM_TRIAGE_TIME
        yield env.timeout(triage_time) # "Wait" for the triage duration to pass

        print(f"{env.now:.2f}: Patient '{patient_name}' has finished triage and is leaving.")
    
    # The 'with' block automatically releases the nurse here.

# --- 3. The Setup / Generator Function ---
# This function sets up the simulation and creates new patients over time.
def setup_ed(env, nurse_capacity, arrival_interval):
    """Creates the ED environment and a patient generator."""
    
    # Create the resource for the triage nurse(s)
    triage_nurse = simpy.Resource(env, capacity=nurse_capacity)

    patient_number = 0
    # This loop runs indefinitely, creating patients throughout the simulation
    while True:
        # Create a new patient process
        # env.process() tells SimPy to start running this new lifecycle
        env.process(patient_lifecycle(env, f"Patient {patient_number}", triage_nurse))

        # Wait for the next patient to arrive
        # We model arrivals with an exponential distribution (hallmark of a Poisson process)
        next_arrival_time = np.random.exponential(arrival_interval)
        yield env.timeout(next_arrival_time)

        patient_number += 1

# --- 4. Main Execution Block ---
if __name__ == '__main__':
    print("--- Starting Emergency Department Triage Simulation ---")
    np.random.seed(RANDOM_SEED)  # Set the random seed for reproducibility

    # Create a SimPy environment
    env = simpy.Environment()

    # Start the setup process
    env.process(setup_ed(env, NURSE_CAPACITY, PATIENT_INTERARRIVAL_TIME))

    # Run the simulation for a set amount of time
    env.run(until=SIMULATION_TIME)

    print("\n--- Simulation Finished ---")