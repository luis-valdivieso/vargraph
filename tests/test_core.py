import pytest
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