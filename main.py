from MainWindow import MainWindow
from log_config import logger

import PyQt6.QtWidgets as qtw
import sys
import atexit


def main():
    logger.info("电路分析仿真系统启动")
    atexit.register(logger.info, "电路分析仿真系统关闭")

    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
