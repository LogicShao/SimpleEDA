from .BasicCircuitItem import CircuitNode
from common_import import *


class WireItem(qtw.QGraphicsItem):
    def __init__(self, start: CircuitNode, end: CircuitNode):
        super().__init__()
        self.start = start
        self.end = end

        self.start.signals.positionChanged.connect(self.updatePosition)
        self.end.signals.positionChanged.connect(self.updatePosition)

        logger.info('添加导线 ({},{}) -> ({},{})'.format(
            self.start.scenePos().x(),
            self.start.scenePos().y(),
            self.end.scenePos().x(),
            self.end.scenePos().y()
        ))

    def boundingRect(self):
        x1, y1 = self.start.scenePos().x(), self.start.scenePos().y()
        x2, y2 = self.end.scenePos().x(), self.end.scenePos().y()
        return qtc.QRectF(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.drawLine(self.start.scenePos(), self.end.scenePos())

    def updatePosition(self):
        self.prepareGeometryChange()
        self.update()
