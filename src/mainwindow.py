from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.MainWindow import Ui_MainWindow
from .ui.NewCurve import Ui_NewCurve

from .curvedetails import CurveDetails

from .canvas import Canvas
from .curves import CurvesModel, BezierCurve

import pickle

class NewCurveDialog(QtWidgets.QDialog, Ui_NewCurve):
    def __init__(self, *args, obj=None, **kwargs):
        super(NewCurveDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.actionSave.triggered.connect(self.save)

        self.model = CurvesModel()

        self.canvas = Canvas()
        self.canvas.setModel(self.model)

        self.listView.setModel(self.model)
        self.listView.doubleClicked['QModelIndex'].connect(self.curve_details)
        self.listView.clicked['QModelIndex'].connect(self.curve_selected)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(self.canvas)
        self.graphicsView.setScene(scene)

        self.addCurve.clicked.connect(self.add_new_curve)
        self.removeCurve.clicked.connect(self.remove_curve)

        self.model.updated()

    def curve_details(self, index):
        details = CurveDetails(index.row(), parent=self)
        details.setModel(self.model)
        details.show()

    def curve_selected(self, index):
        index = index.row()
        print(index)

        self.model.select(index)

    def add_new_curve(self):
        dialog = NewCurveDialog(parent=self)
        if dialog.exec_():
            name = dialog.name_line.text()
            curve = BezierCurve(name)
            self.model.add(curve)
            self.model.layoutChanged.emit()

    def remove_curve(self):
        self.model.remove_selected()

    def save(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save", "", "Pickle (*.pickle)", options=options)

        if filename:
            with open(f'{filename}.pickle', 'wb') as handle:
                pickle.dump(self.model, handle, protocol=pickle.HIGHEST_PROTOCOL)