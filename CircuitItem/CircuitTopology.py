from log_config import logger

import CircuitItem as CI
import sympy as sp


class NoGNDNodeError(Exception):
    def __init__(self):
        super().__init__('电路没有接地')


class CircuitTopology:
    def __init__(self, item_nodes: set[CI.ItemNode]):
        self.s = sp.symbols('s', complex=True)
        self.circuit_nodes = self.getCircuitNodes(item_nodes)

        self.items = set(node.parentItem() for node in item_nodes)
        self.notGNDNodes = sorted(
            node for node in self.circuit_nodes if not node.isGround)
        self.notGNDNodeToIndex = {node: i for i,
                                  node in enumerate(self.notGNDNodes)}
        self.voltageSources = sorted(
            item for item in self.items if isinstance(item, CI.VoltageSourceItem))
        self.voltageSourceToIndex = {item: i for i,
                                     item in enumerate(self.voltageSources)}

        self.adjacency_list = self.getAdjacencyList()

        self.t = sp.symbols('t', real=True)
        self.solution = self.solve_MNA_matrix()
        for node, pot in zip(self.notGNDNodes, self.solution):
            node.potential = pot
            logger.info('{}: {}'.format(node.getName(), pot))
        for gnd_node in (node for node in self.circuit_nodes if node.isGround):
            gnd_node.potential = 0
            logger.info('{}: {}'.format(gnd_node.getName(), 0))
        for item, cur in zip(self.voltageSources, self.solution[self.getNumOfNotGND():]):
            item.current = cur
            logger.info('{}: {}'.format(item.getName(), cur))

    def getAdjacencyList(self) -> dict[CI.CircuitNode, set[tuple[CI.CircuitNode, CI.BaseCircuitItem]]]:
        # 构建 (节点, (连接节点, 元件)) 的邻接表
        adj = {node: set() for node in self.circuit_nodes}
        for node in self.circuit_nodes:
            for item in node.connect_items:
                for connect_node in item.getCircuitNodes():
                    if connect_node != node:
                        adj[node].add((connect_node, item))
        return adj

    def __str__(self):
        node_info = '电路节点：\n'
        for node in self.circuit_nodes:
            info = node.getName() + ":"
            for to_node, item in self.adjacency_list[node]:
                info += ' {}({})'.format(to_node.getName(), item.getName())
            node_info += info + '\n'

        item_info = '电路元件：\n'
        for item in self.items:
            info = item.getName()
            info += ': [{}]'.format(','.join(circuit_node.getName()
                                             for circuit_node in item.getCircuitNodes()))
            item_info += info + '\n'

        return '电路拓扑:\n{}\n{}'.format(node_info, item_info)

    def findItemNodesOfSamePotential(self, item_node: CI.ItemNode, visited: set[CI.ItemNode]) -> list[CI.ItemNode]:
        if item_node in visited:
            return []
        visited.add(item_node)
        item_nodes = [item_node]
        for connect_node in item_node.getConnectItemNodes():
            item_nodes += self.findItemNodesOfSamePotential(
                connect_node, visited)
            connect_item = connect_node.parentItem()
            if isinstance(connect_item, CI.AmmeterItem):
                item_nodes += self.findItemNodesOfSamePotential(
                    connect_item.getAnotherNode(connect_node), visited)
        return item_nodes

    def getCircuitNodes(self, item_nodes: set[CI.ItemNode]) -> list[CI.CircuitNode]:
        visited = set()
        circuit_nodes = []
        for item_node in item_nodes:
            if item_node in visited:
                continue
            circuit_node = CI.CircuitNode()
            circuit_nodes.append(circuit_node)
            item_nodes_of_same_potential = self.findItemNodesOfSamePotential(
                item_node, visited)
            for item_node in item_nodes_of_same_potential:
                circuit_node.addConnectItem(item_node.parentItem())
                item_node.circuitNode = circuit_node
        return circuit_nodes

    def getVoltageSourcesNum(self) -> int:
        return len(self.voltageSources)

    def getVoltageSources(self) -> list[CI.VoltageSourceItem]:
        return self.voltageSources

    def getNumOfNotGND(self) -> int:
        # 除去地节点
        return len(self.notGNDNodes)

    def getNotGNDNodes(self) -> list[CI.CircuitNode]:
        return self.notGNDNodes

    def getNodesIndex(self, node: CI.CircuitNode) -> int:
        if node.isGround:
            return None
        return self.notGNDNodeToIndex[node]

    def getVoltageSourceIndex(self, item: CI.VoltageSourceItem) -> int:
        return self.voltageSourceToIndex[item]

    def get_MNA_matrix(self):
        num_nodes = self.getNumOfNotGND()
        num_voltage_sources = self.getVoltageSourcesNum()

        if num_nodes == len(self.circuit_nodes):
            raise NoGNDNodeError()

        G = sp.zeros(num_nodes, num_nodes)
        B = sp.zeros(num_nodes, num_voltage_sources)
        D = sp.zeros(num_voltage_sources, num_voltage_sources)
        I_s = sp.zeros(num_nodes, 1)
        E = sp.zeros(num_voltage_sources, 1)

        for item in self.items:
            if isinstance(item, CI.ResistorItem):
                Y = 1 / item.resistance
            elif isinstance(item, CI.CapacitorItem):
                Y = self.s * item.capacitance
            elif isinstance(item, CI.InductorItem):
                Y = 1 / (self.s * item.inductance)
            else:
                Y = 0

            if isinstance(item, (CI.ResistorItem, CI.CapacitorItem, CI.InductorItem)):
                node1, node2 = item.getCircuitNodes()
                n1, n2 = self.getNodesIndex(node1), self.getNodesIndex(node2)
                if not node1.isGround:
                    G[n1, n1] += Y
                if not node2.isGround:
                    G[n2, n2] += Y
                if not node1.isGround and not node2.isGround:
                    G[n1, n2] -= Y
                    G[n2, n1] -= Y
            elif isinstance(item, CI.VoltageSourceItem):
                node1, node2 = item.getCircuitNodes()
                n1, n2 = self.getNodesIndex(node1), self.getNodesIndex(node2)
                voltage_index = self.getVoltageSourceIndex(item)
                if not node1.isGround:
                    B[n1, voltage_index] = 1
                if not node2.isGround:
                    B[n2, voltage_index] = -1
                E[voltage_index] = item.voltage / self.s
            elif isinstance(item, CI.CurrentSourceItem):
                node1, node2 = item.getCircuitNodes()
                n1, n2 = self.getNodesIndex(node1), self.getNodesIndex(node2)
                if not node1.isGround:
                    I_s[n1] += item.current / self.s
                if not node2.isGround:
                    I_s[n2] -= item.current / self.s

        A = sp.Matrix.vstack(
            sp.Matrix.hstack(G, B),
            sp.Matrix.hstack(B.T, D)
        )
        b = sp.Matrix.vstack(I_s, E)

        return A, b

    def solve_MNA_matrix(self):
        A, b = self.get_MNA_matrix()
        x = sp.linsolve((A, b))
        return list(x)[0]

    def output(self) -> str:
        x = self.solution
        logger.info('x: ' + str(x))

        potiential = x[:self.getNumOfNotGND()]
        current = x[self.getNumOfNotGND():]
        output = '电路节点电势：\n'
        for node, pot in zip(self.getNotGNDNodes(), potiential):
            output += '{}: {}V\n'.format(node.getName(), sp.inverse_laplace_transform(
                pot, self.s, t=self.t).simplify())
        output += '电压源电流：\n'
        for item, cur in zip(self.getVoltageSources(), current):
            output += '{}: {}A\n'.format(item.getName(), sp.inverse_laplace_transform(
                cur, self.s, t=self.t).simplify())
        return '电路求解结果：\n' + output
