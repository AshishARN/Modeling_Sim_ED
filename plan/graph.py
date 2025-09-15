from graphviz import Digraph

# Create a new directed graph
dot = Digraph('ED_Simulation_Flow', comment='Patient Flow based on the Al-Zahraa Hospital Study')
dot.attr(rankdir='TB', label='Patient Flow Diagram (Al-Zahraa Hospital Model)', fontsize='20', labelloc='t')
dot.attr('node', shape='box', style='rounded,filled', color='black')

# --- Define styles for different node types for clarity ---
queue_style = {'shape': 'cylinder', 'fillcolor': 'lightgrey'}
process_style = {'shape': 'box', 'fillcolor': 'lightblue'}
decision_style = {'shape': 'diamond', 'fillcolor': 'khaki'}
start_end_style = {'shape': 'ellipse', 'fillcolor': 'palegreen'}

# --- Define the Nodes (Stages) in the Flow ---

# Start and End points
dot.node('start', 'Patient Arrives', **start_end_style)
dot.node('end', 'Patient Departs System', **start_end_style)

# Stage 1: Registration
dot.node('registration_queue', 'Registration Queue', **queue_style)
dot.node('registration_process', 'Registration Process', **process_style)

# Stage 2: Triage
dot.node('triage_queue', 'Triage Queue', **queue_style)
dot.node('triage_process', 'Triage Assessment\n(by Nurse)', **process_style)

# Stage 3: Doctor Consultation / First Aid
# This is the central processing hub. We'll use a larger node to show its complexity.
dot.node('doctor_queue', 'Doctor Queue', **queue_style)
dot.node('doctor_process', 
         'Doctor Consultation / First Aid\n\n- PICU (Pediatric)\n- ICU (Intensive Care)\n- CCU (Cardiac Care)\n- Non-Critical Treatment', 
         **process_style, height='2')

# Stage 4: Complementary Tests (Parallel Paths)
dot.node('lab_queue', 'Lab Tests Queue', **queue_style)
dot.node('lab_process', 'Perform Lab Tests', **process_style)

dot.node('radiology_queue', 'Radiology Queue', **queue_style)
dot.node('radiology_process', 'Perform Radiology Tests\n(X-ray, Scanner, etc.)', **process_style)


# --- Define the Edges (Paths) between Nodes ---

# Path from Arrival to Registration
dot.edge('start', 'registration_queue')
dot.edge('registration_queue', 'registration_process')

# Path from Registration to Triage
dot.edge('registration_process', 'triage_queue')
dot.edge('triage_queue', 'triage_process')

# Path from Triage to Doctor
dot.edge('triage_process', 'doctor_queue')
dot.edge('doctor_queue', 'doctor_process')

# Branching paths after Doctor consultation
# These edges represent the decisions made after the initial treatment.
# A patient might need no tests, one test, or both (handled by code logic).
# The diagram shows the possible destinations from the doctor node.
dot.edge('doctor_process', 'end', label='No Tests Needed')
dot.edge('doctor_process', 'lab_queue', label='Lab Tests Ordered')
dot.edge('doctor_process', 'radiology_queue', label='Radiology Ordered')

# Paths for the test processes
dot.edge('lab_queue', 'lab_process')
dot.edge('lab_process', 'end', label='Tests Complete') # After tests, patient departs

dot.edge('radiology_queue', 'radiology_process')
dot.edge('radiology_process', 'end', label='Tests Complete') # After tests, patient departs


# --- Render and Save the Diagram ---
try:
    # This will create a file named 'ED_Simulation_Flow.gv' and a PNG image
    dot.render('ED_Simulation_Flow_2', view=True, format='png', cleanup=True)
    print("Successfully generated 'ED_Simulation_Flow.png' and opened it.")
except Exception as e:
    print(f"Error rendering diagram: {e}")
    print("Please ensure Graphviz is installed and in your system's PATH.")