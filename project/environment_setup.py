# environment_setup.py
import simpy
import numpy as np
from process import patient_lifecycle
from config import *

def setup_ed(env, results_log):
    """Create environment, resources, and patient generator."""
    resources = {
        'registration_desk': simpy.Resource(env, REGISTRATION_DESKS_CAPACITY),
        'triage_nurse': simpy.Resource(env, TRIAGE_NURSES_CAPACITY),
        'doctor': simpy.Resource(env, DOCTORS_CAPACITY),
        'lab': simpy.Resource(env, LAB_TECH_CAPACITY),
        'radiology': simpy.Resource(env, RADIOLOGY_TECH_CAPACITY)
    }

    for i in range(NUM_PATIENTS):
        env.process(patient_lifecycle(env, f"Patient-{i}", resources, results_log))
        next_arrival = np.random.exponential(PATIENT_INTERARRIVAL_TIME)
        yield env.timeout(next_arrival)
