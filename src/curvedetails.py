from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.CurveDetails import Ui_CurveDetails

class CurveDetails(QtWidgets.QMainWindow, Ui_CurveDetails):
    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.index = index

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