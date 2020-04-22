from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.CurveDetails import Ui_CurveDetails

class CurveDetails(QtWidgets.QMainWindow, Ui_CurveDetails):
    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.index = index

        self.translateApply.clicked.connect(self.translate_curve)
        self.scaleApply.clicked.connect(self.scale_curve)
        self.rotateApply.clicked.connect(self.rotate_curve)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super(CurveDetails, self).showEvent(event)
        self.fill()

    def setModel(self, model):
        self.model = model
        self.model.layoutChanged.connect(self.fill)

    def fill(self):
        curve = self.model.curves[self.index]

        self.name_label.setText(curve.name)
        self.nodes_label.setText(str(len(curve.nodes)))

    def translate_curve(self):
        dx = float(self.translate_dx.text())
        dy = float(self.translate_dy.text())

        self.model.curves[self.index].translate(dx, dy)
        self.model.updated()

    def scale_curve(self):
        scalar = float(self.scaleInput.text())

        self.model.curves[self.index].scale(scalar)
        self.model.updated()

    def rotate_curve(self):
        theta = float(self.rotateInput.text())

        self.model.curves[self.index].rotate(theta)
        self.model.updated()