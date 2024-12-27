from common_import import *
import sympy as sp
import CircuitItem as CI


class _CircuitEdge:
    start: CI.BaseCircuitItem
    end: CI.BaseCircuitItem

    def __init__(self, start: CI.BaseCircuitItem, end: CI.BaseCircuitItem):
        self.start = start
        self.end = end


class CircuitEdge:
    start: CI.CircuitNode
    end: CI.CircuitNode
    item: CI.BaseCircuitItem

    def __init__(self, start: CI.CircuitNode, end: CI.CircuitNode, item: CI.BaseCircuitItem):
        self.start = start
        self.end = end
        self.item = item


class CircuitTopology:
    _G: dict[CI.ItemNode, list[_CircuitEdge]]
    G: dict[CI.CircuitNode, list[CircuitEdge]]

    def __init__(self, wires: list[CI.WireItem]):
        self._G = {}
        for wire in wires:
            start, end = wire.start_item(), wire.end_item()
            self.addEdge(start, end)
            self.addEdge(end, start)

    def addEdge(self, start: CI.BaseCircuitItem, end: CI.BaseCircuitItem):
        if start not in self._G:
            self._G[start] = []
        self._G[start].append(_CircuitEdge(start, end))

        self.G = self.point_edge_transform()

        logger.info('添加电路拓扑 ({}) -> ({})'.format(
            start.getName(),
            end.getName()
        ))

    def point_edge_transform(self) -> dict[CI.CircuitNode, list[CircuitEdge]]:
        self.G = {}
        for start, edges in self._G.items():
            if start not in self.G:
                self.G[start] = []
            for edge in edges:
                self.G[start].append(CircuitEdge(start, edge.end, edge.end))
        return self.G


class Solver:
    def __init__(self, topo: CircuitTopology):
        self.topo = topo

    def solve(self):
        logger.info('开始求解电路')
        # 电路方程
        # 电压源
        # 电阻
        # 电流源
        # 电容
        # 电感
        # 电路方程组
        # 电路方程求解
        #
