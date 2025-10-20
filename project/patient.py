# patient.py
class Patient:
    def __init__(self, name):
        self.name = name
        self.timestamps = {}
        self.wait_times = {stage: 0.0 for stage in ['registration', 'triage', 'doctor', 'lab', 'radiology']}
        self.patient_type = None

    def record_time(self, stage, time):
        self.timestamps[stage] = time

    def record_wait(self, stage, duration):
        self.wait_times[stage] = duration

    def summary(self):
        return {
            "patient": self.name,
            "type": self.patient_type,
            **self.wait_times
        }
