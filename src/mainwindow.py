from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.MainWindow import Ui_MainWindow
from .ui.NewCurve import Ui_NewCurve

from .curvedetails import CurveDetails

from .canvas import Canvas
from .curves import CurvesModel, BezierCurve

class NewCurveDialog(QtWidgets.QDialog, Ui_NewCurve):
    def __init__(self, *args, obj=None, **kwargs):
        super(NewCurveDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.model = CurvesModel()

        self.canvas = Canvas()
        self.canvas.setModel(self.model)

        self.listView.setModel(self.model)
        self.listView.doubleClicked['QModelIndex'].connect(self.curve_details)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(self.canvas)
        self.graphicsView.setScene(scene)

        self.pushButton.clicked.connect(self.add_new_curve)

        self.model.layoutChanged.emit()

    def curve_details(self, index):
        details = CurveDetails(index.row(), parent=self)
        details.setModel(self.model)
        details.show()

    def add_new_curve(self):
        dialog = NewCurveDialog(parent=self)
        if dialog.exec_():
            name = dialog.name_line.text()
            curve = BezierCurve(name)
            self.model.add(curve)
            self.model.layoutChanged.emit()
