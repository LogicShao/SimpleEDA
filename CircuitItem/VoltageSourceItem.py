from .BasicCircuitItem import BasicCircuitItem

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc


class VoltageSourceItem(BasicCircuitItem):
    # 直流电压源
    def __init__(self):
        super().__init__()
        self.size = 40
        self.radius = self.size * 0.3

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

    def getNodes(self) -> list[qtc.QPointF]:
        # 获取电压源两端的节点
        return [qtc.QPointF(-self.size / 2, 0),
                qtc.QPointF(self.size / 2, 0)]
