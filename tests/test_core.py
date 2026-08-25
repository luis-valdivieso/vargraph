import sympy as sp

from vargraph import VarGraph


def test_vargraph_initialization():
    g_undirected = VarGraph()
    g_directed = VarGraph(directed=True)

    assert g_undirected.directed is False
    assert g_undirected.graph == {}

    assert g_directed.directed is True
    assert g_directed.graph == {}

def test_add_node():
    g = VarGraph()

    g.add_node("A")
    g.add_node("B")
    g.add_node("A") # Adding a node again shouldn't be a problem

    assert "A" in g.graph
    assert "B" in g.graph
    assert g.graph["A"] == {}

def test_add_edge_directed():
    g = VarGraph(directed=True)

    g.add_edge("A", "B", "x + 2")

    assert "A" in g.graph
    assert "B" in g.graph
    assert g.graph["A"]["B"] == sp.sympify("x+2")
    assert isinstance(g.graph["A"]["B"], sp.Expr)
    assert "A" not in g.graph["B"]  # B shouldn't be connected back to A

def test_add_edge_undirected():
    g = VarGraph(directed=False)

    g.add_edge("A", "B", "x + 2")

    assert "A" in g.graph
    assert "B" in g.graph
    assert g.graph["A"]["B"] == sp.sympify("x+2")
    assert g.graph["B"]["A"] == sp.sympify("x+2")
    assert isinstance(g.graph["B"]["A"], sp.Expr)
    assert isinstance(g.graph["A"]["B"], sp.Expr)

def test_free_symbols():
    g = VarGraph()
    g.add_edge("A", "B", "x + 2")
    g.add_edge ("B", "C", "y**2 + x + 1")

    expected_symbols = {sp.Symbol("x"), sp.Symbol("y")}

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

def test_evaluate_all_variables_substituted():
    g = VarGraph(directed=True)
    g.add_edge("A", "B", "y")
    g.add_edge("B", "C", "x + 2")
    g.add_node("C")
    g.add_edge("A", "C", 5)

    subs_dict = {"x" : 5, "y": 1}
    substituted_graph = g.evaluate(subs_dict)

    assert substituted_graph.graph == {
        "A": {"B": sp.Float(1.0), "C": sp.Float(5.0)},
        "B": {"C": sp.Float(7.0)},
        "C": {},
    }

    assert g.graph["B"]["C"] == sp.sympify("x + 2")

def test_evaluate_one_variable_substituted():
    g = VarGraph(directed=True)
    g.add_edge("A", "B", "y")
    g.add_edge("B", "C", "x + 2")
    g.add_node("C")
    g.add_edge("A", "C", 5)

    subs_dict = {"x" : 5}
    substituted_graph = g.evaluate(subs_dict)

    assert substituted_graph.graph == {
        "A": {"B": sp.sympify("y"), "C": sp.Float(5.0)},
        "B": {"C": sp.Float(7.0)},
        "C": {},
    }

    assert g.graph["B"]["C"] == sp.sympify("x + 2")

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