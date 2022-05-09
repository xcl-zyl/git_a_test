# This Python file uses the following encoding: utf-8

import sys
from PyQt5.QtWidgets import QApplication
import widget
import threading

class Process:
    def __init__(self) -> None:
        self.widget = widget.Login(0)
        self.widget.show()
        self.recv()
        
    def recv(self):
        self.tr = threading.Thread(target=self.widget.recv, args=(), daemon=True)
        self.tr.start()


            
if __name__ == "__main__":
    app = QApplication([])
    run = Process()
    sys.exit(app.exec_())
