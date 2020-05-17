from PyQt5 import QtGui, QtCore

from .curves import Curve


class PolygonalCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Polygonal Curve"

    def calculate_points(self):
        self.points = self.nodes
        return self.points
