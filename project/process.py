# process.py
import random
import numpy as np
from patient import Patient
from config import *

def patient_lifecycle(env, name, resources, results_log):
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
        wait = env.now - t_in
        patient.record_wait("registration", wait)
        yield env.timeout(random.uniform(*REGISTRATION_TIME))

    # --- Triage ---
    t_in = env.now
    with triage.request() as req:
        yield req
        patient.record_time("triage_start", env.now)
        wait = env.now - t_in
        patient.record_wait("triage", wait)
        yield env.timeout(random.triangular(*TRIAGE_TIME))

    # --- Doctor Consultation ---
    t_in = env.now
    with doc.request() as req:
        yield req
        patient.record_time("doctor_start", env.now)
        wait = env.now - t_in
        patient.record_wait("doctor", wait)

        r = random.random()
        if r < PROB_PICU:
            patient.patient_type = "PICU"
            service = random.uniform(*FIRST_AID_PICU_TIME)
        elif r < PROB_PICU + PROB_ICU:
            patient.patient_type = "ICU"
            service = random.uniform(*FIRST_AID_ICU_TIME)
        elif r < PROB_PICU + PROB_ICU + PROB_CCU:
            patient.patient_type = "CCU"
            service = random.uniform(*FIRST_AID_CCU_TIME)
        else:
            patient.patient_type = "Non-Critical"
            service = random.uniform(*COMPLEMENTARY_TREATMENT_TIME)
        yield env.timeout(service)

    # --- Optional Lab Test ---
    if random.random() < PROB_NEED_LAB:
        t_in = env.now
        with lab.request() as req:
            yield req
            wait = env.now - t_in
            patient.record_wait("lab", wait)
            yield env.timeout(random.triangular(*LAB_TEST_TIME))

    # --- Optional Radiology Test ---
    if random.random() < PROB_NEED_RADIOLOGY:
        t_in = env.now
        with rad.request() as req:
            yield req
            wait = env.now - t_in
            patient.record_wait("radiology", wait)
            yield env.timeout(random.triangular(*RADIOLOGY_TEST_TIME))

    patient.record_time("departure", env.now)
    results_log.append(patient.summary())
