from common_import import *
import CircuitItem as CI


class MainWindow(qtw.QMainWindow):
    _selected_node: CI.ItemNode | None = None
    _linked_item_node_pairs: set[tuple[CI.ItemNode, CI.ItemNode]]
    _items = set[CI.BaseCircuitItem]
    item_nodes: set[CI.ItemNode]
    solved = False

    def __init__(self):
        super().__init__()

        self.setWindowTitle("电路分析仿真系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

        self.item_nodes = set()
        self._items = set()
        self._linked_item_node_pairs = set()

    def setup_ui(self):
        self.scene = qtw.QGraphicsScene()  # 电路图绘制区域
        self.view = qtw.QGraphicsView(self.scene)
        self.view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)

        self._layout = qtw.QVBoxLayout()
        self._layout.addWidget(self.view)

        self.setCentralWidget(qtw.QWidget())
        self.centralWidget().setLayout(self._layout)

        self.btnBox = self.getBtnLayout()
        self._layout.addLayout(self.btnBox)

        self.setStyleSheet("""
            QMainWindow { background-color: black; }
            QGraphicsView { background-color: black; }
            QPushButton { background-color: rgb(50, 50, 50); color: white; }""")

    def getBtnLayout(self) -> qtw.QHBoxLayout:
        btnLayout = qtw.QHBoxLayout()
        if self.solved:
            clearBtn = qtw.QPushButton('清空')
            clearBtn.clicked.connect(self.clearItems)
            btnLayout.addWidget(clearBtn)
            return btnLayout
        for itemType in CI.BTN_ITEM_TYPES:
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
            self._items.add(item_instance)
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
            solver = CI.CircuitTopology(self.item_nodes, self._items)
            martrix = solver.get_MNA_matrix()
            self.onAfterSolve(True)
            
            logger.info('求解')
            logger.info(solver)
            logger.info('MNA矩阵：' + str(martrix))
            logger.info(solver.output())
        except Exception as e:
            qtw.QMessageBox.critical(self, '求解失败', 'error: ' + str(e))

    def clearItems(self):
        self.scene.clear()
        self.scene.update()
        self.item_nodes.clear()
        self._linked_item_node_pairs.clear()
        self._selected_node = None
        self._items.clear()
        self.onAfterSolve(False)
        logger.info('清空')
