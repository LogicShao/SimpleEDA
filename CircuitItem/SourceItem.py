from .BaseCircuitItem import *
from common_import import *


class VoltageSourceSymbol(ItemSymbol):
    # 直流电压源
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__(parent=parent)
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
    _item_counter = ItemCounter()

    @staticmethod
    def What() -> str:
        return '电压源'

    def __init__(self, voltage: float = 10):
        super().__init__()

        self.mainSymbol = VoltageSourceSymbol(parent=self)
        self.nodes = [ItemNode(parent=self, position=pos)
                      for pos in self.mainSymbol.getNodesPos()]

        self.width = self.mainSymbol.size + 2 * self.nodes[0].radius
        self.height = self.mainSymbol.size

        self.voltage = voltage
        self.voltageInfo = ItemInfo(
            parent=self,
            text=f'{self.voltage}V',
            position=qtc.QPointF(0, -self.height / 2)
        )

        self.nameText = ItemInfo(
            parent=self,
            text=self.getName(),
            position=qtc.QPointF(0, self.height / 2)
        )

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass


class CurrentSourceSymbol(ItemSymbol):
    # 直流电流源
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__(parent=parent)
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
    _item_counter = ItemCounter()

    @staticmethod
    def What() -> str:
        return '电流源'

    def __init__(self, current: float = 10):
        super().__init__()

        self.mainSymbol = CurrentSourceSymbol(parent=self)
        self.nodes = [ItemNode(parent=self, position=pos)
                      for pos in self.mainSymbol.getNodesPos()]

        self.width = self.mainSymbol.size + 2 * self.nodes[0].radius
        self.height = self.mainSymbol.size

        self.current = current
        self.currentInfo = ItemInfo(
            parent=self,
            text=f'{self.current}A',
            position=qtc.QPointF(0, -self.height / 2)
        )

        self.nameText = ItemInfo(
            parent=self,
            text=self.getName(),
            position=qtc.QPointF(0, self.height / 2)
        )

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass


class GroundSymbol(ItemSymbol):
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__(parent=parent)
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
    _item_counter = ItemCounter()

    @staticmethod
    def What() -> str:
        return 'GND'

    def __init__(self):
        super().__init__()

        self.mainSymbol = GroundSymbol(parent=self)
        self.nodes = [ItemNode(parent=self, position=pos)
                      for pos in self.mainSymbol.getNodesPos()]

        self.width = self.mainSymbol.width
        self.height = self.mainSymbol.height + self.nodes[0].radius

        self.nameText = ItemInfo(
            parent=self,
            text=self.getName(),
            position=qtc.QPointF(0, self.height + 10)
        )

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pass
