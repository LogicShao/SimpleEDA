from common_import import *
import CircuitItem as CI


class MainWindow(qtw.QMainWindow):
    selectedNode: CI.CircuitNode | None = None

    def __init__(self):
        super().__init__()

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

        layout.addLayout(self.btnBox)

    def addItemBtn(self, btnLayout: qtw.QHBoxLayout, item: type[CI.BaseCircuitItem]):
        btn = qtw.QPushButton('添加{}'.format(item.What()))
        btn.clicked.connect(lambda: self.scene.addItem(item()))
        btnLayout.addWidget(btn)

    def NodeSelect(self, node: CI.CircuitNode):
        if self.selectedNode is None:
            logger.info('选择导线起点')
            self.selectedNode = node
        else:
            logger.info('选择导线终点')
            self.scene.addItem(CI.WireItem(self.selectedNode, node))
            self.scene.update()
            self.selectedNode = None
