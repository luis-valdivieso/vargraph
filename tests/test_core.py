import sympy as sp

from vargraph import VarGraph


def test_vargraph_initialization():
    g_undirected = VarGraph()
    g_directed = VarGraph(directed=True)

    assert g_undirected.directed is False
    assert g_undirected.get_nodes() == []

    assert g_directed.directed is True
    assert g_directed.get_edges() == []

def test_add_node():
    g = VarGraph()

    g.add_node("A")
    g.add_node("B")
    g.add_node("A") # Adding a node again shouldn't be a problem

    assert "A" in g.get_nodes()
    assert "B" in g.get_nodes()
    assert g.get_neighbors("A") == []

def test_add_edge_directed():
    g = VarGraph(directed=True)

    g.add_edge("A", "B", "x + 2")

    assert "A" in g.get_nodes()
    assert "B" in g.get_nodes()
    assert g.get_weight("A","B") == sp.sympify("x+2")
    assert isinstance(g.get_weight("A","B"), sp.Expr)
    assert "A" not in g.get_neighbors("B")  # B shouldn't be connected back to A

def test_add_edge_undirected():
    g = VarGraph(directed=False)

    g.add_edge("A", "B", "x + 2")

    assert "A" in g.get_nodes()
    assert "B" in g.get_nodes()
    assert g.get_weight("A","B") == sp.sympify("x+2")
    assert g.get_weight("B","A") == sp.sympify("x+2")
    assert isinstance(g.get_weight("A","B"), sp.Expr)
    assert isinstance(g.get_weight("B","A"), sp.Expr)

def test_add_edge_condition_directed():
    g = VarGraph(directed=True)
    
    g.add_edge("A", "B", "x + 2", "x>2")

    assert "A" in g.get_nodes()
    assert "B" in g.get_nodes()
    assert g.get_weight("A","B") == sp.sympify("x+2")
    assert isinstance(g.get_weight("A","B"), sp.Expr)
    assert "A" not in g.get_neighbors("B")  # B shouldn't be connected back to A
    assert g.get_edge_condition("A", "B") == sp.sympify("x>2")

def test_add_edge_condition_undirected():
    g = VarGraph(directed=False)
    
    g.add_edge("A", "B", "x + 2", "x>2")

    assert "A" in g.get_nodes()
    assert "B" in g.get_nodes()
    assert g.get_weight("A","B") == sp.sympify("x+2")
    assert g.get_weight("B","A") == sp.sympify("x+2")
    assert isinstance(g.get_weight("A","B"), sp.Expr)
    assert isinstance(g.get_weight("B","A"), sp.Expr)
    assert g.get_edge_condition("A", "B") == sp.sympify("x>2")
    assert g.get_edge_condition("B", "A") == sp.sympify("x>2")

def test_free_symbols():
    g = VarGraph()
    g.add_edge("A", "B", "x + 2")
    g.add_edge("B", "C", "y**2 + x + 1")
    g.add_edge("C", "A", 4.0, "api_cost > 2")
    expected_symbols = {sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("api_cost")}

    assert g.free_symbols == expected_symbols

def test_get_adjacency_matrix_automatic_order():
    g = VarGraph(directed=True)
    g.add_edge("A", "A", "y")
    g.add_edge("A", "B", "x + 2")
    g.add_edge("B", "A", "x + 2")
    g.add_edge("B", "C", "y**2 + x + 1")
    g.add_edge("C", "B", "y**1 + x")
    g.add_edge("A", "C", 5)

    expected_matrix = [
        [sp.sympify("y"), sp.sympify("x+2"), sp.sympify(5)],
        [sp.sympify("x+2"), sp.S.Zero, sp.sympify("y**2 + x + 1")],
        [sp.S.Zero, sp.sympify("y**1 + x"), sp.S.Zero]
    ]
    
    matrix, nodes = g.get_adjacency_matrix()
    
    assert matrix == sp.Matrix(expected_matrix)
    assert nodes == ["A", "B", "C"]

def test_get_adjacency_matrix_defined_order():
    g = VarGraph(directed=True)
    g.add_edge("A", "A", "y")
    g.add_edge("A", "B", "x + 2")
    g.add_edge("B", "A", "x + 2")
    g.add_edge("B", "C", "y**2 + x + 1")
    g.add_edge("C", "B", "y**1 + x")
    g.add_edge("A", "C", 5)

    expected_matrix = [
        [sp.sympify("y"), sp.sympify(5)],
        [sp.S.Zero, sp.S.Zero]
    ]
    
    matrix, nodes = g.get_adjacency_matrix(["A", "C"])
    
    assert matrix == sp.Matrix(expected_matrix)
    assert nodes == ["A","C"]

def test_has_cycles_and_is_dag_with_acyclic_graph():
    g = VarGraph(directed=True)
    g.add_edge("FinderAgent", "ValidationAgent")
    g.add_edge("ValidationAgent", "WriterAgent")
    
    assert g.has_cycles() is False
    assert g.is_dag() is True

def test_has_cycles_with_cyclic_graph():
    g = VarGraph(directed=True)
    g.add_edge("FinderAgent", "ValidationAgent")
    g.add_edge("ValidationAgent", "FinderAgent")
    
    assert g.has_cycles() is True
    assert g.is_dag() is False

def test_is_dag_on_undirected_graph():
    g = VarGraph(directed=False)
    g.add_edge("AgentA", "AgentB")
    
    assert g.is_dag() is False

def test_evaluate_all_variables_substituted():
    g = VarGraph(directed=True)
    # Añadimos variables lógicas (z, w) a las condiciones
    g.add_edge("A", "B", "y", "z > 5")
    g.add_edge("B", "C", "x + 2", "Eq(w, 1)")
    g.add_node("C")
    g.add_edge("A", "C", 5) # Condición por defecto: True

    # Sustituimos todo, haciendo que las condiciones se cumplan
    subs_dict = {"x" : 5, "y": 1, "z": 10, "w": 1}
    substituted_graph = g.evaluate(subs_dict)

    assert set(substituted_graph.get_nodes()) == {"A", "B", "C"}

    expected_edges = [
        ("A", "B", sp.Float(1.0), sp.S.true),  # 10 > 5 se evalúa a True
        ("A", "C", sp.Float(5.0), sp.S.true),
        ("B", "C", sp.Float(7.0), sp.S.true)   # 1 == 1 se evalúa a True
    ]

    assert set(substituted_graph.get_edges()) == set(expected_edges)
    assert substituted_graph.get_neighbors("C") == []
    
    # Comprobamos que el grafo original no ha mutado
    assert g.get_weight("B", "C") == sp.sympify("x + 2")
    assert g.get_edge_condition("A", "B") == sp.sympify("z > 5")


def test_evaluate_one_variable_substituted():
    g = VarGraph(directed=True)
    g.add_edge("A", "B", "y", "z > 5")
    g.add_edge("B", "C", "x + 2")
    g.add_node("C")
    g.add_edge("A", "C", 5)

    # Solo sustituimos 'x'. Las variables 'y' (peso) y 'z' (condición) deben quedar intactas.
    subs_dict = {"x" : 5}
    substituted_graph = g.evaluate(subs_dict)

    assert set(substituted_graph.get_nodes()) == {"A", "B", "C"}

    expected_edges = [
        ("A", "B", sp.sympify("y"), sp.sympify("z > 5")), # Condición intacta
        ("A", "C", sp.Float(5.0), sp.S.true),
        ("B", "C", sp.Float(7.0), sp.S.true)
    ]
    assert set(substituted_graph.get_edges()) == set(expected_edges)
    assert substituted_graph.get_neighbors("C") == []
    assert g.get_weight("B", "C") == sp.sympify("x + 2")

def test_get_symbolic_paths():
    g = VarGraph(directed=True)
    g.add_edge("A", "B", "x")
    g.add_edge("B", "C", "x")

    assert g.get_symbolic_paths("A", "C") == [(["A", "B", "C"], sp.sympify("2*x"))]

    g = VarGraph(directed=True)
    g.add_edge("A", "B", "x")
    g.add_edge("B", "C", "x")
    g.add_edge("A", "D", "y")
    g.add_edge("D", "C", 5)

    assert g.get_symbolic_paths("A", "C") == [(["A", "B", "C"], sp.sympify("2*x")), (["A", "D", "C"], sp.sympify("y+5")) ]

    g = VarGraph(directed=True)
    g.add_edge("A", "B", "x")
    g.add_edge("B", "C", "x")
    g.add_edge("C", "A", "y")

    assert g.get_symbolic_paths("A", "C") == [(["A", "B", "C"], sp.sympify("2*x")) ]

    assert g.get_symbolic_paths("A", "A") == [(["A"], sp.S.Zero)]

def test_get_valid_subgraph():
    g = VarGraph(directed=True)

    # Add edge with conditions
    g.add_edge("A", "B", weight="api_cost", condition="conf > 0.8")
    g.add_edge("A", "C", weight="penalty", condition="conf <= 0.8")
    
    # Edge with no condition
    g.add_edge("B", "D", weight="gen_cost")
    
    # Add an isolated node to ensure topology is preserved
    g.add_node("E")

    # First scenario
    context_high = {"conf": 0.9}
    valid_g_high = g.get_valid_subgraph(context_high)
    
    assert set(valid_g_high.get_nodes()) == {"A", "B", "C", "D", "E"}
    
    # A C path is blocked but B C path is not 
    expected_edges_high = [
        ("A", "B", sp.sympify("api_cost"), sp.S.true),
        ("B", "D", sp.sympify("gen_cost"), sp.S.true)
    ]
    assert set(valid_g_high.get_edges()) == set(expected_edges_high)
    assert "C" not in valid_g_high.get_neighbors("A")

    # Second Scenario
    context_low = {"conf": 0.4}
    valid_g_low = g.get_valid_subgraph(context_low)
    
    # Now A C route is valid but A B is not
    expected_edges_low = [
        ("A", "C", sp.sympify("penalty"), sp.S.true),
        ("B", "D", sp.sympify("gen_cost"), sp.S.true)
    ]
    assert set(valid_g_low.get_edges()) == set(expected_edges_low)
    assert "B" not in valid_g_low.get_neighbors("A")