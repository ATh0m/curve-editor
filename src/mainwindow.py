from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.MainWindow import Ui_MainWindow
from .canvas import Canvas
from .curves import CurvesModel

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.model = CurvesModel()

        self.canvas = Canvas()
        self.canvas.setModel(self.model)

        self.listView.setModel(self.model)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(self.canvas)
        self.graphicsView.setScene(scene)

        self.model.layoutChanged.emit()
