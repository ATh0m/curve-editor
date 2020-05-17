import logging

logger = logging.getLogger('curve-editor')

import math
import numpy as np

from PyQt5 import QtGui, QtCore, QtWidgets

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
        return BezierCurve.binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))

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

    def setup_toolbar(self, parent):
        super().setup_toolbar(parent)

        self.show_convex_hull_action = QtWidgets.QAction("Show convex hull", parent)
        self.show_convex_hull_action.triggered.connect(
            self.show_convex_hull_action_triggered)
        self.show_convex_hull_action.setCheckable(True)
        self.toolbar.addAction(self.show_convex_hull_action)

    def show_convex_hull_action_triggered(self, state):
        if self.show_convex_hull != state:
            self.show_convex_hull = state
            self.model.updated()
            logger.info(f'Convex hull: {state}')

    def __de_casteljau(self, k, i, t, cache):
        if (k, i) not in cache:
            if k == 0:
                cache[(k, i)] = np.array(self.nodes[i])
            else:
                cache[(k, i)] = (1 - t) * self.__de_casteljau(k-1, i, t, cache) + \
                                t * self.__de_casteljau(k-1, i+1, t, cache)
        return cache[(k, i)]

    def de_casteljau(self, t):
        return tuple(self.__de_casteljau(len(self.nodes)-1, 0, t, dict()))

    def __approximate_length(self):
        if len(self.nodes) < 2:
            return 0.0

        length = 0.
        for i in range(len(self.nodes) - 1):
            x, y = self.nodes[i]
            next_x, next_y = self.nodes[i + 1]

            length += np.sqrt((next_x - x)**2 + (next_y - y)**2)

        return length

    def calculate_points(self):
        super().calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        approximate_length = self.__approximate_length()
        logger.info(approximate_length)

        steps = int(max(approximate_length // 10, 10)) # 1000

        points = [self.nodes[0]]
        for point in BezierCurve.bezier_curve_range(steps, self.nodes):
            points.append(point)
        # points = [self.de_casteljau(i / steps) for i in range(steps + 1)]

        self.points = points
        return self.points

    def draw_nodes(self, qp: QtGui.QPainter):
        black_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        red_pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        red_brush = QtGui.QBrush(QtCore.Qt.red)

        old_point = self.nodes[0]

        qp.setPen(red_pen)
        qp.setBrush(red_brush)
        qp.drawEllipse(old_point[0] - 3, old_point[1] - 3, 6, 6)

        qp.drawText(old_point[0] + 5, old_point[1] - 3, '1')
        for i, point in enumerate(self.nodes[1:]):
            i += 2
            qp.setPen(black_pen)
            qp.drawLine(old_point[0], old_point[1], point[0], point[1])

            qp.setPen(red_pen)
            qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

            qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)
            old_point = point
