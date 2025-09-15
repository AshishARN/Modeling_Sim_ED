from graphviz import Digraph

# Create a new directed graph
dot = Digraph('ED_Simulation_Flow_Priority', comment='Patient Flow with Priority Logic')
dot.attr(rankdir='TB', label='Patient Flow Diagram (with Priority Assignment)', fontsize='20', labelloc='t')
dot.attr('node', shape='box', style='rounded,filled', color='black')

# --- Define styles for different node types ---
queue_style = {'shape': 'cylinder', 'fillcolor': 'lightgrey'}
process_style = {'shape': 'box', 'fillcolor': 'lightblue'}
decision_style = {'shape': 'diamond', 'fillcolor': 'khaki'}
start_end_style = {'shape': 'ellipse', 'fillcolor': 'palegreen'}
priority_queue_style = {'shape': 'cylinder', 'fillcolor': 'lightcoral'} # New style for emphasis

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

# ### NEW LOGIC NODE ###
# Add a decision node to show where the priority is assigned
dot.node('priority_assignment', 'Assign Priority\n(Critical / Non-Critical)', **decision_style)

# Stage 3: Doctor Consultation
# Emphasize that this is a priority queue
dot.node('doctor_queue', 'Doctor PRIORITY Queue', **priority_queue_style)
dot.node('doctor_process', 
         'Doctor Consultation / First Aid\n\n- PICU (Pediatric)\n- ICU (Intensive Care)\n- CCU (Cardiac Care)\n- Non-Critical Treatment', 
         **process_style, height='2')

# Stage 4: Complementary Tests
dot.node('lab_queue', 'Lab Tests Queue', **queue_style)
dot.node('lab_process', 'Perform Lab Tests', **process_style)

dot.node('radiology_queue', 'Radiology Queue', **queue_style)
dot.node('radiology_process', 'Perform Radiology Tests', **process_style)


# --- Define the Edges (Paths) between Nodes ---

# Path from Arrival to Registration
dot.edge('start', 'registration_queue')
dot.edge('registration_queue', 'registration_process')

# Path from Registration to Triage
dot.edge('registration_process', 'triage_queue')
dot.edge('triage_queue', 'triage_process')

# ### UPDATED PATH ###
# Path from Triage, through Priority Assignment, to the Doctor Queue
dot.edge('triage_process', 'priority_assignment')
dot.edge('priority_assignment', 'doctor_queue') # The output of the decision is to enter the queue

# Path from Doctor Queue to Doctor Process
dot.edge('doctor_queue', 'doctor_process')

# Branching paths after Doctor consultation (Unchanged)
dot.edge('doctor_process', 'end', label='No Tests Needed')
dot.edge('doctor_process', 'lab_queue', label='Lab Tests Ordered')
dot.edge('doctor_process', 'radiology_queue', label='Radiology Ordered')

# Paths for the test processes (Unchanged)
dot.edge('lab_queue', 'lab_process')
dot.edge('lab_process', 'end', label='Tests Complete')

dot.edge('radiology_queue', 'radiology_process')
dot.edge('radiology_process', 'end', label='Tests Complete')


# --- Render and Save the Diagram ---
try:
    dot.render('ED_Simulation_Flow_Priority', view=True, format='png', cleanup=True)
    print("Successfully generated 'ED_Simulation_Flow_Priority.png' and opened it.")
except Exception as e:
    print(f"Error rendering diagram: {e}")
    print("Please ensure Graphviz is installed and in your system's PATH.")