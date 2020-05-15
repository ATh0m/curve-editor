from PyQt5.QtCore import QAbstractListModel, Qt
from PyQt5 import QtGui, QtCore

import math

from .curves import Curve


class BezierCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Bezier Curve"

    @staticmethod
    def binomial(i, n):
        """Binomial coefficient"""
        return math.factorial(n) / float(
            math.factorial(i) * math.factorial(n - i))

    @staticmethod
    def bernstein(t, i, n):
        """Bernstein polynom"""
        return BezierCurve.binomial(i, n) * (t**i) * ((1 - t)**(n - i))

    @staticmethod
    def bezier(t, nodes):
        """Calculate coordinate of a point in the bezier curve"""
        n = len(nodes) - 1
        x = y = 0
        for i, pos in enumerate(nodes):
            bern = BezierCurve.bernstein(t, i, n)
            x += pos[0] * bern
            y += pos[1] * bern
        return x, y

    @staticmethod
    def bezier_curve_range(n, nodes):
        """Range of points in a curve bezier"""
        for i in range(n):
            t = i / float(n - 1)
            yield BezierCurve.bezier(t, nodes)

    def calculate_points(self):
        if not self.nodes:
            self.points = []
            return self.points

        steps = 1000

        points = [self.nodes[0]]
        for point in BezierCurve.bezier_curve_range(steps, self.nodes):
            points.append(point)

        self.points = points
        return self.points

    def draw(self, qp: QtGui.QPainter):
        if self.hidden or not self.nodes:
            return

        blackPen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        redPen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        greenPen = QtGui.QPen(QtCore.Qt.green, 1, QtCore.Qt.DashLine)
        redBrush = QtGui.QBrush(QtCore.Qt.red)

        oldPoint = self.nodes[0]

        if self.show_control_points:
            qp.setPen(redPen)
            qp.setBrush(redBrush)
            qp.drawEllipse(oldPoint[0] - 3, oldPoint[1] - 3, 6, 6)

            qp.drawText(oldPoint[0] + 5, oldPoint[1] - 3, '1')
            for i, point in enumerate(self.nodes[1:]):
                i += 2
                qp.setPen(blackPen)
                qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])

                qp.setPen(redPen)
                qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

                qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)
                oldPoint = point

        qp.setPen(bluePen)
        for point in self.points:
            qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])
            oldPoint = point