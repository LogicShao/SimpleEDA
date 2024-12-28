from common_import import *
from CircuitTopology import CircuitTopology
import CircuitItem as CI


class MainWindow(qtw.QMainWindow):
    _selected_node: CI.ItemNode | None = None
    _linked_item_node_pairs: set[tuple[CI.ItemNode, CI.ItemNode]] = set()
    item_nodes: set[CI.ItemNode]

    def __init__(self):
        super().__init__()

        self.item_nodes = set()

        self.setWindowTitle("电路分析仿真系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        self.scene = qtw.QGraphicsScene()  # 电路图绘制区域
        self.view = qtw.QGraphicsView(self.scene)
        self.view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.view)

        self.setCentralWidget(qtw.QWidget())
        self.centralWidget().setLayout(layout)

        self.btnBox = qtw.QHBoxLayout()
        for itemType in CI.BTN_ITEM_TYPES:
            self.addItemBtn(self.btnBox, itemType)

        solveBtn = qtw.QPushButton('求解')
        solveBtn.clicked.connect(self.solve)
        self.btnBox.addWidget(solveBtn)

        layout.addLayout(self.btnBox)

        self.setStyleSheet("""
            QMainWindow { background-color: black; }
            QGraphicsView { background-color: black; }
            QPushButton { background-color: rgb(50, 50, 50); color: white; }""")

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

    def _solve(self):
        solver = CircuitTopology(self.item_nodes)
        logger.info(solver)
        martrix = solver.get_MNA_matrix()
        logger.info('MNA矩阵：' + str(martrix))
        logger.info(solver.output())

    def solve(self):
        try:
            self._solve()
        except Exception as e:
            qtw.QMessageBox.critical(self, '求解失败', 'error: ' + str(e))
