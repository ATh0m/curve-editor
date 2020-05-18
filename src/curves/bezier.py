import logging

logger = logging.getLogger('curve-editor')

import math
import numpy as np
from scipy.special import comb

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog

from .curves import Curve

from src.states import SplitCurveState, DefaultState

class BezierCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.helper_nodes = {}

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

        self.extra_toolbar = QtWidgets.QToolBar()

        self.show_convex_hull_action = QtWidgets.QAction("Show convex hull", parent)
        self.show_convex_hull_action.triggered.connect(
            self.show_convex_hull_action_triggered)
        self.show_convex_hull_action.setCheckable(True)
        self.extra_toolbar.addAction(self.show_convex_hull_action)

        self.split_curve_action = QtWidgets.QAction("Split curve", parent)
        self.split_curve_action.triggered.connect(self.split_curve_action_triggered)
        self.split_curve_action.setCheckable(True)
        self.extra_toolbar.addAction(self.split_curve_action)

        self.raise_degree_action = QtWidgets.QAction("Raise degree", parent)
        self.raise_degree_action.triggered.connect(self.raise_degree_action_triggered)
        self.extra_toolbar.addAction(self.raise_degree_action)

    def show_convex_hull_action_triggered(self, state):
        if self.show_convex_hull != state:
            self.show_convex_hull = state
            self.calculate_points(force=False)
            self.model.updated()
            logger.info(f'Convex hull: {state}')

    def split_curve_action_triggered(self, state):
        if state:
            self.model.state = SplitCurveState(self)
        else:
            self.model.state = DefaultState()

    def raise_degree(self, m):
        nodes = [np.array(node) for node in self.nodes]
        n = len(nodes) - 1

        new_nodes = []

        for i in range(n + m + 1):
            node = sum(nodes[k] * comb(n, k) * comb(m, i-k) * comb(n+m, i)**(-1)
                       for k in range(max(0, i-m), min(i, n)+1))
            new_nodes.append(tuple(node))

        self.nodes = new_nodes
        self.calculate_points()

    def raise_degree_action_triggered(self, state):
        degree, ok = QInputDialog().getInt(self.model.parent,
                                               "Raise degree",
                                               "Raise by:",
                                               value=0,
                                               min=0,
                                               max=100,
                                               step=1)
        if ok and degree > 0:
            logger.info(f"Degree raising: +{degree}")
            self.raise_degree(degree)
            self.model.updated()

    def __approximate_length(self):
        if len(self.nodes) < 2:
            return 0.0

        length = 0.
        for i in range(len(self.nodes) - 1):
            x, y = self.nodes[i]
            next_x, next_y = self.nodes[i + 1]

            length += np.sqrt((next_x - x)**2 + (next_y - y)**2)

        return length

    def _de_casteljau(self, k, i, t):
        if (k, i, t) not in self.helper_nodes:
            if k == 0:
                self.helper_nodes[(k, i, t)] = np.array(self.nodes[i])
            else:
                u = t / self.resolution
                self.helper_nodes[(k, i, t)] = (1 - u) * self._de_casteljau(k-1, i, t) + \
                                               u * self._de_casteljau(k-1, i+1, t)
        return self.helper_nodes[(k, i, t)]

    def de_casteljau(self, t):
        return tuple(self._de_casteljau(len(self.nodes)-1, 0, t))

    def calculate_points(self, force=False, fast=False):
        super().calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        if fast:
            steps = max(20, self.resolution // 10)

            points = [self.nodes[0]]
            for point in BezierCurve.bezier_curve_range(steps, self.nodes):
                points.append(point)

            self.points = points
            return self.points

        if force:
            self.helper_nodes = {}

        steps = self.resolution

        # Basic Algorithm
        # points = [self.nodes[0]]
        # for point in BezierCurve.bezier_curve_range(steps, self.nodes):
        #     points.append(point)

        # De Casteljau Algorithm
        points = [self.de_casteljau(i) for i in range(steps + 1)]

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
