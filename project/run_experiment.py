# --- run_experiment.py ---

import matplotlib.pyplot as plt
from sim import run_simulation # Import the function from your other file

def plot_los_vs_capacity(resource_to_vary, capacity_range, default_capacities, patient_arrival_time):
    """
    Runs simulations for a range of capacities for a specific resource
    and plots the average LOS against the number of servers.
    """
    x_values = []  # To store capacities (e.g., 1, 2, 3, 4, 5)
    y_values = []  # To store the resulting average LOS for each capacity

    print(f"--- Starting Experiment: LOS vs. Number of {resource_to_vary}s ---")
    
    for capacity in capacity_range:
        # Create a copy of the default capacities for this specific run
        current_capacities = default_capacities.copy()
        # Set the capacity for the resource we are currently varying
        current_capacities[resource_to_vary] = capacity
        
        print(f"Running simulation for {capacity} {resource_to_vary}(s)...")
        
        # Run the simulation and get the average LOS
        avg_los = run_simulation(capacities=current_capacities)
        
        # Store the results for plotting
        x_values.append(capacity)
        y_values.append(avg_los)
        
        print(f"  -> Result: Average LOS = {avg_los:.2f} minutes")

    print("\n--- Experiment Complete ---")

    # --- Plotting the results ---
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    
    plt.title(f'Impact of {resource_to_vary.replace("_", " ").title()} on Average Length of Stay', fontsize=16)
    plt.xlabel(f'Number of {resource_to_vary.replace("_", " ").title()}s', fontsize=12)
    plt.ylabel('Average Length of Stay (minutes)', fontsize=12)
    
    # Make the plot clearer
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(x_values) # Ensure x-axis ticks are integers for the capacities tested
    
    # Save the plot to a file
    filename = f'los_vs_{resource_to_vary}.png'
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")
    
    # Display the plot
    plt.show()


if __name__ == '__main__':
    # --- Define Your Experiment Here ---

    # 1. Define the baseline capacities for all resources
    baseline_capacities = {
        'registration_desk': 2, # This value will be overridden in the loop
        'triage_nurse': 2,
        'doctor': 4,
        'lab': 3,
        'radiology': 2
    }

    # 2. Define which resource to vary and the range of servers to test
    # To plot for a different resource, just change this one line!
    # e.g., resource = 'triage_nurse' or resource = 'doctor'
    resource_to_test = 'radiology'
    
    # Let's test with 1, 2, 3, 4, and 5 registration desks
    capacities_to_test = range(2, 7)

    # 3. Set the arrival time for this experiment
    arrival_time = 20.0

    # 4. Run the plotting function
    # Note: We pass PATIENT_INTERARRIVAL_TIME so it's clear what load the system is under
    plot_los_vs_capacity(
        resource_to_vary=resource_to_test,
        capacity_range=capacities_to_test,
        default_capacities=baseline_capacities,
        patient_arrival_time=arrival_time
    )