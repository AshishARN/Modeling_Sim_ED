# environment_setup.py
import simpy
import random
from process import patient_lifecycle
from config import *

def setup_ed(env, results_log):
    """Sets up resources for the Emergency Department simulation."""
    resources = {
        'registration_desk': simpy.Resource(env, capacity=REGISTRATION_DESKS_CAPACITY),
        'triage_nurse': simpy.Resource(env, capacity=TRIAGE_CAPACITY),
        'doctor': simpy.Resource(env, capacity=DOCTORS_CAPACITY),
        'lab': simpy.Resource(env, capacity=LAB_CAPACITY),
        'radiology': simpy.Resource(env, capacity=RADIOLOGY_CAPACITY),
    }

    i = 0
    while True:
        # Patients arrive exponentially distributed
        yield env.timeout(random.expovariate(1.0 / PATIENT_INTERARRIVAL_TIME))
        i += 1
        env.process(patient_lifecycle(env, f"Patient-{i}", resources, results_log))
