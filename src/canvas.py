import math
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from .model import CurvesModel
from .states import SelectCurveState, DefaultState, AddPointState


class Canvas(QtWidgets.QGraphicsPixmapItem):
    """ Canvas for drawing"""
    def __init__(self):
        super().__init__(QtGui.QPixmap(930, 690))
        self.model: CurvesModel = None

    def setModel(self, model):
        self.model: CurvesModel = model
        self.model.layoutChanged.connect(self.draw)

    def mousePressEvent(self, ev) -> None:
        x, y = ev.pos().x(), ev.pos().y()

        if isinstance(self.model.state, SelectCurveState):
            print('selecting')

            index, dist = self.model.distance_to_nearest_curve(x, y)
            print(index, dist)
            if dist is not None and dist < 10:
                self.model.select(index)
                print(f'Selected curve: {index}')

            self.model.state = self.model.state.nextState()

        elif isinstance(self.model.state, AddPointState):
            curve = self.model.state.curve
            curve.nodes.append((x, y))
            curve.calculate_points()

            self.model.layoutChanged.emit()

    def draw(self):
        pixmap = QtGui.QPixmap(930, 690)
        pixmap.fill(Qt.white)

        qp = QtGui.QPainter(pixmap)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)

        for curve in self.model.curves:
            curve.draw(qp)

        qp.end()
        self.setPixmap(pixmap)
        print('Updated')

    def screenshot(self, filename):
        self.pixmap().save(filename)

        print('OK')
