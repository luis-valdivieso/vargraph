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

    def get_adjacency_matrix(self, nodelist=None):
        
        if nodelist is None:
            nodelist = list(self.graph.keys())
        row_list = []
        for node in nodelist:
            if node not in self.graph:
                raise ValueError(f"El nodo '{node}' no existe en el grafo.")
        for node in nodelist:
            row = []
            for other_node in nodelist:
                weight = self.graph[node].get(other_node, sp.S.Zero)
                row.append(weight)
            row_list.append(row)

        return sp.Matrix(row_list), nodelist

    def evaluate(self, subs_dict):
        new_graph = VarGraph(directed=self.directed)
        for node in self.graph:
            new_graph.add_node(node)
            for other_node, weight in self.graph[node].items():
                new_graph.add_edge(node, other_node, weight.subs(subs_dict).evalf())
        return new_graph

    def get_symbolic_paths(self, source, target):
        # Node validation
        if source not in self.graph:
            raise ValueError(f"Node '{source}' does not exist in the graph.")
        if target not in self.graph:
            raise ValueError(f"Node '{target}' does not exist in the graph.")

        paths_found = []

        # Auxiliary dfs function
        def dfs(current_node, current_path, current_cost, visited):
            current_path.append(current_node)
            visited.add(current_node)

            if current_node == target:
                paths_found.append((list(current_path), sp.simplify(current_cost)))
            else:
                for neighbour, weight in self.graph[current_node].items():
                    if neighbour not in visited:
                        dfs(neighbour, current_path, current_cost + weight, visited)
            # Backtracking
            current_path.pop()
            visited.remove(current_node)

        dfs(source, [], sp.S.Zero, set())

        return paths_found
