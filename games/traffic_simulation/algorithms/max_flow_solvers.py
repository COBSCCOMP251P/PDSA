import collections  # Used for deque (faster BFS queues)
import random  # Used for generating random capacities
import sys  # Used to set recursion limit for Dinic's DFS
import unittest  # Used for unit testing

# Set recursion limit higher for potentially deep DFS in Dinic's Algorithm
sys.setrecursionlimit(2000)

#--------------------------------------------------------------------------------------#
# Section 02 - Graph structure and Constants 
#--------------------------------------------------------------------------------------#

# The specified network edges
# Defines how the each nodes are connected to the network
GRAPH_EDGES = [
    ('A', 'B'), ('A', 'C'), ('A', 'H'), 
    ('B', 'D'), 
    ('C', 'D'), ('C', 'E'), 
    ('D', 'F'), ('D', 'G'), ('D', 'T'),
    ('E', 'F'), ('E', 'G'),
    ('F', 'T'), ('G', 'T')
]

# All nodes for initialization 
ALL_NODES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'T']
SOURCE = 'A'
SINK = 'T'

#--------------------------------------------------------------------------------------#
# Section 03 - Graph Generation Function 
#--------------------------------------------------------------------------------------#

def create_random_graph():
    """
    Creates the graph structure with randomized edge capacities (integer 5-15).
    Returns: A dictionary representing the capacity graph and the elements for Cytoscape.js.
    """
    
    # Initialized an empty graph spaces for all the nodes
    final_graph = {node: {} for node in ALL_NODES}
    cytoscape_elements = []

    # 1. Add all nodes first for visualization
    for node_id in ALL_NODES:
        cytoscape_elements.append({'group': 'nodes', 'data': {'id': node_id, 'label': node_id}})

    # 2. Add edges with randomized capacity
    for u, v in GRAPH_EDGES:
        capacity = random.randint(5, 15)
        
        # Populate/Stores capacity into graph for algorithm
        final_graph[u][v] = capacity
        
        # Prepare data for Cytoscape.js visualization
        cytoscape_elements.append({
            'group': 'edges',
            'data': {
                'id': f'{u}{v}',
                'source': u,
                'target': v,
                'capacity': capacity 
            }
        })
    
    return final_graph, cytoscape_elements

#--------------------------------------------------------------------------------------#
# Section 04 - Edmonds-Karp Implementation 
#--------------------------------------------------------------------------------------#

def bfs_edmonds_karp(r_graph, s, t, parent):
    """
    Finds an augmenting path in the residual graph using BFS.
    Only travels through residual capacity > 0.
    """
    # Use keys of r_graph to get the correct set of nodes for the graph being processed
    visited = {node: False for node in r_graph}
    queue = collections.deque([s])
    visited[s] = True
    
    while queue:
        u = queue.popleft()
        for v, cap in r_graph[u].items():
            if not visited.get(v) and cap > 0:
                queue.append(v)
                visited[v] = True
                parent[v] = u
                if v == t:
                    return True
    return False

def edmonds_karp(capacity_graph, source, sink):
    """
    Main function for Edmonds-Karp Algorithm.
    Finds Max Flow by repeatedly finding augmenting paths using BFS.
    """
    flow = 0
    # 1. Copy the initial capacity graph to use as the residual graph
    residual_graph = {u: capacity_graph[u].copy() for u in capacity_graph}
    nodes = list(capacity_graph.keys()) # Identify nodes in the current graph

    # 2. Initialize all required reverse edges to 0 capacity.
    # This block replaces the problematic loop that used the global ALL_NODES.
    for u in nodes:
        if u not in residual_graph:
            residual_graph[u] = {}
        
        # Iterate over existing forward edges (u, v)
        for v in capacity_graph.get(u, {}):
            if v not in residual_graph: # Safety check for node v
                residual_graph[v] = {}
            
            # If the reverse edge (v, u) doesn't exist, initialize its residual capacity to 0
            if u not in residual_graph[v]:
                residual_graph[v][u] = 0
    
    while True:
        parent = {}
        if not bfs_edmonds_karp(residual_graph, source, sink, parent):
            break
            
        # Find bottleneck capacity
        path_flow = float('inf')
        v = sink
        
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual_graph[u].get(v, 0))
            v = u
            
        # Augment flow and update residual capacities
        flow += path_flow
        v = sink
        while v != source:
            u = parent[v]
            # Forward edge capacity decreases
            residual_graph[u][v] -= path_flow
            # Backward edge capacity increases (allowing flow cancellation)
            residual_graph[v][u] = residual_graph[v].get(u, 0) + path_flow
            v = u

    return flow, residual_graph

#--------------------------------------------------------------------------------------#
# Section 05 - Dinic's Algorithm Implementation 
#--------------------------------------------------------------------------------------#

def bfs_dinic(r_graph, s, t, level):
    """
    Constructs the Level Graph using BFS.
    Assigns a level number to each node. Returns TRUE if sink is reachable.
    """
    level.clear()
    level[s] = 0
    queue = collections.deque([s])
    
    while queue:
        u = queue.popleft()
        for v, cap in r_graph[u].items():
            # Check for residual capacity and ensure we move to an unvisited node (v not in level)
            if cap > 0 and v not in level:
                level[v] = level[u] + 1
                queue.append(v)
                
    # Return True if the sink (t) is reachable
    return t in level

def dfs_dinic(r_graph, u, t, pushed_flow, level, ptr):
    """
    Finds an Augmenting Flow path using DFS within the Level Graph.
    Uses 'ptr' optimization (Edge Echelon).
    """
    if pushed_flow == 0 or u == t:
        return pushed_flow

    # Get neighbors safely
    neighbors = list(r_graph.get(u, {}).keys())
    
    # We iterate using index 'i' to update the pointer 'ptr[u]'
    while ptr[u] < len(neighbors):
        v = neighbors[ptr[u]]
        cap = r_graph[u].get(v, 0)
        
        # Check edge capacity and ensure the edge is level-compatible (level[v] == level[u] + 1)
        if cap > 0 and v in level and level[v] == level[u] + 1:
            # Recursively find the bottleneck flow through this path
            tr = dfs_dinic(r_graph, v, t, min(pushed_flow, cap), level, ptr)
            
            if tr > 0:
                # Augment flow and update residual capacities
                r_graph[u][v] -= tr
                r_graph[v][u] = r_graph[v].get(u, 0) + tr
                return tr
        
        # If no flow pushed through this neighbor, move ptr forward
        ptr[u] += 1
            
    return 0

def dinics_algorithm(capacity_graph, source, sink):
    """
    Runs Dinic's Max Flow algorithm.
    """
    flow = 0
    # 1. Copy the initial capacity graph to use as the residual graph
    residual_graph = {u: capacity_graph[u].copy() for u in capacity_graph}
    nodes = list(capacity_graph.keys()) # Identify nodes in the current graph
    level = {}
    
    # 2. Initialize all required reverse edges to 0 capacity.
    # This block replaces the problematic loop that used the global ALL_NODES.
    for u in nodes:
        if u not in residual_graph:
            residual_graph[u] = {}
        
        # Iterate over existing forward edges (u, v)
        for v in capacity_graph.get(u, {}):
            if v not in residual_graph: # Safety check for node v
                residual_graph[v] = {}
            
            # If the reverse edge (v, u) doesn't exist, initialize its residual capacity to 0
            if u not in residual_graph[v]:
                residual_graph[v][u] = 0
    
    # Loop over phases
    while bfs_dinic(residual_graph, source, sink, level):
        # Pointer to keep track of next edge to explore for each node (optimization)
        ptr = {node: 0 for node in nodes}

        # Find the Blocking Flow in the current phase
        while True:
            # We use float('inf') as the initial flow limit for the DFS
            pushed_flow = dfs_dinic(residual_graph, source, sink, float('inf'), level, ptr)

            if pushed_flow == 0:
                break
            flow += pushed_flow
            
    return flow, residual_graph

#--------------------------------------------------------------------------------------#
# Section 06 - Min-Cut Calculation 
#--------------------------------------------------------------------------------------#

def find_min_cut_nodes(residual_graph, source):
    """
    Finds all nodes reachable from the source (S-set) in the final residual graph.
    The min-cut edges are those connecting an S-set node to a non-S-set node.
    """
    # Use keys of residual_graph to get the correct set of nodes
    reachable = {node: False for node in residual_graph}
    queue = collections.deque([source])
    reachable[source] = True

    while queue:
        u = queue.popleft()
        for v, cap in residual_graph.get(u, {}).items():
            # If a path with residual capacity > 0 exists
            if not reachable.get(v) and cap > 0:
                reachable[v] = True
                queue.append(v)

    # Returns the list of nodes that are reachable (S-set)
    return [node for node, status in reachable.items() if status]


#--------------------------------------------------------------------------------------#
# Section 07 - Unit Tests 
#--------------------------------------------------------------------------------------#

# Define a simple, fixed graph for deterministic testing
# S->1 (10), S->2 (10), 1->2 (2), 1->T (8), 2->T (10)
# Expected Max Flow: 18 (S-1-T: 8, S-2-T: 10)
# Min-Cut: (S, 1, 2) | (T) - Cut edges: (1->T), (2->T)
FIXED_TEST_GRAPH = {
    'S': {'1': 10, '2': 10},
    '1': {'2': 2, 'T': 8},
    '2': {'T': 10},
    'T': {}
}
FIXED_TEST_NODES = ['S', '1', '2', 'T']
FIXED_TEST_SOURCE = 'S'
FIXED_TEST_SINK = 'T'
FIXED_MAX_FLOW = 18

class TestMaxFlowAlgorithms(unittest.TestCase):
    """Unit tests for the Max Flow and Min Cut implementations."""
    
    def test_random_graph_generation(self):
        """Test that the random graph structure is correct and capacities are within bounds."""
        
        # Temporarily fix the random seed for deterministic testing of the structure
        random.seed(42)
        graph, elements = create_random_graph()

        # 1. Check graph structure (must contain all required edges)
        for u, v in GRAPH_EDGES:
            self.assertIn(v, graph[u], f"Edge {u}->{v} missing from graph structure.")
            capacity = graph[u][v]
            self.assertTrue(5 <= capacity <= 15, f"Capacity {capacity} out of bounds (5-15).")
            
        # 2. Check Cytoscape elements structure (correct number of elements)
        expected_elements = len(ALL_NODES) + len(GRAPH_EDGES)
        self.assertEqual(len(elements), expected_elements, "Incorrect number of Cytoscape elements generated.")
        
        # 3. Check node/edge count
        node_count = sum(1 for el in elements if el['group'] == 'nodes')
        edge_count = sum(1 for el in elements if el['group'] == 'edges')
        self.assertEqual(node_count, len(ALL_NODES), "Incorrect node count.")
        self.assertEqual(edge_count, len(GRAPH_EDGES), "Incorrect edge count.")

    def test_edmonds_karp_fixed_graph(self):
        """Test Edmonds-Karp Max Flow against a known result."""
        
        flow, residual_graph = edmonds_karp(FIXED_TEST_GRAPH, FIXED_TEST_SOURCE, FIXED_TEST_SINK)
        
        self.assertEqual(flow, FIXED_MAX_FLOW, f"Edmonds-Karp Max Flow incorrect. Expected {FIXED_MAX_FLOW}, got {flow}.")
        
        # Test Min-Cut nodes for the EK result
        min_cut_nodes = find_min_cut_nodes(residual_graph, FIXED_TEST_SOURCE)
        self.assertCountEqual(min_cut_nodes, ['S', '1', '2'], "Min-Cut nodes (S-set) incorrect for Edmonds-Karp.")

    def test_dinics_algorithm_fixed_graph(self):
        """Test Dinic's Algorithm Max Flow against a known result."""
        
        flow, residual_graph = dinics_algorithm(FIXED_TEST_GRAPH, FIXED_TEST_SOURCE, FIXED_TEST_SINK)
        
        self.assertEqual(flow, FIXED_MAX_FLOW, f"Dinic's Algorithm Max Flow incorrect. Expected {FIXED_MAX_FLOW}, got {flow}.")

        # Test Min-Cut nodes for the Dinic result
        min_cut_nodes = find_min_cut_nodes(residual_graph, FIXED_TEST_SOURCE)
        self.assertCountEqual(min_cut_nodes, ['S', '1', '2'], "Min-Cut nodes (S-set) incorrect for Dinic's Algorithm.")

    def test_min_cut_after_max_flow_is_equal(self):
        """Ensure both algorithms yield the exact same Max Flow result."""
        
        ek_flow, _ = edmonds_karp(FIXED_TEST_GRAPH, FIXED_TEST_SOURCE, FIXED_TEST_SINK)
        dinic_flow, _ = dinics_algorithm(FIXED_TEST_GRAPH, FIXED_TEST_SOURCE, FIXED_TEST_SINK)
        
        self.assertEqual(ek_flow, dinic_flow, "Edmonds-Karp and Dinic's algorithms yielded different Max Flow results.")

# Standard boilerplate to run the tests if the script is executed directly
if __name__ == '__main__':
    # Print a message before running to confirm the script reached this point
    print("\n--- Starting Max Flow Algorithm Unit Tests ---")
    
    # Use TextTestRunner to explicitly force output to sys.stdout
    # verbosity=2 provides more detailed output (running test names)
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    
    # Discover and run all tests in the current module
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner.run(suite)