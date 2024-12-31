from common_import import *
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

SPECIAL_FUNCTIONS = {
    'DiracDelta': lambda t: np.zeros_like(t),
    'Heaviside': np.heaviside,
    'Piecewise': lambda *args: np.piecewise(args[0], args[1::2], args[2::2]),
    'Abs': np.abs,
    'sign': np.sign,
    'Max': np.maximum,
    'Min': np.minimum,
    'sin': np.sin,
    'cos': np.cos,
    'tan': np.tan,
    'exp': np.exp,
    'log': np.log,
    'sqrt': np.sqrt
}
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


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
        if item_id in cls._used_item_id:
            cls._used_item_id.remove(item_id)


class CircuitNode:
    potential: sp.Symbol | None = None
    _item_counter = ItemCounter()
    item_id: int
    connect_items: list['BaseCircuitItem']
    isGround: bool = False

    def getName(self):
        return 'V{}'.format(self.item_id)

    def __init__(self):
        self.item_id = self._item_counter.genItemID()
        self.connect_items = []

    def __del__(self):
        self._item_counter.delItemID(self.item_id)

    def addConnectItem(self, item: 'BaseCircuitItem'):
        self.connect_items.append(item)
        if item.What() == 'GND':
            self.isGround = True
            self.potential = 0
            self._item_counter.delItemID(self.item_id)
            self.item_id = 0

    def __str__(self):
        return "{} [{}]".format(self.getName(), ','.join([item.getName() for item in self.connect_items]))

    def __lt__(self, other):
        if not isinstance(other, CircuitNode):
            raise TypeError('类型不匹配')
        return self.item_id < other.item_id


class ItemSymbol(qtw.QGraphicsItem):
    def __init__(self, parent: qtw.QGraphicsItem):
        super().__init__()
        self.setParentItem(parent)

    def getNodesPos(self) -> list[qtc.QPointF]:
        return [self.scenePos()]


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

    def set_text(self, text: str):
        self.text = text
        self.update()


class ItemNode(ItemSymbol):
    wires: set
    circuitNode: CircuitNode | None = None
    _item_node_counter = ItemCounter()
    item_id: int

    def getName(self):
        return 'N{}'.format(self.item_id)

    def __str__(self):
        return '{}的节点'.format(self.parentItem().getName())

    class SignalEmitter(qtc.QObject):
        positionChanged = qtc.pyqtSignal()
        selfDeleted = qtc.pyqtSignal()

    def __init__(self, parent: qtw.QGraphicsItem, position: qtc.QPointF):
        super().__init__(parent=parent)
        self.setPos(position)
        self.radius = 3
        self.signals = self.SignalEmitter()
        self.wires = set()
        self.setFlags(
            qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.item_id = self._item_node_counter.genItemID()
        self.id_info = ItemInfo(parent=self, text=str(
            self.item_id), position=qtc.QPointF(0, -12))

    def __del__(self):
        self._item_node_counter.delItemID(self.item_id)
        try:
            mainWinodw = self.scene().views()[0].window()
            if mainWinodw:
                mainWinodw._selected_node = None
        except:
            pass

    def addWire(self, wire):
        self.wires.add(wire)

    def removeWire(self, wire):
        self.wires.remove(wire)

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

    def getConnectItemNodes(self) -> list['ItemNode']:
        return [wire.start if wire.end == self else wire.end for wire in self.wires]


class ModifyItemDialog(qtw.QDialog):
    def __init__(self, item: 'BaseCircuitItem'):
        super().__init__()
        self.item = item
        self.setWindowTitle('修改{}'.format(item.getName()))
        self.setup_ui()

    def setup_ui(self):
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.lineEdit = qtw.QLineEdit()
        self.lineEdit.setValidator(qtg.QDoubleValidator())
        layout.addWidget(self.lineEdit)

        self.btnBox = qtw.QHBoxLayout()
        self.addBtn(self.btnBox, '确定', self.validate)
        self.addBtn(self.btnBox, '取消', self.reject)

        layout.addLayout(self.btnBox)

    def addBtn(self, layout: qtw.QHBoxLayout, text: str, func):
        btn = qtw.QPushButton(text)
        btn.clicked.connect(func)
        layout.addWidget(btn)

    def validate(self):
        value = float(self.lineEdit.text())
        if value <= 0:
            qtw.QMessageBox.warning(self, '错误', '元件值应为正数')
            return
        super().accept()
        logger.info('修改{}为{}'.format(self.item.getName(), value))


class ShowItemInfoDialog(qtw.QDialog):
    def __init__(self, item: 'BaseCircuitItem'):
        super().__init__()
        self.item = item
        self.setWindowTitle('元件信息')
        self.setup_ui()

    def setup_ui(self):
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.item_name_label = qtw.QLabel()
        self.item_name_label.setText('元件名称：{}'.format(self.item.getName()))
        layout.addWidget(self.item_name_label)

        mainWinodw = self.item.scene().views()[0].window()
        solved = mainWinodw.solved

        self.item_nodes_label = qtw.QLabel()
        self.item_nodes_label.setText('元件节点：{}'.format(','.join([node.getName() + ('({}: {}V)'.format(
            node.circuitNode.getName(), node.circuitNode.potential) if solved else '') for node in self.item.nodes])))
        layout.addWidget(self.item_nodes_label)

        if self.item._has_value:
            self.item_value_label = qtw.QLabel()
            self.item_value_label.setText('{}：{}'.format(
                self.item.What(), self.item.get_value()))
            layout.addWidget(self.item_value_label)

        self.btnBox = qtw.QHBoxLayout()
        self.addBtn(self.btnBox, '确定', self.accept)

        layout.addLayout(self.btnBox)

    def addBtn(self, layout: qtw.QHBoxLayout, text: str, func):
        btn = qtw.QPushButton(text)
        btn.clicked.connect(func)
        layout.addWidget(btn)


class BaseCircuitItem(qtw.QGraphicsItem):
    nodes: list[ItemNode]
    mainSymbol: ItemSymbol
    _item_counter = ItemCounter()
    _has_value: bool = False
    item_id: int
    current: sp.Expr | float | None = None
    voltage: sp.Expr | float | None = None
    s = sp.symbols('s', complex=True)
    t = sp.symbols('t', real=True)

    def get_voltage_expr_in_s_domin(self) -> sp.Expr | float | None:
        # 返回电压源的电压（频域）
        return self.voltage

    def get_current_expr_in_s_domin(self) -> sp.Expr | float | None:
        # 返回电流源的电流（频域）
        return self.current

    @staticmethod
    def What() -> str:
        return '电路元件'

    def getName(self):
        return self.What() + str(self.item_id)

    def __str__(self):
        return self.getName()

    def getCircuitNodes(self) -> list[CircuitNode]:
        return [node.circuitNode for node in self.nodes]

    def get_solve_state(self) -> bool:
        mainWinodw = self.scene().views()[0].window()
        return mainWinodw.solved if mainWinodw else False

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

    def showItemInfo(self):
        logger.info('显示{}的信息'.format(self.getName()))

        dialog = ShowItemInfoDialog(self)
        dialog.exec()

    def contextMenuEvent(self, event):
        menu = qtw.QMenu()
        showInfoAction = menu.addAction('显示信息')
        modifyAction = menu.addAction('修改')
        deleteAction = menu.addAction('删除')
        drawCurrentTimeAction = menu.addAction('绘制电流时域波形')
        drawVoltageTimeAction = menu.addAction('绘制电压时域波形')

        action = menu.exec(event.screenPos())
        if action == showInfoAction:
            self.showItemInfo()
        elif action == deleteAction:
            if self.get_solve_state():
                qtw.QMessageBox.warning(self.scene().views()[
                                        0].window(), '提示', '求解结束电路不可修改，请通过清除按钮清空电路')
            else:
                self.deleteItem()
        elif action == modifyAction:
            self.modifyItem()
        elif action == drawCurrentTimeAction:
            logger.info('绘制{}的电流时域波形'.format(self.getName()))
            self.drawCurrentTime()
        elif action == drawVoltageTimeAction:
            logger.info('绘制{}的电压时域波形'.format(self.getName()))
            self.drawVoltageTime()
        else:
            super().contextMenuEvent(event)

    def drawCurrentTime(self):
        if not self.get_solve_state():
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', '电路未求解')
            return

        if self.What() == 'GND':
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', 'GND无法绘制电流-时间波形')
            return

        current_expr = self.get_current_expr_in_s_domin()
        if current_expr is None:
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', '电流未求解')
            return

        current_expr = sp.inverse_laplace_transform(
            current_expr, self.s, self.t).simplify()
        current_func = sp.lambdify(self.t, current_expr, modules=[
                                   SPECIAL_FUNCTIONS, 'numpy'])
        logger.info('电流-时间波形：{}'.format(current_expr))

        t_values = np.linspace(0, 100, 1000)
        current_values = current_func(t_values)

        plt.plot(t_values, current_values,
                 label='{}:电流-时间波形'.format(self.getName()))
        plt.xlabel('时间/s')
        plt.ylabel('电流/A')
        plt.legend()
        plt.title('{}:电流-时间波形'.format(self.getName()))
        plt.grid(True)
        plt.show()

    def drawVoltageTime(self):
        if not self.get_solve_state():
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', '电路未求解')
            return

        if self.What() == 'GND':
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', 'GND无法绘制电压-时间波形')
            return

        voltage_expr = self.get_voltage_expr_in_s_domin()
        if voltage_expr is None:
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', '电压未求解')
            return

        voltage_expr = sp.inverse_laplace_transform(
            voltage_expr, self.s, self.t).simplify()
        voltage_func = sp.lambdify(self.t, voltage_expr, modules=[
                                   SPECIAL_FUNCTIONS, 'numpy'])
        logger.info('电压-时间波形：{}'.format(voltage_expr))

        t_values = np.linspace(0, 100, 1000)
        voltage_values = voltage_func(t_values)

        plt.plot(t_values, voltage_values,
                 label='{}:电压-时间波形'.format(self.getName()))
        plt.xlabel('时间/s')
        plt.ylabel('电压/V')
        plt.legend()
        plt.title('{}:电压-时间波形'.format(self.getName()))
        plt.grid(True)
        plt.show()

    def modifyItem(self):
        if not self._has_value or self.get_solve_state():
            qtw.QMessageBox.warning(self.scene().views()[
                                    0].window(), '提示', '求解结束电路不可修改，请通过清除按钮清空电路')
            return

        logger.info('修改{}'.format(self.getName()))

        dialog = ModifyItemDialog(self)
        dialog.exec()

    def deleteItem(self):
        for node in self.nodes:
            node.signals.selfDeleted.emit()
        scene = self.scene()
        scene.removeItem(self)
        scene.update()

    def itemChange(self, change, value):
        if change == qtw.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for node in self.nodes:
                node.signals.positionChanged.emit()
        return super().itemChange(change, value)

    def getAnotherNode(self, node: ItemNode) -> ItemNode | None:
        if node not in self.nodes or len(self.nodes) != 2:
            return None
        return self.nodes[1] if node == self.nodes[0] else self.nodes[0]

    def __lt__(self, other):
        if not isinstance(other, BaseCircuitItem):
            raise TypeError('类型不匹配')
        return self.item_id < other.item_id

    def set_value(self, value: float):
        pass

    def get_value(self) -> float:
        pass
