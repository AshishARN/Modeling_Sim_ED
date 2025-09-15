from graphviz import Digraph

# Create a new directed graph
dot = Digraph('EmergencyDepartmentFlow', comment='Patient Flow in an ED')
dot.attr(rankdir='TB', label='Emergency Department Patient Flow', fontsize='20')
dot.attr('node', shape='box', style='rounded,filled', color='black', fillcolor='lightblue')

# Define styles for different node types for clarity
queue_style = {'shape': 'cylinder', 'fillcolor': 'lightgrey'}
decision_style = {'shape': 'diamond', 'fillcolor': 'khaki'}
process_style = {'shape': 'box', 'fillcolor': 'lightblue'}
start_end_style = {'shape': 'ellipse', 'fillcolor': 'palegreen'}

# --- Define the Nodes (Stages) in the Flow ---

# Start and End points
dot.node('start', 'Patient Arrives', **start_end_style)
dot.node('end', 'Patient Departs System', **start_end_style)

# Triage Stage
dot.node('triage_queue', 'Triage Queue', **queue_style)
dot.node('triage_process', 'Triage Assessment\n(by Nurse)', **process_style)

# Decision Point after Triage
dot.node('priority_decision', 'Assess Priority', **decision_style)

# Treatment Stage (Queues and Process)
dot.node('treatment_queue_critical', 'Treatment Queue\n(Priority 1: Critical)', **queue_style)
dot.node('treatment_queue_urgent', 'Treatment Queue\n(Priority 2: Urgent)', **queue_style)
dot.node('treatment_queue_nonurgent', 'Treatment Queue\n(Priority 3: Non-Urgent)', **queue_style)
dot.node('treatment_process', 'Treatment\n(by Doctor in Room)', **process_style)

# Diagnostics Stage (Decision and Process)
dot.node('diagnostics_decision', 'Diagnostics Needed?', **decision_style)
dot.node('diagnostics_queue', 'Diagnostics Queue\n(e.g., X-ray)', **queue_style)
dot.node('diagnostics_process', 'Perform Diagnostics', **process_style)


# --- Define the Edges (Paths) between Nodes ---

# Path from Arrival to Triage
dot.edge('start', 'triage_queue')
dot.edge('triage_queue', 'triage_process')

# Path from Triage to Priority Decision
dot.edge('triage_process', 'priority_decision')

# Paths branching from Priority Decision to respective Treatment Queues
dot.edge('priority_decision', 'treatment_queue_critical', label='Critical')
dot.edge('priority_decision', 'treatment_queue_urgent', label='Urgent')
dot.edge('priority_decision', 'treatment_queue_nonurgent', label='Non-Urgent')

# Paths from Treatment Queues to the Treatment Process
dot.edge('treatment_queue_critical', 'treatment_process')
dot.edge('treatment_queue_urgent', 'treatment_process')
dot.edge('treatment_queue_nonurgent', 'treatment_process')

# Path from Treatment to the Diagnostics Decision
dot.edge('treatment_process', 'diagnostics_decision')

# Path for patients who DO need diagnostics (the re-entrant loop)
dot.edge('diagnostics_decision', 'diagnostics_queue', label='Yes')
dot.edge('diagnostics_queue', 'diagnostics_process')
# This edge shows the patient returning to the doctor after the test
dot.edge('diagnostics_process', 'treatment_process', label='Results Ready')

# Path for patients who DO NOT need diagnostics or are finished
dot.edge('diagnostics_decision', 'end', label='No / Finished')


# --- Render and Save the Diagram ---

# This will create a file named 'ed_flow_diagram.gv' and a PNG image
# The `view=True` argument will automatically open the generated image.
try:
    dot.render('ed_flow_diagram', view=True, format='png', cleanup=True)
    print("Successfully generated 'ed_flow_diagram.png' and opened it.")
except Exception as e:
    print(f"Error rendering diagram: {e}")
    print("Please ensure Graphviz is installed and in your system's PATH.")