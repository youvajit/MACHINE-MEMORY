"""Miss Minutes desktop assistant entry point."""
import sys
from PySide6.QtWidgets import QApplication
from miss_minutes.ui import MissMinutesWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Miss Minutes")
    app.setOrganizationName("MissMinutes")
    window = MissMinutesWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
