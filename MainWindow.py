from common_import import *
import CircuitItem as CI

main_QSS = """
    QMainWindow { 
        background-color: white; 
    }
    QGraphicsView { 
        background-color: white; 
    }
    QPushButton { 
        background-color: #D3D3D3; 
        color: black; 
        border: none; 
        padding: 10px 20px; 
        text-align: center; 
        text-decoration: none; 
        font-size: 16px; 
        margin: 4px 2px; 
        border-radius: 8px; 
    }
    QPushButton:hover { 
        background-color: #C0C0C0; 
        color: black; 
        border: 2px solid #A9A9A9; 
    }
    QPushButton:pressed { 
        background-color: #A9A9A9; 
    }
    QScrollBar:vertical {
        border: 1px solid #A9A9A9;
        background: #D3D3D3;
        width: 16px;
        margin: 16px 0 16px 0;
        border-radius: 8px;
    }
    QScrollBar::handle:vertical {
        background: #A9A9A9;
        min-height: 20px;
        border-radius: 8px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background: #C0C0C0;
        height: 16px;
        subcontrol-origin: margin;
        border-radius: 8px;
    }
    QScrollBar::add-line:vertical {
        subcontrol-position: bottom;
    }
    QScrollBar::sub-line:vertical {
        subcontrol-position: top;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        border: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QScrollBar:horizontal {
        border: 1px solid #A9A9A9;
        background: #D3D3D3;
        height: 16px;
        margin: 0 16px 0 16px;
        border-radius: 8px;
    }
    QScrollBar::handle:horizontal {
        background: #A9A9A9;
        min-width: 20px;
        border-radius: 8px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: #C0C0C0;
        width: 16px;
        subcontrol-origin: margin;
        border-radius: 8px;
    }
    QScrollBar::add-line:horizontal {
        subcontrol-position: right;
    }
    QScrollBar::sub-line:horizontal {
        subcontrol-position: left;
    }
    QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
        border: none;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }
"""


class GridScene(qtw.QGraphicsScene):
    def __init__(self, parent=None):
        super(GridScene, self).__init__(parent)

    def drawBackground(self, painter, rect):
        super(GridScene, self).drawBackground(painter, rect)
        # 设置网格线的颜色
        grid_color = qtg.QColor(200, 200, 200, 200)
        painter.setPen(grid_color)
        # 设置网格线的间隔
        grid_size = 20
        # 获取视图的边界
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        # 绘制垂直网格线
        x = left
        while x < rect.right():
            painter.drawLine(qtc.QLineF(x, rect.top(), x, rect.bottom()))
            x += grid_size
        # 绘制水平网格线
        y = top
        while y < rect.bottom():
            painter.drawLine(qtc.QLineF(rect.left(), y, rect.right(), y))
            y += grid_size


class MainWindow(qtw.QMainWindow):
    _selected_node: CI.ItemNode | None = None
    _linked_item_node_pairs: set[tuple[CI.ItemNode, CI.ItemNode]]
    item_nodes: set[CI.ItemNode]
    solved = False

    def __init__(self):
        super().__init__()

        self.setWindowTitle("电路分析仿真系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

        self.item_nodes = set()
        self._linked_item_node_pairs = set()

    def setup_ui(self):
        self.scene = GridScene()
        self.view = qtw.QGraphicsView(self.scene)
        self.view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)

        self._layout = qtw.QVBoxLayout()
        self._layout.addWidget(self.view)

        self.setCentralWidget(qtw.QWidget())
        self.centralWidget().setLayout(self._layout)

        self.btnBox = self.getBtnLayout()
        self._layout.addLayout(self.btnBox)

        self.setStyleSheet(main_QSS)

    def getBtnLayout(self) -> qtw.QHBoxLayout:
        btnLayout = qtw.QHBoxLayout()
        if self.solved:
            clearBtn = qtw.QPushButton('清空')
            clearBtn.clicked.connect(self.clearItems)
            btnLayout.addWidget(clearBtn)
            return btnLayout
        for itemType in CI.ADD_ITEM_TYPES:
            self.addItemBtn(btnLayout, itemType)
        solveBtn = qtw.QPushButton('求解')
        solveBtn.clicked.connect(self.solve)
        btnLayout.addWidget(solveBtn)
        return btnLayout

    def onAfterSolve(self, solved: bool):
        if solved == self.solved:
            return
        self.solved = solved
        btnLayout = self.getBtnLayout()
        if self.btnBox is not None:
            while self.btnBox.count() > 0:
                item = self.btnBox.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.btnBox.deleteLater()
        self._layout.removeItem(self.btnBox)
        self._layout.addLayout(btnLayout)
        self.btnBox = btnLayout

    def addItemBtn(self, btnLayout: qtw.QHBoxLayout, item: type[CI.BaseCircuitItem]):
        def add_item():
            item_instance = item()
            self.scene.addItem(item_instance)
            self.scene.update()
        btn = qtw.QPushButton('添加{}'.format(item.What()))
        btn.clicked.connect(add_item)
        btnLayout.addWidget(btn)

    def NodeSelect(self, node: CI.ItemNode):
        if self._selected_node is None:
            logger.info('选择导线起点')
            self._selected_node = node
        else:
            logger.info('选择导线终点')
            node1, node2 = self._selected_node, node
            self._selected_node = None

            if node1 == node2:
                logger.info('起点和终点不能相同，取消连接')
                return
            if (node1, node2) in self._linked_item_node_pairs:
                logger.info('连接已存在，取消连接')
                return

            self._linked_item_node_pairs.add((node1, node2))
            self._linked_item_node_pairs.add((node2, node1))

            wire = CI.WireItem(node1, node2)
            self.scene.addItem(wire)
            self.scene.update()
            self.item_nodes.add(node1)
            self.item_nodes.add(node2)

    def solve(self):
        try:
            solver = CI.CircuitTopology(self.item_nodes)
            martrix = solver.get_MNA_matrix()
            self.onAfterSolve(True)
        except Exception as e:
            logger.error(e)
            qtw.QMessageBox.critical(self, '错误', str(e))
            return

        logger.info('求解')
        logger.info(solver)
        logger.info('MNA矩阵：' + str(martrix))
        logger.info(solver.output())

    def clearItems(self):
        self.item_nodes.clear()
        self._linked_item_node_pairs.clear()
        self._selected_node = None
        self.scene.clear()
        self.scene.update()
        self.onAfterSolve(False)
        logger.info('清空')
