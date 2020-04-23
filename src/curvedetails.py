from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

from .ui.CurveDetails import Ui_CurveDetails

class CurveDetails(QtWidgets.QMainWindow, Ui_CurveDetails):
    def __init__(self, index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.index = index
        self.curve = None

        self.translateApply.clicked.connect(self.translate_curve)
        self.scaleApply.clicked.connect(self.scale_curve)
        self.rotateApply.clicked.connect(self.rotate_curve)

        self.nodesList.itemChanged.connect(self.node_changed)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super(CurveDetails, self).showEvent(event)
        self.fill()

    def setModel(self, model):
        self.model = model
        self.model.layoutChanged.connect(self.fill)

        self.curve = self.model.curves[self.index]

    def fill(self):
        curve = self.model.curves[self.index]

        self.name_label.setText(curve.name)
        self.nodes_label.setText(str(len(curve.nodes)))

        self.nodesList.clear()
        for i, (x, y) in enumerate(curve.nodes):
            item = QtWidgets.QListWidgetItem(f'({x}, {y})')
            item.index = i
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            self.nodesList.addItem(item)

    def node_changed(self, item):
        index = item.index
        val = item.text()

        x, y = val.strip('()').split(',')
        x, y = float(x), float(y)

        self.curve.nodes[index] = (x, y)
        self.model.updated()

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