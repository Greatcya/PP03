import sys
from PyQt6.QtWidgets import QApplication
from ui import ImageForgeApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageForgeApp()
    window.show()
    sys.exit(app.exec())