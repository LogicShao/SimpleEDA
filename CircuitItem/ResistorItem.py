from .BasicCircuitItem import BasicCircuitItem, CircuitNode, ItemInfo
from common_import import *


class ResistorSymbol(qtw.QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.width = 60
        self.height = 20

    def getPoints(self) -> list[qtc.QPointF]:
        points = []
        # 左边起点
        points.append(qtc.QPointF(0, self.height / 2))
        sideLineWidth = 10
        # 绘制折线
        zigzag_cnt = 8
        zigzag_dx = (self.width - 2 * sideLineWidth) / zigzag_cnt
        zigzag_dy = self.height / 2
        begin_x = 0 + sideLineWidth
        begin_y = self.height / 2
        points.append(qtc.QPointF(begin_x, begin_y))
        for i in range(1, zigzag_cnt):
            x = begin_x + i * zigzag_dx
            y = begin_y + zigzag_dy if i % 2 == 0 else begin_y - zigzag_dy
            points.append(qtc.QPointF(x, y))
        points.append(qtc.QPointF(self.width - sideLineWidth, self.height / 2))
        # 右边终点
        points.append(qtc.QPointF(self.width, self.height / 2))
        return points

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        # 绘制 zig-zag 线（电阻符号）
        points = self.getPoints()
        for point1, point2 in zip(points[:-1], points[1:]):
            painter.drawLine(point1, point2)

    def getNodesPos(self) -> list[qtc.QPointF]:
        # 获取电阻两端的节点
        return [qtc.QPointF(0, self.height / 2),
                qtc.QPointF(self.width, self.height / 2)]


class ResistorItem(BasicCircuitItem):
    def __init__(self, resistance: float = 10):
        super().__init__()

        self.resistorSymbol = ResistorSymbol()
        self.resistorSymbol.setParentItem(self)

        self.nodes_pos = self.resistorSymbol.getNodesPos()
        self.nodes = [CircuitNode(pos) for pos in self.nodes_pos]
        for node in self.nodes:
            node.setParentItem(self)

        self.width = self.resistorSymbol.width + 2 * self.nodes[0].radius
        self.height = self.resistorSymbol.height

        self.resistance = resistance
        self.resistanceInfo = ItemInfo(
            text='{:.0f}Ω'.format(self.resistance),
            position=qtc.QPointF(0, -self.height / 2 - 10)
        )
        self.resistanceInfo.setParentItem(self)

        logger.info('添加 {:.0f}Ω 电阻'.format(self.resistance))

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def modifyItem(self):
        logger.info('修改电阻')

    def deleteItem(self):
        logger.info('删除电阻')
        self.scene().removeItem(self)
