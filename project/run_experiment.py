# --- run_experiment.py (Modified) ---

import matplotlib.pyplot as plt
import numpy as np
from sim import run_simulation

def plot_los_vs_capacity(resource_to_vary, capacity_range, default_capacities, cohort_filter='all'):
    """
    Runs simulations and plots average LOS for a specific patient cohort.

    Args:
        resource_to_vary (str): The dictionary key of the resource to change.
        capacity_range (iterable): The range of capacities to test (e.g., range(1, 6)).
        default_capacities (dict): The baseline capacities for all other resources.
        cohort_filter (str): 'all', 'lab_users', or 'radiology_users'.
    """
    x_values = []
    y_values = []

    print(f"--- Starting Experiment: LOS vs. {resource_to_vary} for cohort: '{cohort_filter}' ---")
    
    for capacity in capacity_range:
        current_capacities = default_capacities.copy()
        current_capacities[resource_to_vary] = capacity
        
        print(f"Running simulation for {capacity} {resource_to_vary}(s)...")
        
        # 1. Get the raw data from the simulation
        all_patients = run_simulation(capacities=current_capacities)
        
        # 2. ### NEW: Filter the data to get your specific cohort ###
        cohort_patients = []
        if cohort_filter == 'lab_users':
            # A patient is a "lab user" if they started the lab process.
            # The lab_start timestamp will be > 0.
            cohort_patients = [p for p in all_patients if p.timestamps['lab_start'] > 0]
        elif cohort_filter == 'radiology_users':
            # Similarly for radiology
            cohort_patients = [p for p in all_patients if p.timestamps['rad_start'] > 0]
        else: # Default is 'all'
            cohort_patients = all_patients

        # 3. Calculate the metric ONLY on the filtered cohort
        avg_los = 0.0
        if cohort_patients:
            cohort_los_times = [
                p.timestamps['depart'] - p.timestamps['arrival'] for p in cohort_patients
            ]
            avg_los = np.mean(cohort_los_times)
        
        x_values.append(capacity)
        y_values.append(avg_los)
        
        print(f"  -> Found {len(cohort_patients)} patients in cohort.")
        print(f"  -> Result: Cohort Average LOS = {avg_los:.2f} minutes")

    print("\n--- Experiment Complete ---")

    # --- Plotting the results ---
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    
    # Dynamic plot title
    title = f'Impact of {resource_to_vary.replace("_", " ").title()} on Avg. LOS for {cohort_filter.replace("_", " ").title()}'
    plt.title(title, fontsize=16)
    plt.xlabel(f'Number of {resource_to_vary.replace("_", " ").title()}s', fontsize=12)
    plt.ylabel('Average Length of Stay (minutes)', fontsize=12)
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(x_values)
    
    filename = f'los_vs_{resource_to_vary}_cohort_{cohort_filter}.png'
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")
    
    plt.show()


if __name__ == '__main__':
    # --- Define Your Experiment for LAB PATIENTS ---

    baseline_capacities = {
        'registration_desk': 2,
        'triage_nurse': 2,
        'doctor': 4,
        'lab': 3, # This value will be overridden
        'radiology': 2
    }

    # 1. Set the resource to vary to 'lab' or the other 4 services
    resource_to_test = 'doctor'
    
    # 2. Test with 1, 2, 3, 4, and 5 lab technicians
    capacities_to_test = range(1, 6)

    # 3. Call the plotting function with the specific cohort_filter
    plot_los_vs_capacity(
        resource_to_vary=resource_to_test,
        capacity_range=capacities_to_test,
        default_capacities=baseline_capacities,
        cohort_filter='lab_users' # <-- This is the key change!
    )