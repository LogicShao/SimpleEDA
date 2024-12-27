from common_import import *
import sympy as sp


class ItemCounter:
    def __init__(self):
        self._used_item_id = set()

    def genItemID(cls) -> int:
        item_id = 1
        while item_id in cls._used_item_id:
            item_id += 1
        cls._used_item_id.add(item_id)
        return item_id

    def delItemID(cls, item_id: int):
        cls._used_item_id.remove(item_id)


class CircuitNode:
    potential: sp.Symbol  # 电位
    _item_counter = ItemCounter()
    item_id: int

    def __init__(self):
        self.item_id = self._item_counter.genItemID()
        self.potential = sp.Symbol('V{}'.format(self.item_id))

    def __del__(self):
        self._item_counter.delItemID(self.item_id)


class ItemSymbol(qtw.QGraphicsItem):
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__()
        self.setParentItem(parent)

    def getNodesPos(self) -> list[qtc.QPointF]:
        return [self.scenePos()]


class ItemNode(ItemSymbol):
    class SignalEmitter(qtc.QObject):
        positionChanged = qtc.pyqtSignal()
        selfDeleted = qtc.pyqtSignal()

    def __init__(self, parent: qtw.QGraphicsItem, position: qtc.QPointF):
        super().__init__(parent=parent)
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
            pen.setColor(qtc.Qt.GlobalColor.blue)
            painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.blue))
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

    def getParentItem(self) -> 'BaseCircuitItem':
        return self.parentItem()


class ItemInfo(ItemSymbol):
    def __init__(self, parent: qtw.QGraphicsItem, text: str, position: qtc.QPointF):
        super().__init__(parent=parent)
        self.text = text
        self.width = 80
        self.height = 20
        self.setPos(position)

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.setFont(qtg.QFont('Arial', 12))
        painter.drawText(self.boundingRect(),
                         qtc.Qt.AlignmentFlag.AlignCenter, self.text)


class BaseCircuitItem(qtw.QGraphicsItem):
    nodes: list[ItemNode]
    mainSymbol: ItemSymbol
    _item_counter = ItemCounter()
    item_id: int

    @staticmethod
    def What() -> str:
        return '电路元件'

    def getName(self):
        return self.What() + str(self.item_id)

    def __init__(self):
        super().__init__()

        self.item_id = self._item_counter.genItemID()

        self.setFlags(
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        logger.info('添加{}'.format(self.getName()))

    def __del__(self):
        self._item_counter.delItemID(self.item_id)

        logger.info('删除{}'.format(self.getName()))

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
        logger.info('修改{}'.format(self.getName()))

    def deleteItem(self):
        logger.info('删除{}'.format(self.getName()))
        for node in self.nodes:
            node.signals.selfDeleted.emit()
        self.scene().removeItem(self)

    def itemChange(self, change, value):
        if change == qtw.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for node in self.nodes:
                node.signals.positionChanged.emit()
        return super().itemChange(change, value)
