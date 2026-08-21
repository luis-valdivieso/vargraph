import sympy as sp

class VarGraph:
    def __init__(self, directed=False):
        self.directed = directed
        self.graph = {}

    @property
    def free_symbols(self):
        "Returns the complete set of free_symbols of the weights expressions of the graph"
        symbols = set()
        for neighbors in self.graph.values():
            for weight in neighbors.values():
                symbols.update(weight.free_symbols)
                
        return symbols

    def add_node(self, node):
        """Adds an isolated node if it doesn't exist previously"""
        if node not in self.graph:
            self.graph[node] = {}

    def add_edge(self, u, v, weight=1):
        """Adds an edge between u and v with a weight"""
        # If the nodes are new, we initialize the internal dictionaries
        self.add_node(u)
        self.add_node(v)

        sympified_weight = sp.sympify(weight)
        # Create u-v connection with sympy expression
        self.graph[u][v] = sympified_weight
        
        # If the graph is not directed, we create the v-u connection
        if not self.directed:
            self.graph[v][u] = sympified_weight