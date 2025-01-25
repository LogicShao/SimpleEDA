from .BaseCircuitItem import *
from common_import import *
import sympy as sp


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
        pen = qtg.QPen(qtc.Qt.GlobalColor.blue, 2)
        painter.setPen(pen)

        start_pos = self.start.scenePos()
        end_pos = self.end.scenePos()
        x1, y1 = start_pos.x(), start_pos.y()
        x2, y2 = end_pos.x(), end_pos.y()
        if abs(x1 - x2) < abs(y1 - y2):
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
        pen = qtg.QPen(qtc.Qt.GlobalColor.blue, 2)
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

    def get_value(self):
        return self.resistance

    def get_voltage_expr_in_s_domain(self) -> sp.Expr | None:
        node1, node2 = self.nodes
        expr = node1.circuitNode.potential - node2.circuitNode.potential
        return expr

    def get_current_expr_in_s_domain(self) -> sp.Expr | None:
        node1, node2 = self.nodes
        expr = (node1.circuitNode.potential -
                node2.circuitNode.potential) / self.resistance
        return expr


class CapacitorSymbol(ItemSymbol):
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__(parent=parent)
        self.width = 60
        self.height = 20

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.blue, 2)
        painter.setPen(pen)

        side_margin_factor = 0.4
        side_margin = self.width * side_margin_factor
        mid_width = self.width - 2 * side_margin
        # 绘制两条竖线
        painter.drawLine(qtc.QPointF(mid_width / 2, -self.height / 2),
                         qtc.QPointF(mid_width / 2, self.height / 2))
        painter.drawLine(qtc.QPointF(-mid_width / 2, -self.height / 2),
                         qtc.QPointF(-mid_width / 2, self.height / 2))
        # 绘制两条横线
        painter.drawLine(qtc.QPointF(-mid_width / 2, 0),
                         qtc.QPointF(-self.width / 2, 0))
        painter.drawLine(qtc.QPointF(mid_width / 2, 0),
                         qtc.QPointF(self.width / 2, 0))

    def getNodesPos(self) -> list[qtc.QPointF]:
        # 获取电容两端的节点
        return [qtc.QPointF(-self.width / 2, 0),
                qtc.QPointF(self.width / 2, 0)]


class CapacitorItem(BaseCircuitItem):
    _item_counter = ItemCounter()
    _has_value = True

    @staticmethod
    def What() -> str:
        return '电容'

    def __init__(self, capacitance: float = 10):
        super().__init__()

        self.mainSymbol = CapacitorSymbol(parent=self)
        self.nodes = [ItemNode(parent=self, position=pos)
                      for pos in self.mainSymbol.getNodesPos()]

        self.width = self.mainSymbol.width + 2 * self.nodes[0].radius
        self.height = self.mainSymbol.height

        self.capacitance = capacitance
        self.capacitanceInfo = ItemInfo(
            parent=self,
            text='{:.0f}F'.format(self.capacitance),
            position=qtc.QPointF(0, -self.height / 2 - 12)
        )

        self.nameText = ItemInfo(
            parent=self,
            text=self.getName(),
            position=qtc.QPointF(0, self.height / 2 + 14)
        )

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def set_value(self, value):
        self.capacitance = value
        self.capacitanceInfo.set_text('{:.0f}F'.format(self.capacitance))
        self.scene().update()

    def get_value(self):
        return self.capacitance

    def get_current_expr_in_s_domain(self) -> sp.Expr | None:
        node1, node2 = self.nodes
        Y = self.capacitance * self.s
        expr = Y * (node1.circuitNode.potential - node2.circuitNode.potential)
        return expr

    def get_voltage_expr_in_s_domain(self) -> sp.Expr | None:
        node1, node2 = self.nodes
        expr = node1.circuitNode.potential - node2.circuitNode.potential
        return expr


class InductorSymbol(ItemSymbol):
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__(parent=parent)
        self.width = 60
        self.height = 20

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = qtg.QPen(qtc.Qt.GlobalColor.blue, 2)
        painter.setPen(pen)

        side_margin_factor = 0.25
        side_margin = self.width * side_margin_factor
        mid_width = self.width - 2 * side_margin
        # 绘制两条横线
        painter.drawLine(qtc.QPointF(-mid_width / 2, 0),
                         qtc.QPointF(-self.width / 2, 0))
        painter.drawLine(qtc.QPointF(mid_width / 2, 0),
                         qtc.QPointF(self.width / 2, 0))
        # 绘制弧线
        arc_num = 9
        arc_dx = mid_width / arc_num
        arc_dy = self.height / 2
        x1, x2 = -mid_width / 2, -mid_width / 2 + arc_dx
        for i in range(arc_num):
            if i % 2 == 0:
                # 绘制向上的弧线
                painter.drawArc(qtc.QRectF(
                    x1, -arc_dy, arc_dx, arc_dy * 2), 0, 180 * 16)
            else:
                # 绘制向下的弧线
                painter.drawArc(qtc.QRectF(
                    x1, -arc_dy, arc_dx, arc_dy * 2), 0, -180 * 16)
            x1, x2 = x2, x2 + arc_dx

    def getNodesPos(self) -> list[qtc.QPointF]:
        # 获取电感两端的节点
        return [qtc.QPointF(-self.width / 2, 0),
                qtc.QPointF(self.width / 2, 0)]


class InductorItem(BaseCircuitItem):
    _item_counter = ItemCounter()
    _has_value = True

    @ staticmethod
    def What() -> str:
        return '电感'

    def __init__(self, inductance: float = 10):
        super().__init__()

        self.mainSymbol = InductorSymbol(parent=self)
        self.nodes = [ItemNode(parent=self, position=pos)
                      for pos in self.mainSymbol.getNodesPos()]

        self.width = self.mainSymbol.width + 2 * self.nodes[0].radius
        self.height = self.mainSymbol.height

        self.inductance = inductance
        self.inductanceInfo = ItemInfo(
            parent=self,
            text='{:.0f}H'.format(self.inductance),
            position=qtc.QPointF(0, -self.height / 2 - 12)
        )

        self.nameText = ItemInfo(
            parent=self,
            text=self.getName(),
            position=qtc.QPointF(0, self.height / 2 + 14)
        )

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return qtc.QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def set_value(self, value):
        self.inductance = value
        self.inductanceInfo.set_text('{:.0f}H'.format(self.inductance))
        self.scene().update()

    def get_value(self):
        return self.inductance

    def get_current_expr_in_s_domain(self) -> sp.Expr | None:
        Y = 1 / (self.inductance * self.s)
        node1, node2 = self.nodes
        expr = Y * (node1.circuitNode.potential - node2.circuitNode.potential)
        return expr

    def get_voltage_expr_in_s_domain(self) -> sp.Expr | None:
        node1, node2 = self.nodes
        expr = node1.circuitNode.potential - node2.circuitNode.potential
        return expr
