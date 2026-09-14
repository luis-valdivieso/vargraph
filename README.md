# VarGraph 🕸️📐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/luis-valdivieso/vargraph)

**VarGraph** is a Python library that merges Graph Theory with Symbolic Computation. Instead of being limited to pure numerical weights, VarGraph allows you to build mathematical nets where edges are algebraic expressions, equations, or variables.

Under the hood, it seamlessly integrates with [SymPy](https://www.sympy.org/) to provide advanced algebraic operations over complex network topologies.

## 📦 Installation

VarGraph requires **SymPy** as its core dependency for all mathematical evaluations.

**For regular users:**
```bash
pip install vargraph
```

**For developers (Local Setup)**
If you want to contribute or modify the source code, install it in editable mode with testing dependencies:
```bash
git clone [https://github.com/luis-valdivieso/vargraph.git](https://github.com/luis-valdivieso/vargraph.git)
cd vargraph
pip install -e .[dev]
```

## 🚀 Quickstart and core features

### 1. Initialization and Algebraic Edges
Create a graph and assign symbolic mathematical expressions as edge weights.

```python
import sympy as sp
from vargraph import VarGraph

# Initialize a directed graph
g = VarGraph(directed=True)

# Add edges with symbolic weights
g.add_edge("A", "B", "x**2 + 2*y")
g.add_edge("B", "C", "3*x")
g.add_edge("A", "C", "z")

# Extract all free algebraic variables used in the graph
print(g.free_symbols) 
# Output: {x, y, z}
```

### 2. Logical Conditions (Topological Guardrails)
You can define strict logical requirements for edge traversal using SymPy equalities. This is particularly useful for routing multi-agent workflows or handling out-of-domain queries.
```python
# Define state variables
in_domain = sp.Symbol("in_domain")

# Build a routing topology with guardrails
g.add_edge("Router", "Agent_Alpha", weight="cost_alpha", condition=sp.Eq(in_domain, 1))
g.add_edge("Router", "OOD_Handler", weight="cost_ood", condition=sp.Eq(in_domain, 0))

# Extract the valid subgraph given a specific context
valid_g = g.get_valid_subgraph({"in_domain": 1})
```

### 3. Visualizing Execution Traces
Render dynamic, auto-scaling visual representations of your pipelines. Highlight successful execution paths and expose topological guardrails that blocked specific routes.
```python
successful_route = ["Input", "Router", "Agent_Alpha", "Output"]
blocked_routes = [("Router", "OOD_Handler")]

# Renders the graph with adaptive scaling and bounding boxes for SymPy labels
fig = g.draw_execution_trace(
    path=successful_route, 
    failed_edges=blocked_routes, 
    node_size=2500
)
```

### 4. JSON Serialization & Persistence
Save your complex topological configurations to a standard JSON file and load them back in any environment without losing your symbolic mathematical properties.
```python
# Serialize the pipeline state for later use
g.save_to_json("multi_agent_pipeline.json")

# Safely reconstruct the graph, SymPy weights, and logical conditions
loaded_g = VarGraph.load_from_json("multi_agent_pipeline.json")
```

### 5. Symbolic Pathfinding
Find all simple paths between two nodes and get the simplified algebraic cost of the route.
```python
paths = g.get_symbolic_paths("A", "C")
for route, cost in paths:
    print(f"Route: {route} | Cost: {cost}")

# Output:
# Route: ['A', 'C'] | Cost: z
# Route: ['A', 'B', 'C'] | Cost: x**2 + 3*x + 2*y
```

### 6. Adjacency Matrix Extraction
Export the graph topology as a mathematical SymPy Matrix for linear algebra operations.
```python
matrix, nodes = g.get_adjacency_matrix(["A", "B", "C"])
print(matrix)

# Output: 
# Matrix([
# [0, x**2 + 2*y, 0],
# [0,          0, 3*x],
# [0,          0,   0]])
```

### 7. Numerical Evaluation
Instantiate the abstract mathematical model into a real-world numerical use case. It supports partial evaluations, safely keeping non-substituted variables as SymPy symbols.
```python
# Evaluate substituting x=2 (partial evaluation, y and z remain)
num_graph = g.evaluate({"x": 2})

print(num_graph.get_weight("B", "C"))
# Output: 6.0

print(num_graph.get_weight("A", "B"))
# Output: 2.0*y + 4.0
```

## 📄 License
This project is licensed under the MIT License.