# main.py
"""
Fleet-Management desktop entry-point.

Usage
-----
pip install PyQt5               # (once, if not already in env)
python -m database.init_db      # first time only – creates fleet.db
python main.py                  # launch GUI
"""
import sys

from PyQt5.QtWidgets import QApplication

from database.init_db import init_db
from ui.main_window import MainWindow


def main() -> None:
    # Ensure tables exist (harmless if they already do)
    init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Qt event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
