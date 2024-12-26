from common_import import *
import CircuitItem as CI
import typing as tp


class MainWindow(qtw.QMainWindow):
    selectedNode: tp.Optional[CI.CircuitNode] = None

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

        self.addResistorBtn = qtw.QPushButton("添加电阻")
        self.addVoltageSourceBtn = qtw.QPushButton("添加电压源")
        self.addCurrentSourceBtn = qtw.QPushButton("添加电流源")

        layout.addWidget(self.addResistorBtn)
        layout.addWidget(self.addVoltageSourceBtn)
        layout.addWidget(self.addCurrentSourceBtn)

        self.addResistorBtn.clicked.connect(self.addResistor)
        self.addVoltageSourceBtn.clicked.connect(self.addVoltageSource)
        self.addCurrentSourceBtn.clicked.connect(self.addCurrentSource)

    def addResistor(self):
        item = CI.ResistorItem()
        self.scene.addItem(item)

    def addVoltageSource(self):
        item = CI.VoltageSourceItem()
        self.scene.addItem(item)

    def addCurrentSource(self):
        item = CI.CurrentSourceItem()
        self.scene.addItem(item)

    def NodeSelect(self, node: CI.CircuitNode):
        if self.selectedNode is None:
            logger.info('选择导线起点')
            self.selectedNode = node
        else:
            logger.info('选择导线终点')
            self.scene.addItem(CI.WireItem(self.selectedNode, node))
            self.selectedNode = None
