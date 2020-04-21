import math
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class Canvas(QtWidgets.QGraphicsPixmapItem):
    """ Canvas for drawing"""
    def __init__(self):
        super().__init__(QtGui.QPixmap(930, 690))

        self.model = None

    def setModel(self, model):
        self.model = model
        self.model.layoutChanged.connect(self.draw)

    def mousePressEvent(self, ev) -> None:
        x, y = ev.pos().x(), ev.pos().y()

        curve = self.model.curves[0]
        curve.nodes.append((x, y))
        curve.calculate_points()

        self.model.layoutChanged.emit()

    def draw(self):
        pixmap = QtGui.QPixmap(930, 690)
        pixmap.fill(Qt.white)

        qp = QtGui.QPainter(pixmap)

        for curve in self.model.curves:
            curve.draw(qp)

        qp.end()
        self.setPixmap(pixmap)
        print('Updated')
