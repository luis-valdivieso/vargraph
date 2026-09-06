from collections import deque

import sympy as sp


class VarGraph:
    """
    A graph object that allows to store symbolic expressions as weights.

    This class allows to get adjacency matrices, compute paths from an origin to a target, and build mathematical nets, all of this using Sympy methods.

    Attributes:
        directed (bool): allows to specify if a graph is directed (True) or undirected (False, by default)
    """
    def __init__(self, directed=False):
        """
        Initializes a new empty graph

        Args:
            directed (bool, optional): allows to specify if a graph is directed (True) or undirected (False, by default)
        """
        self.directed = directed
        self._graph = {}

    @property
    def free_symbols(self):
        """
        Returns the complete set of free_symbols of the weights expressions of the graph.
        """
        symbols = set()
        for neighbors in self._graph.values():
            for edge in neighbors.values():
                symbols.update(edge["weight"].free_symbols)
                symbols.update(edge["condition"].free_symbols)
                
        return symbols

    def add_node(self, node):
        """
        Adds an isolated node if it doesn't exist previously
        
        Args:
            node (str): Node that will be added to the graph
        """
        if node not in self._graph:
            self._graph[node] = {}

    def add_edge(self, u, v, weight=1, condition=None):
        """
        Adds an edge between u and v with a weight
        
        Args:
            u (str): Origin of the edge
            v (str): End of the edge
            weight (optional): Weight of the edge (by default is 1). Should be a sympy convertible formula
            condition: Logical constraint that represent when we can pass from u to v
        """
        # If the nodes are new, we initialize the internal dictionaries
        self.add_node(u)
        self.add_node(v)

        sympified_weight = sp.sympify(weight)

        if condition is None:
            sympified_condition = sp.S.true
        else:
            sympified_condition = sp.sympify(condition)
            if isinstance(sympified_condition, bool):
                sympified_condition = sp.S.true if sympified_condition else sp.S.false

        # Create u-v connection with sympy expression
        self._graph[u][v] = {
            'weight': sympified_weight, 
            'condition': sympified_condition
        }
        
        # If the graph is not directed, we create the v-u connection
        if not self.directed:
            self._graph[v][u] = {
                'weight': sympified_weight, 
                'condition': sympified_condition
            }

    def get_nodes(self):
        """
        Returns all the list of nodes of the graph.

        Returns:
            list: A list containing all the nodes of the graph.
        """
        return list(self._graph.keys())

    def get_neighbors(self, node):
        """
        Returns all the neighbors of a given node

        Args:
            node (str): Node which we will get the neighbors from 
        
        Raises:
            ValueError: If the node does not exist
        """
        if node not in self._graph:
            raise ValueError(f"Node {node} does not exist")
        else:
            return list(self._graph[node].keys())

    def get_weight(self, u, v):
        """
        Returns the weight of the u-v edge

        Args:
            u (str): Origin of the edge
            v (str): End of the edge 

        Raises: 
            ValueError if any of the nodes does not exists
        """
        if u not in self._graph:
            raise ValueError(f"Node {u} does not exist")
        if v not in self._graph:
            raise ValueError(f"Node {v} does not exist")
        
        edge_data = self._graph[u].get(v)
        if edge_data is None:
            return None
            
        return edge_data["weight"]

    def get_edge_condition(self, u, v):
        """
        Returns the logic condition of the u-v edge

        Args:
            u (str): Origin of the edge
            v (str): End of the edge 

        Raises: 
            ValueError if any of the nodes does not exists
        """
        if u not in self._graph:
            raise ValueError(f"Node {u} does not exist")
        if v not in self._graph:
            raise ValueError(f"Node {v} does not exist")
        edge_data = self._graph[u].get(v)
        if edge_data is None:
            return None
            
        return edge_data["condition"]

    def get_edges(self):
        """
        Returns all the edges of the graph.
        

        Returns:
            list: A list containing all the edges of the graph.
        """
        edges = []
        for u, neighbors in self._graph.items():
            for v in neighbors:
                edges.append((u, v, self.get_weight(u,v), self.get_edge_condition(u,v)))
        return edges
    
    def get_adjacency_matrix(self, nodelist=None):
        """
        Returns a Sympy adjacency matrix of the graph

        Args:
            nodelist: A list that contains the nodes that will appear in the adjacency matrix. By default is empty.

        Returns:
            - A Sympy matrix with all the desired nodes
            - A node list with all the desired nodes
        """
        if nodelist is None:
            nodelist = list(self._graph.keys())
        row_list = []
        for node in nodelist:
            if node not in self._graph:
                raise ValueError(f"Node '{node}' does not exist in the graph.")
        for node in nodelist:
            row = []
            for other_node in nodelist:
                if self.get_weight(node, other_node) is None:
                    weight = sp.S.Zero
                else:
                    weight = self.get_weight(node, other_node)
                row.append(weight)
            row_list.append(row)

        return sp.Matrix(row_list), nodelist

    def has_cycles(self):
        """Detects cycles using Kanh's Algorithm  (Topological Sort)."""
        # Initialize indegrees
        in_degree = {node: 0 for node in self._graph}

        # Compute indegrees
        for u in self._graph:
            for v in self._graph[u]:
                in_degree[v] += 1

        # Add to the queue nodes without dependencies (in-degree == 0)
        q = deque([node for node in self._graph if in_degree[node] == 0])

        visited = 0

        # Process the queue
        while q:
            u = q.popleft()
            visited += 1

            # Decrease neighbors indegree
            for v in self._graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    q.append(v)

        # If we visited less than the total number of nodes, we found a cycle
        return visited != len(self._graph)

    def is_dag(self):
        """
        Returns true if the graph is directed and has no cycles
        """
        return self.directed and not self.has_cycles()
    
    def evaluate(self, subs_dict):
        """
        Returns a graph with all the variables susbtituted in it

        Args:
            subs_dict: Dictionary that contains the variables that you want to substitute and the values to substitute them. For example {"x": 3.0, "y":7.0}
        """
        new_graph = VarGraph(directed=self.directed)
        for node in self._graph:
            new_graph.add_node(node)
            for other_node, edge in self._graph[node].items():
                new_weight = edge.get("weight").subs(subs_dict).evalf()
                new_cond = edge.get("condition").subs(subs_dict)
                new_graph.add_edge(node, other_node, weight=new_weight, condition=new_cond)
        return new_graph

    def get_symbolic_paths(self, source, target):
        """
        Returns a list a tuple representing all the paths between source and target nodes.

        Args: 
            source (str): Node from which the path will begin
            target (str): Node that the path will end in

        Returns:
            list of tuple: A list where each element is a tuple containing:
            - A node list representing the path (ordered).
            - A Sympy object representing the path cost.
        """
        # Node validation
        if source not in self._graph:
            raise ValueError(f"Node '{source}' does not exist in the graph.")
        if target not in self._graph:
            raise ValueError(f"Node '{target}' does not exist in the graph.")

        paths_found = []

        # Auxiliary dfs function
        def dfs(current_node, current_path, current_cost, visited):
            current_path.append(current_node)
            visited.add(current_node)

            if current_node == target:
                paths_found.append((list(current_path), sp.simplify(current_cost)))
            else:
                for neighbour in self._graph[current_node]:
                    if neighbour not in visited:
                        dfs(neighbour, current_path, current_cost + self.get_weight(current_node, neighbour), visited)
            # Backtracking
            current_path.pop()
            visited.remove(current_node)

        dfs(source, [], sp.S.Zero, set())

        return paths_found

    def get_valid_subgraph(self, context_dict):
        """
        Returns a graph which contains only the edges where the condition evaluates to True given the context dictionary

        Args:
            subs_dict: Dictionary that contains the variables that you want to substitute and the values to substitute them. For example {"x": 3.0, "y":7.0}
        """
        new_graph = VarGraph(directed=self.directed)
        for node in self.get_nodes():
            new_graph.add_node(node)
            for other_node, edge in self._graph[node].items():
                new_cond = edge.get("condition").subs(context_dict)
                if new_cond == sp.S.true:
                    new_graph.add_edge(node, other_node, weight=edge.get("weight"), condition=new_cond)
        return new_graph

    def get_bottleneck(self, path, subs_dict):
        """
        Returns a sorted structure containing the absolute numerical contribution of each algebraic variable to the total path cost.

        Args:
            path: Node list that represents a particular path in the graph
            subs_dict: Dictionary that contains the variables that you want to substitute and the values to substitute them. For example {"x": 3.0, "y":7.0}
        Return:
            term_contributions: A list that contains the contribution of each variable to the total cost
        """
        # A route with only one node does not have any transition cost
        if len(path) < 2:
            return [] 
        
        total_path_cost = sp.S.Zero
        for start, end in zip(path[:-1], path[1:]):
            weight = self.get_weight(start, end)
            total_path_cost+=weight
        
        expanded_cost = sp.expand(total_path_cost)

        # Extract individual additive terms
        terms = expanded_cost.as_ordered_terms()

        term_contributions = []
        for term in terms:
            # Substitute variables and evaluate to a float
            substituted_term = term.subs(subs_dict).evalf()
            try:
                # We try to convert it to float
                evaluated_value = float(substituted_term)
            except TypeError:
                missing_symbols = substituted_term.free_symbols
                raise ValueError(f"Missing numerical values for symbols: {missing_symbols} in term '{term}'")
            
            term_contributions.append((term, evaluated_value))

        # Sort the terms by their numerical contribution in descending order
        term_contributions.sort(key=lambda x: x[1], reverse=True)

        return term_contributions