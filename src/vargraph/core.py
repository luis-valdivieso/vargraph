class VarGraph:
    def __init__(self, directed=False):
        self.directed = directed
        self.graph = {}

    def add_node(self, node):
        """Adds an isolated node if it doesn't exist previously"""
        if node not in self.graph:
            self.graph[node] = {}

    def add_edge(self, u, v, weight=1):
        """Adds an edge between u and v with a weight"""
        # If the nodes are new, we initialize the internal dictionaries
        self.add_node(u)
        self.add_node(v)
            
        # Create u-v connection
        self.graph[u][v] = weight
        
        # If the graph is not directed, we create the v-u connection
        if not self.directed:
            self.graph[v][u] = weight