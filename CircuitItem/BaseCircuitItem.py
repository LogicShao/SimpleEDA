from common_import import *


class CircuitNode(qtw.QGraphicsItem):
    potential: float | None = None

    class SignalEmitter(qtc.QObject):
        positionChanged = qtc.pyqtSignal()

    def __init__(self, position: qtc.QPointF):
        super().__init__()
        self.setPos(position)
        self.radius = 3
        self.signals = self.SignalEmitter()
        self.setFlags(
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def boundingRect(self):
        return qtc.QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen()
        pen.setWidth(2)

        if self.isSelected():
            pen.setColor(qtc.Qt.GlobalColor.red)
            painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.red))
        else:
            pen.setColor(qtc.Qt.GlobalColor.yellow)
            painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.yellow))

        painter.setPen(pen)
        painter.drawEllipse(qtc.QPointF(0, 0), self.radius, self.radius)

    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            logger.info('选中节点')
            self.setSelected(True)
            mainWindow = self.scene().views()[0].window()
            if mainWindow:
                mainWindow.NodeSelect(self)
        super().mousePressEvent(event)


class BaseCircuitItem(qtw.QGraphicsItem):
    nodes: list[CircuitNode]

    @staticmethod
    def What() -> str:
        return '电路元件'

    def __init__(self):
        super().__init__()
        # 设置图元可被选中和移动
        self.setFlags(
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        logger.info('添加{}'.format(self.What()))

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key.Key_Delete:
            scene = self.scene()
            if scene:
                scene.removeItem(self)
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = qtw.QMenu()
        modifyAction = menu.addAction('修改')
        deleteAction = menu.addAction('删除')

        action = menu.exec(event.screenPos())
        if action == deleteAction:
            self.deleteItem()
        elif action == modifyAction:
            self.modifyItem()
        else:
            super().contextMenuEvent(event)

    def modifyItem(self):
        logger.info('修改{}图元'.format(self.what))

    def deleteItem(self):
        logger.info('删除{}图元'.format(self.what))
        self.scene().removeItem(self)

    def itemChange(self, change, value):
        if change == qtw.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for node in self.nodes:
                node.signals.positionChanged.emit()
        return super().itemChange(change, value)


class ItemInfo(qtw.QGraphicsItem):
    def __init__(self, text: str, position: qtc.QPointF):
        super().__init__()
        self.text = text
        self.position = position
        self.width = 40
        self.height = 20
        self.setPos(position)

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.setFont(qtg.QFont('Arial', 12))
        painter.drawText(self.boundingRect(),
                         qtc.Qt.AlignmentFlag.AlignCenter, self.text)
