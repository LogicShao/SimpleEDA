from .BaseCircuitItem import CircuitNode, BaseCircuitItem
import sympy as sp


class CircuitTopology:
    nodes: list[CircuitNode]
    edges: dict[CircuitNode, list[tuple[CircuitNode, BaseCircuitItem]]]

    def __init__(self):
        self.nodes = []
        self.edges = []

    def addNode(self, node: CircuitNode):
        self.nodes.append(node)

    def addEdge(self, node1: CircuitNode, node2: CircuitNode, item: BaseCircuitItem):
        self.edges.get(node1, []).append((node2, item))

    def getNodeEquations(self):
        equations = []
        for node in self.nodes:
            equation = sp.Eq(0, 0)
            for edge in self.edges.get(node, []):
                equation += edge[1].getEquation(edge[0])
            equations.append(equation)
        return equations
