# results_analysis.py
import pandas as pd
import matplotlib.pyplot as plt

def analyze_csv(file_path, title_suffix=""):
    df = pd.read_csv(file_path)
    waits = ['registration', 'triage', 'doctor', 'lab', 'radiology']
    df['total_wait'] = df[waits].sum(axis=1)
    summary = df[waits + ['total_wait']].mean().round(2)
    print(f"\nAverage Wait Times ({title_suffix}):\n", summary)
    return df, summary

def plot_bar_staffing(file="results_staffing_experiment.csv"):
    df = pd.read_csv(file)
    plt.bar(df['doctors'], df['doctor'])
    plt.title("Average Doctor Wait vs Doctor Count")
    plt.xlabel("Number of Doctors")
    plt.ylabel("Average Doctor Wait (min)")
    plt.show()

def plot_line_stress(file="results_stress_experiment.csv"):
    df = pd.read_csv(file)
    df.sort_values('interarrival', inplace=True)
    plt.plot(df['interarrival'], df['total_wait'], marker='o')
    plt.title("Arrival Rate vs Total Wait (Hockey Stick Effect)")
    plt.xlabel("Mean Interarrival Time (min)")
    plt.ylabel("Average Total Wait (min)")
    plt.show()

def plot_box_criticality(file="simulation_results_full.csv"):
    df = pd.read_csv(file)
    plt.figure(figsize=(6,5))
    df.boxplot(column='doctor', by='type')
    plt.title("Doctor Waits by Patient Type")
    plt.suptitle("")
    plt.xlabel("Patient Type")
    plt.ylabel("Doctor Wait (min)")
    plt.show()
