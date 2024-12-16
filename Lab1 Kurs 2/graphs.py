import networkx as nx


class Graph(nx.Graph):
    def __init__(self, start=None):
        super().__init__(start)

    def neighbors(self, vertex):
        return list(self.adj[vertex])

    def vertices(self):
        return list(self.nodes)

    def edges(self):
        return list(self.edges)

    def __len__(self):
        return self.number_of_nodes()

    def add_vertex(self, vertex):
        self.add_node(vertex)

    def add_edge(self, u, v):
        super().add_edge(u, v)

    def remove_vertex(self, vertex):
        self.remove_node(vertex)

    def remove_edge(self, u, v):
        self.remove_edge(u, v)

    def get_vertex_value(self, vertex):
        return self.nodes[vertex].get('value', None)

    def set_vertex_value(self, vertex, value):
        self.nodes[vertex]['value'] = value


class WeightedGraph(Graph):
    def get_weight(self, u, v):
        return self[u][v].get('weight', None)

    def set_weight(self, u, v, weight):
        self[u][v]['weight'] = weight


def costs2attributes(G, cost, attr='weight'):
    for u, v in G.edges:
        G[u][v][attr] = cost(u, v)


def dijkstra(graph, source, cost=lambda u, v: 1):
    costs2attributes(graph, cost)
    paths = nx.shortest_path(graph, source=source, weight='weight')
    return {target: path for target, path in paths.items()}


def visualize(graph, view='dot', name='mygraph', nodecolors={}, engine='dot'):
    from graphviz import Digraph

    dot = Digraph(name=name, engine=engine)
    for node in graph.nodes:
        color = nodecolors.get(str(node), 'white')
        dot.node(str(node), color=color, style='filled')
    for u, v in graph.edges:
        dot.edge(str(u), str(v))

    if view == 'view':
        dot.view()
    return dot
