from .BaseCircuitItem import *
from common_import import *


class WireItem(qtw.QGraphicsItem):
    def __init__(self, start: ItemNode, end: ItemNode):
        super().__init__()
        self.start = start
        self.end = end

        start.addWire(self)
        end.addWire(self)

        self.start.signals.selfDeleted.connect(self.removeItem)
        self.end.signals.selfDeleted.connect(self.removeItem)

        self.start.signals.positionChanged.connect(self.updatePosition)
        self.end.signals.positionChanged.connect(self.updatePosition)

        logger.info('添加导线 ({}) <-> ({})'.format(
            self.start.parentItem().getName(), self.end.parentItem().getName()
        ))

    def start_item(self):
        return self.start.parentItem()

    def end_item(self):
        return self.end.parentItem()

    def removeItem(self):
        self.start.signals.positionChanged.disconnect(self.updatePosition)
        self.end.signals.positionChanged.disconnect(self.updatePosition)

        self.start.signals.selfDeleted.disconnect(self.removeItem)
        self.end.signals.selfDeleted.disconnect(self.removeItem)

        self.start.removeWire(self)
        self.end.removeWire(self)

        scene = self.scene()
        if not scene:
            return
        mainWindow = scene.views()[0].window()
        if mainWindow:
            mainWindow._linked_item_node_pairs.remove((self.start, self.end))
            mainWindow._linked_item_node_pairs.remove((self.end, self.start))
        scene.removeItem(self)
        scene.update()

    def boundingRect(self):
        return qtc.QRectF(self.start.scenePos(), self.end.scenePos())

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.red, 2)
        painter.setPen(pen)

        start_pos = self.start.scenePos()
        end_pos = self.end.scenePos()
        x1, y1 = start_pos.x(), start_pos.y()
        x2, y2 = end_pos.x(), end_pos.y()
        if abs(x1 - x2) > abs(y1 - y2):
            x3, y3 = x1, y2
        else:
            x3, y3 = x2, y1
        painter.drawLine(start_pos, qtc.QPointF(x3, y3))
        painter.drawLine(qtc.QPointF(x3, y3), end_pos)

    def updatePosition(self):
        self.prepareGeometryChange()
        self.update()
        self.scene().update()

    def contextMenuEvent(self, event):
        menu = qtw.QMenu()
        deleteAction = menu.addAction('删除')
        action = menu.exec(event.screenPos())
        if action == deleteAction:
            self.removeItem()
        else:
            super().contextMenuEvent(event)


class ResistorSymbol(ItemSymbol):
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__(parent=parent)
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


class ResistorItem(BaseCircuitItem):
    _item_counter = ItemCounter()
    _has_value = True

    @staticmethod
    def What() -> str:
        return '电阻'

    def __init__(self, resistance: float = 10):
        super().__init__()

        self.mainSymbol = ResistorSymbol(parent=self)
        self.nodes = [ItemNode(parent=self, position=pos)
                      for pos in self.mainSymbol.getNodesPos()]

        self.width = self.mainSymbol.width + 2 * self.nodes[0].radius
        self.height = self.mainSymbol.height

        self.resistance = resistance
        self.resistanceInfo = ItemInfo(
            parent=self,
            text='{:.0f}Ω'.format(self.resistance),
            position=qtc.QPointF(self.width / 2, -12)
        )

        self.nameText = ItemInfo(
            parent=self,
            text=self.getName(),
            position=qtc.QPointF(self.width / 2, self.height + 14)
        )

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return qtc.QRectF(0, 0, self.width, self.height)

    def set_value(self, value):
        self.resistance = value
        self.resistanceInfo.set_text('{:.0f}Ω'.format(self.resistance))
        self.scene().update()
