import math
import numpy as np
from scipy.special import comb

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog

from . import BezierCurve

from src.states import SplitCurveState, DefaultState, SetWeightNodeState

import numpy as np
import logging

logger = logging.getLogger('curve-editor')


class RationalBezierCurve(BezierCurve):
    def __init__(self, name, nodes=None, weights=None):
        super().__init__(name, nodes)

        self.helper_weights = {}

        self.weights = weights or []
        self.type = "Rational Bezier Curve"

    def add_node(self, x, y, calculate=True):
        self.nodes.append((x, y))
        self.weights.append(1.0)
        if calculate:
            self.calculate_points(force=False)

    def remove_node(self, index, calculate=True):
        self.nodes.pop(index)
        self.weights.pop(index)
        if calculate:
            self.calculate_points()

    def change_nodes_order(self, index1, index2, mode, calculate=True):
        node1, weight1 = self.nodes[index1], self.weights[index1]
        node2, weight2 = self.nodes[index2], self.weights[index2]

        if mode == 'swap':
            self.nodes[index1] = node2
            self.nodes[index2] = node1

            self.weights[index1] = weight2
            self.weights[index2] = weight1

        elif mode == 'before':
            self.nodes.insert(index2, node1)
            self.weights.insert(index2, weight1)

            if index2 <= index1:
                self.nodes.pop(index1 + 1)
                self.weights.pop(index1 + 1)
            else:
                self.nodes.pop(index1)
                self.weights.pop(index1)

        elif mode == 'after':
            self.nodes.insert(index2 + 1, node1)
            self.weights.insert(index2 + 1, weight1)

            if index2 + 1 <= index1:
                self.nodes.pop(index1 + 1)
                self.weights.pop(index1 + 1)
            else:
                self.nodes.pop(index1)
                self.weights.pop(index1)

        if calculate:
            self.calculate_points()

    def set_node_weight(self, index, weight, calculate=True):
        self.weights[index] = weight

        if calculate:
            self.calculate_points()

    @staticmethod
    def rational_bezier(t, nodes, weights):
        """Calculate coordinate of a point in the bezier curve"""
        n = len(nodes) - 1

        numerator = sum(RationalBezierCurve.bernstein(t, i, n) * weights[i] * node
                        for i, node in enumerate(nodes))
        denominator = sum(RationalBezierCurve.bernstein(t, i, n) * weights[i]
                          for i, node in enumerate(nodes))

        return numerator / denominator

    @staticmethod
    def rational_bezier_curve_range(n, nodes, weights):
        """Range of points in a curve bezier"""
        for i in range(n):
            t = i / float(n - 1)
            yield RationalBezierCurve.rational_bezier(t, nodes, weights)

    def setup_toolbar(self, parent):
        super().setup_toolbar(parent)

        self.set_weight_action = QtWidgets.QAction("Set weight", parent)
        self.set_weight_action.triggered.connect(self.set_weight_action_triggered)
        self.set_weight_action.setCheckable(True)
        self.extra_toolbar.addAction(self.set_weight_action)

        self.raise_degree_action.setDisabled(True)

    def set_weight_action_triggered(self, state):
        if state:
            self.model.state = SetWeightNodeState(self)
        else:
            self.model.state = DefaultState()

    def split_curve(self, index):
        n = len(self.nodes) - 1

        first_nodes, first_weights = [], []
        second_nodes, second_weights = [], []
        for k in range(n+1):
            w1, W1 = self._rational_de_casteljau(k, 0, index)
            w2, W2 = self._rational_de_casteljau(k, n - k, index)
            
            first_nodes.append(tuple(W1))
            first_weights.append(w1)
            
            second_nodes.append(tuple(W2))
            second_weights.append(w2)

        first_curve = self.clone()
        second_curve = self.clone()

        first_curve.nodes = first_nodes
        first_curve.weights = first_weights
        first_curve.calculate_points(force=True)

        second_curve.nodes = second_nodes
        second_curve.weights = second_weights
        second_curve.calculate_points(force=True)

        return first_curve, second_curve

    def draw_nodes(self, qp: QtGui.QPainter):
        black_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        red_pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        red_brush = QtGui.QBrush(QtCore.Qt.red)

        weights = self.weights
        old_point = self.nodes[0]

        qp.setPen(red_pen)
        qp.setBrush(red_brush)
        qp.drawEllipse(old_point[0] - 3, old_point[1] - 3, 6, 6)

        qp.drawText(old_point[0] + 5, old_point[1] - 3, f'1 ({weights[0]: .2f})')
        for i, point in enumerate(self.nodes[1:], 1):
            qp.setPen(black_pen)
            qp.drawLine(old_point[0], old_point[1], point[0], point[1])

            qp.setPen(red_pen)
            qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

            qp.drawText(point[0] + 5, point[1] - 3, f'{i+1} ({weights[i]: .2f})')
            old_point = point

    def _rational_de_casteljau(self, i, k, t):
        if (i, k, t) not in self.helper_nodes:
            if i == 0:
                self.helper_weights[(i, k, t)] = self.weights[k]
                self.helper_nodes[(i, k, t)] = np.array(self.nodes[k])
            else:
                w1, W1 = self._rational_de_casteljau(i-1, k, t)
                w2, W2 = self._rational_de_casteljau(i-1, k+1, t)

                u = t / self.resolution
                w = (1 - u) * w1 + u * w2
                W = (1 - u) * w1 / w * W1 + u * w2 / w * W2

                self.helper_weights[(i, k, t)] = w
                self.helper_nodes[(i, k, t)] = W

        return self.helper_weights[(i, k, t)], self.helper_nodes[(i, k, t)]

    def rational_de_casteljau(self, t):
        w, W = self._rational_de_casteljau(len(self.nodes) - 1, 0, t)
        return w, tuple(W)

    def calculate_points(self, force=True, fast=False):
        super(BezierCurve, self).calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        nodes, weights = np.array(self.nodes), np.array(self.weights)

        if fast:
            steps = max(20, self.resolution // 10)

            points = [nodes[0]]
            for point in RationalBezierCurve.rational_bezier_curve_range(steps, nodes, weights):
                points.append(point)

            self.points = points
            return self.points

        if force:
            self.helper_nodes = {}
            self.helper_weights = {}

        steps = self.resolution

        # Rational De Casteljau Algorithm
        points = [self.rational_de_casteljau(i)[1] for i in range(steps + 1)]

        self.points = points
        return self.points