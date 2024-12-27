from .BaseCircuitItem import BaseCircuitItem, CircuitNode, ItemInfo
from common_import import *


class VoltageSourceSymbol(qtw.QGraphicsItem):
    # 直流电压源
    def __init__(self):
        super().__init__()
        self.size = 60
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


class VoltageSourceItem(BaseCircuitItem):
    @staticmethod
    def What() -> str:
        return '电压源'

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

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass

    def modifyItem(self):
        logger.info('修改电压源')

    def deleteItem(self):
        logger.info('删除电压源')
        self.scene().removeItem(self)


class CurrentSourceSymbol(qtw.QGraphicsItem):
    # 直流电流源
    def __init__(self):
        super().__init__()
        self.size = 60
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
                         qtc.QPointF(-self.radius, 0))
        painter.drawLine(qtc.QPointF(self.radius, 0),
                         qtc.QPointF(self.size / 2, 0))
        painter.drawLine(qtc.QPointF(0, self.radius),
                         qtc.QPointF(0, -self.radius))

    def getNodesPos(self) -> list[qtc.QPointF]:
        # 获取电流源两端的节点
        return [qtc.QPointF(-self.size / 2, 0),
                qtc.QPointF(self.size / 2, 0)]


class CurrentSourceItem(BaseCircuitItem):
    @staticmethod
    def What() -> str:
        return '电流源'

    def __init__(self, current: float = 10):
        super().__init__()

        self.currentSourceSymbol = CurrentSourceSymbol()
        self.currentSourceSymbol.setParentItem(self)

        self.nodes_pos = self.currentSourceSymbol.getNodesPos()
        self.nodes = [CircuitNode(pos) for pos in self.nodes_pos]
        for node in self.nodes:
            node.setParentItem(self)

        self.width = self.currentSourceSymbol.size + 2 * self.nodes[0].radius
        self.height = self.currentSourceSymbol.size

        self.current = current
        self.currentInfo = ItemInfo(
            text=f'{self.current}A',
            position=qtc.QPointF(-self.width / 2, -self.height / 2 - 10)
        )
        self.currentInfo.setParentItem(self)

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass


class GroundSymbol(qtw.QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.width = 40
        self.height = 20

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.red))
        painter.drawLine(qtc.QPointF(0, 0), qtc.QPointF(0, self.height))
        painter.drawLine(qtc.QPointF(-self.width / 2, self.height),
                         qtc.QPointF(self.width / 2, self.height))

    def getNodesPos(self) -> list[qtc.QPointF]:
        return [qtc.QPointF(0, 0)]


class GroundItem(BaseCircuitItem):
    @staticmethod
    def What() -> str:
        return '接地'

    def __init__(self):
        super().__init__()

        self.groundSymbol = GroundSymbol()
        self.groundSymbol.setParentItem(self)

        self.nodes_pos = self.groundSymbol.getNodesPos()
        self.nodes = [CircuitNode(pos) for pos in self.nodes_pos]
        for node in self.nodes:
            node.setParentItem(self)

        self.width = self.groundSymbol.width
        self.height = self.groundSymbol.height + self.nodes[0].radius

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass
