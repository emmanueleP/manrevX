import os
import sys

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from PyQt5.QtWidgets import QApplication
from manrev.gui import ManRevGUI


def main():
    app = QApplication(sys.argv)
    window = ManRevGUI(app=app)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
