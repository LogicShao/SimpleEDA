from log_config import logger

import CircuitItem as CI
import numpy as np


class NoGNDNodeError(Exception):
    def __init__(self):
        super().__init__('电路没有接地')


class CircuitTopology:
    def __init__(self, item_nodes: set[CI.ItemNode]):
        self.circuit_nodes = self.getCircuitNodes(item_nodes)
        self.items = set(item_node.parentItem()
                         for item_node in item_nodes)
        self.adjacency_list = self.getAdjacencyList()

    def getAdjacencyList(self) -> dict[CI.CircuitNode, set[tuple[CI.CircuitNode, CI.BaseCircuitItem]]]:
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

                logger.info('添加元件 {} 到节点 {}'.format(
                    item_node.parentItem().getName(), circuit_node.getName()))

                item_node.circuitNode = circuit_node
                logger.info('元件 {} 的节点为 {}'.format(
                    item_node.parentItem().getName(), circuit_node.getName()))

        return circuit_nodes

    def getVoltageSourcesNum(self) -> int:
        return sum(1 for item in self.items if isinstance(item, CI.VoltageSourceItem))

    def getVoltageSources(self) -> list[CI.VoltageSourceItem]:
        return sorted((item for item in self.items if isinstance(item, CI.VoltageSourceItem)))

    def getNumOfNotGND(self) -> int:
        # 除去地节点
        return sum(1 for node in self.circuit_nodes if not node.isGround)

    def getNotGNDNodes(self) -> list[CI.CircuitNode]:
        return [node for node in self.circuit_nodes if not node.isGround]

    def get_MNA_matrix(self):
        num_nodes = self.getNumOfNotGND()
        num_voltage_sources = self.getVoltageSourcesNum()

        if num_nodes == len(self.circuit_nodes):
            raise NoGNDNodeError()

        logger.info('节点数：{}'.format(num_nodes))
        logger.info('电压源数：{}'.format(num_voltage_sources))

        G = np.zeros((num_nodes, num_nodes))
        B = np.zeros((num_nodes, num_voltage_sources))
        D = np.zeros((num_voltage_sources, num_voltage_sources))
        I_s = np.zeros(num_nodes)
        E = np.zeros(num_voltage_sources)

        for item in self.items:
            if isinstance(item, CI.ResistorItem):
                node1, node2 = item.getCircuitNodes()
                n1, n2 = node1.item_id - 1, node2.item_id - 1
                g = 1 / item.resistance
                if not node1.isGround:
                    G[n1, n1] += g
                if not node2.isGround:
                    G[n2, n2] += g
                if not node1.isGround and not node2.isGround:
                    G[n1, n2] -= g
                    G[n2, n1] -= g
            elif isinstance(item, CI.VoltageSourceItem):
                node1, node2 = item.getCircuitNodes()
                n1, n2 = node1.item_id - 1, node2.item_id - 1
                voltage_index = item.item_id - 1
                if not node1.isGround:
                    B[n1, voltage_index] = 1
                if not node2.isGround:
                    B[n2, voltage_index] = -1
                E[voltage_index] = item.voltage

        A = np.block([[G, B], [B.T, D]])
        b = np.block([I_s, E])

        return A, b

    def solve_MNA_matrix(self):
        A, b = self.get_MNA_matrix()
        x = np.linalg.solve(A, b)
        return x

    def output(self) -> str:
        x = self.solve_MNA_matrix()

        logger.info('x: ' + str(x))

        potiential = x[:self.getNumOfNotGND()]
        current = x[self.getNumOfNotGND():]
        output = '电路节点电势：\n'
        for node, pot in zip(self.getNotGNDNodes(), potiential):
            output += '{}: {:.2f}V\n'.format(node.getName(), pot)
        output += '电压源电流：\n'
        for item, cur in zip(self.getVoltageSources(), current):
            output += '{}: {:.2f}A\n'.format(item.getName(), cur)
        return '电路求解结果：\n' + output
