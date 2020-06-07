import logging
logger = logging.getLogger('curve-editor')
logger.setLevel(logging.DEBUG)

# Logger section
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

fh = logging.FileHandler('curve-editor.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s()] %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)


import sys
from PyQt5 import QtWidgets

from src.mainwindow import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
