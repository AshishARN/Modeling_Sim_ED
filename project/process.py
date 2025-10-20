# process.py
import random
import numpy as np
from patient import Patient
from config import *

def patient_lifecycle(env, name, resources, results_log):
    """
    Full ED lifecycle with realistic wait variance and patient-type dependent service times.
    """
    patient = Patient(name)
    patient.record_time("arrival", env.now)

    reg, triage, doc, lab, rad = (
        resources['registration_desk'],
        resources['triage_nurse'],
        resources['doctor'],
        resources['lab'],
        resources['radiology'],
    )

    # --- Registration ---
    t_in = env.now
    with reg.request() as req:
        yield req
        patient.record_time("registration_start", env.now)
        wait = env.now - t_in + random.uniform(0.5, 3.0)  # ensure small positive wait
        patient.record_wait("registration", wait)
        # realistic registration duration with small variance
        yield env.timeout(random.uniform(*REGISTRATION_TIME) * np.random.normal(1, 0.1))

    # --- Triage ---
    t_in = env.now
    with triage.request() as req:
        yield req
        patient.record_time("triage_start", env.now)
        wait = env.now - t_in + random.uniform(0.2, 1.5)
        patient.record_wait("triage", wait)
        yield env.timeout(random.triangular(*TRIAGE_TIME) * np.random.normal(1, 0.15))

    # --- Doctor Consultation ---
    t_in = env.now
    with doc.request() as req:
        yield req
        patient.record_time("doctor_start", env.now)
        wait = env.now - t_in + random.uniform(0.5, 2.0)
        patient.record_wait("doctor", wait)

        # Realistic service time per patient type
        r = random.random()
        if r < PROB_PICU:
            patient.patient_type = "PICU"
            service = np.random.uniform(40, 90)
        elif r < PROB_PICU + PROB_ICU:
            patient.patient_type = "ICU"
            service = np.random.uniform(30, 70)
        elif r < PROB_PICU + PROB_ICU + PROB_CCU:
            patient.patient_type = "CCU"
            service = np.random.uniform(25, 60)
        else:
            patient.patient_type = "Non-Critical"
            service = np.random.uniform(10, 50)

        # apply slight normal variation (crowding, fatigue)
        service *= np.random.normal(1.0, 0.1)
        yield env.timeout(service)

    # --- Optional Lab Test ---
    if random.random() < PROB_NEED_LAB:
        t_in = env.now
        with lab.request() as req:
            yield req
            wait = env.now - t_in + random.uniform(0.5, 2.5)
            patient.record_wait("lab", wait)
            yield env.timeout(random.triangular(*LAB_TEST_TIME) * np.random.normal(1, 0.1))

    # --- Optional Radiology Test ---
    if random.random() < PROB_NEED_RADIOLOGY:
        t_in = env.now
        with rad.request() as req:
            yield req
            wait = env.now - t_in + random.uniform(0.5, 2.0)
            patient.record_wait("radiology", wait)
            yield env.timeout(random.triangular(*RADIOLOGY_TEST_TIME) * np.random.normal(1, 0.1))

    patient.record_time("departure", env.now)
    results_log.append(patient.summary())
