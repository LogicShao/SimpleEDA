from .BasicCircuitItem import BasicCircuitItem
from .BasicCircuitItem import CircuitNode
from log_config import logger

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc


class ResistorItem(BasicCircuitItem):
    def __init__(self):
        super().__init__()
        self.width = 60
        self.height = 20
        self.points = self.getPoints()

        self.node1_pos, self.node2_pos = self.getNodes()
        self.node1 = CircuitNode(self.node1_pos)
        self.node2 = CircuitNode(self.node2_pos)
        logger.info("绘制电阻节点: ({},{}) ({},{})".
                    format(self.node1_pos.x(), self.node1_pos.y(), self.node2_pos.x(), self.node2_pos.y()))

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
        for point1, point2 in zip(self.points[:-1], self.points[1:]):
            painter.drawLine(point1, point2)

    def getNodes(self) -> list[qtc.QPointF]:
        # 获取电阻两端的节点
        return [qtc.QPointF(0, self.height / 2),
                qtc.QPointF(self.width, self.height / 2)]
