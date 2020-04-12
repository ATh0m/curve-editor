from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.MainWindow import Ui_MainWindow
from .canvas import Canvas
from .curves import CurvesModel, CurveItem, PointItem

class PointsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, points=None, **kwargs):
        super(PointsModel, self).__init__(*args, **kwargs)
        self.points = points or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure.
            x, y = self.points[index.row()]
            # Return the todo text only.
            return f"({x}, {y})"

    def rowCount(self, index):
        return len(self.points)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.model = CurvesModel()

        root = self.model.rootItem
        curve = CurveItem('Curve #1', parent=root)

        for point in  [(50, 170), (150, 370), (250, 35), (400, 320)]:
            point_item = PointItem(point, parent=curve)
            curve.childItems.append(point_item)

        root.childItems.append(curve)

        self.setup_treeview()

        self.canvas = Canvas(self.model)
        self.layout.addWidget(self.canvas)

    def setup_treeview(self):
        self.treeView.setModel(self.model)

        self.treeView.setAlternatingRowColors(True)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setModel(self.model)
        self.treeView.setWindowTitle("Simple Tree Model")

        header = self.treeView.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
