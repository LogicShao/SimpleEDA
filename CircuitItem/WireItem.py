from .BasicCircuitItem import BasicCircuitItem

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc


class WireItem(BasicCircuitItem):
    def __init__(self, start: qtc.QPointF, end: qtc.QPointF):
        super().__init__()
        self.start = start
        self.end = end

    def boundingRect(self):
        return qtc.QRectF(self.start, self.end)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.black, 2)
        painter.setPen(pen)
        painter.drawLine(self.start, self.end)
