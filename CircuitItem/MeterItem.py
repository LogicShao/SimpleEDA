from .BaseCircuitItem import BaseCircuitItem, CircuitNode
from common_import import *


class VoltmeterSymbol(qtw.QGraphicsItem):
    def __init__(self):
        super().__init__()

        self.size = 60
        self.margin = 15
        self.radius = self.size / 2 - self.margin

    def boundingRect(self):
        return qtc.QRectF(-self.size / 2, -self.size / 2, self.size, self.size)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.red,
                         qtc.Qt.BrushStyle.NoBrush))

        painter.drawEllipse(qtc.QPointF(0, 0), self.radius, self.radius)

        # 绘制 V 字符
        width_factor = 0.35
        height_factor = 0.85
        V_width = self.radius * width_factor
        V_height = self.radius * height_factor
        painter.drawLine(qtc.QPointF(0, V_height / 2),
                         qtc.QPointF(V_width, -V_height / 2))
        painter.drawLine(qtc.QPointF(0, V_height / 2),
                         qtc.QPointF(-V_width, -V_height / 2))

        # 绘制两条边线
        painter.drawLine(qtc.QPointF(-self.size / 2, 0),
                         qtc.QPointF(-self.radius, 0))
        painter.drawLine(qtc.QPointF(self.size / 2, 0),
                         qtc.QPointF(self.radius, 0))

    def getNodePos(self):
        return [qtc.QPointF(-self.size / 2, 0), qtc.QPointF(self.size / 2, 0)]


class VoltmeterItem(BaseCircuitItem):
    @staticmethod
    def What() -> str:
        return '电压表'

    def __init__(self):
        super().__init__()

        self.voltmeterSymbol = VoltmeterSymbol()
        self.voltmeterSymbol.setParentItem(self)

        self.nodes = [CircuitNode(pos)
                      for pos in self.voltmeterSymbol.getNodePos()]
        for node in self.nodes:
            node.setParentItem(self)

        self.width = self.voltmeterSymbol.size + self.nodes[0].radius
        self.height = self.voltmeterSymbol.size

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass


class AmmeterSymbol(qtw.QGraphicsItem):
    def __init__(self):
        super().__init__()

        self.size = 60
        self.margin = 15
        self.radius = self.size / 2 - self.margin

    def boundingRect(self):
        return qtc.QRectF(-self.size / 2, -self.size / 2, self.size, self.size)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.red,
                         qtc.Qt.BrushStyle.NoBrush))

        painter.drawEllipse(qtc.QPointF(0, 0), self.radius, self.radius)

        # 绘制 A 字符
        width_factor = 0.4
        height_factor = 0.85
        A_width = self.radius * width_factor
        A_height = self.radius * height_factor
        painter.drawLine(qtc.QPointF(-A_width, A_height / 2),
                         qtc.QPointF(0, -A_height / 2))
        painter.drawLine(qtc.QPointF(A_width, A_height / 2),
                         qtc.QPointF(0, -A_height / 2))
        painter.drawLine(qtc.QPointF(-A_width / 2, A_height / 4),
                         qtc.QPointF(A_width / 2, A_height / 4))

        # 绘制两条边线
        painter.drawLine(qtc.QPointF(-self.size / 2, 0),
                         qtc.QPointF(-self.radius, 0))
        painter.drawLine(qtc.QPointF(self.size / 2, 0),
                         qtc.QPointF(self.radius, 0))

    def getNodePos(self):
        return [qtc.QPointF(-self.size / 2, 0), qtc.QPointF(self.size / 2, 0)]


class AmmeterItem(BaseCircuitItem):
    @staticmethod
    def What() -> str:
        return '电流表'

    def __init__(self):
        super().__init__()

        self.ammeterSymbol = AmmeterSymbol()
        self.ammeterSymbol.setParentItem(self)

        self.nodes = [CircuitNode(pos)
                      for pos in self.ammeterSymbol.getNodePos()]
        for node in self.nodes:
            node.setParentItem(self)

        self.width = self.ammeterSymbol.size + self.nodes[0].radius
        self.height = self.ammeterSymbol.size

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass
