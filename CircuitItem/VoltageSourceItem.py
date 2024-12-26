from .BasicCircuitItem import BasicCircuitItem, CircuitNode, ItemInfo
from common_import import *


class VoltageSourceSymbol(qtw.QGraphicsItem):
    # 直流电压源
    def __init__(self):
        super().__init__()
        self.size = 45
        self.radius = self.size * 0.25

    def boundingRect(self):
        return qtc.QRectF(-self.size / 2, -self.size / 2, self.size, self.size)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.setBrush(qtg.QBrush(
            qtc.Qt.GlobalColor.white, qtc.Qt.BrushStyle.NoBrush))
        painter.drawEllipse(qtc.QPointF(0, 0), self.radius, self.radius)
        painter.drawLine(qtc.QPointF(-self.size / 2, 0),
                         qtc.QPointF(self.size / 2, 0))

    def getNodesPos(self) -> list[qtc.QPointF]:
        # 获取电压源两端的节点
        return [qtc.QPointF(-self.size / 2, 0),
                qtc.QPointF(self.size / 2, 0)]


class VoltageSourceItem(BasicCircuitItem):
    def __init__(self, voltage: float = 10):
        super().__init__()

        self.voltageSourceSymbol = VoltageSourceSymbol()
        self.voltageSourceSymbol.setParentItem(self)

        self.nodes_pos = self.voltageSourceSymbol.getNodesPos()
        self.nodes = [CircuitNode(pos) for pos in self.nodes_pos]
        for node in self.nodes:
            node.setParentItem(self)

        self.width = self.voltageSourceSymbol.size + 2 * self.nodes[0].radius
        self.height = self.voltageSourceSymbol.size

        self.voltage = voltage
        self.voltageInfo = ItemInfo(
            text=f'{self.voltage}V',
            position=qtc.QPointF(-self.width / 2, -self.height / 2 - 10)
        )
        self.voltageInfo.setParentItem(self)

        logger.info('添加 {}V 电压源'.format(self.voltage))

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass

    def modifyItem(self):
        logger.info('修改电压源')

    def deleteItem(self):
        logger.info('删除电压源')
        self.scene().removeItem(self)
