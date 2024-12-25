import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc


class BasicCircuitItem(qtw.QGraphicsItem):
    def __init__(self):
        super().__init__()
        # 设置图元可被选中和移动
        self.setFlags(
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key.Key_Delete:
            scene = self.scene()
            if scene:
                scene.removeItem(self)
        else:
            super().keyPressEvent(event)


class CircuitNode(qtw.QGraphicsItem):
    def __init__(self, pos: qtc.QPointF):
        super().__init__()
        self.pos = pos
        self.setPos(pos)
        self.radius = 5

    def boundingRect(self):
        return qtc.QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.darkBlue, 2)
        painter.setPen(pen)
        painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.darkBlue))
        painter.drawEllipse(qtc.QPointF(0, 0), self.radius, self.radius)
