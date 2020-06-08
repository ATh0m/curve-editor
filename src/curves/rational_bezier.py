import logging

import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from scipy.special import comb

from src.states import DefaultState, SetWeightNodeState
from . import BezierCurve

logger = logging.getLogger('curve-editor')


class RationalBezierCurve(BezierCurve):
    type = "Rational Bezier Curve"

    def __init__(self, name, nodes=None, weights=None):
        super().__init__(name, nodes)

        self.helper_weights = {}

        self.weights = weights or []

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

    def setup_toolbar(self, parent):
        super().setup_toolbar(parent)

        self.set_weight_action = QtWidgets.QAction("Set weight", parent)
        self.set_weight_action.triggered.connect(self.set_weight_action_triggered)
        self.set_weight_action.setCheckable(True)
        self.extra_toolbar.addAction(self.set_weight_action)

        self.join_right_action_g1.setDisabled(True)

    def set_weight_action_triggered(self, state):
        if state:
            self.model.state = SetWeightNodeState(self)
        else:
            self.model.state = DefaultState()

    def reverse_nodes(self, calculate=True):
        super().reverse_nodes(calculate=False)
        self.weights = self.weights[::-1]
        if calculate:
            self.calculate_points()

    def split_curve(self, index):
        n = len(self.nodes) - 1

        first_nodes, first_weights = [], []
        second_nodes, second_weights = [], []
        for k in range(n + 1):
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
        red_pen = QtGui.QPen(self.node_color, 1, QtCore.Qt.DashLine)
        red_brush = QtGui.QBrush(self.node_color)

        node_size = self.node_size
        weights = self.weights
        old_point = self.nodes[0]

        qp.setPen(red_pen)
        qp.setBrush(red_brush)
        qp.drawEllipse(QtCore.QPointF(old_point[0] - 3, old_point[1] - 3), node_size, node_size)

        qp.drawText(old_point[0] + 5, old_point[1] - 3, f'1 ({weights[0]: .2f})')
        for i, point in enumerate(self.nodes[1:], 1):
            qp.setPen(black_pen)
            qp.drawLine(old_point[0], old_point[1], point[0], point[1])

            qp.setPen(red_pen)
            qp.drawEllipse(QtCore.QPointF(point[0] - 3, point[1] - 3), node_size, node_size)

            qp.drawText(point[0] + 5, point[1] - 3, f'{i + 1} ({weights[i]: .2f})')
            old_point = point

    def _rational_de_casteljau(self, i, k, t):
        if (i, k, t) not in self.helper_nodes:
            if i == 0:
                self.helper_weights[(i, k, t)] = self.weights[k]
                self.helper_nodes[(i, k, t)] = np.array(self.nodes[k])
            else:
                w1, W1 = self._rational_de_casteljau(i - 1, k, t)
                w2, W2 = self._rational_de_casteljau(i - 1, k + 1, t)

                u = t / self.resolution
                w = (1 - u) * w1 + u * w2
                W = (1 - u) * w1 / w * W1 + u * w2 / w * W2

                self.helper_weights[(i, k, t)] = w
                self.helper_nodes[(i, k, t)] = W

        return self.helper_weights[(i, k, t)], self.helper_nodes[(i, k, t)]

    def rational_de_casteljau(self, t):
        w, W = self._rational_de_casteljau(len(self.nodes) - 1, 0, t)
        return w, tuple(W)

    def horner(self, t):
        n = len(self.nodes) - 1
        nodes = np.array(self.nodes)
        weights = np.array(self.weights)

        if t <= 0.5:
            u = t / (1 - t)
            numerator = weights[n] * nodes[n]
            denominator = weights[n]
            for i in range(n - 1, -1, -1):
                numerator = numerator * u + weights[i] * nodes[i] * comb(n, i)
                denominator = denominator * u + weights[i] * comb(n, i)
            return tuple(numerator / denominator)

        u = (1 - t) / t
        numerator = weights[0] * nodes[0]
        denominator = weights[0]
        for i in range(n - 1, -1, -1):
            numerator = numerator * u + weights[n-i] * nodes[n-i] * comb(n, n-i)
            denominator = denominator * u + weights[n-i] * comb(n, n-i)
        return tuple(numerator / denominator)

    def join_right_smooth(self, other, c1=True):
        nodes1 = np.array(self.nodes)
        nodes2 = np.array(other.nodes)

        dx, dy = nodes1[-1] - nodes2[0]
        other.translate(dx, dy, calculate=False)
        other.weights[0] = self.weights[-1]

        nodes2 = np.array(other.nodes)
        weights1 = np.array(self.weights)
        weights2 = np.array(other.weights)

        if len(nodes1) > 2 and len(nodes2) > 2:
            join_vec = nodes1[-1] - nodes1[-2]
            other.nodes[1] = tuple(nodes2[0] + join_vec)
            other.weights[1] = 2 * weights1[-1] - weights1[-2]

        other.calculate_points(force=True)

    def _drop_degree_first_method(self):
        n = len(self.nodes) - 2
        nodes = np.array(self.nodes)
        weights = np.array(self.weights)

        vs1 = [nodes[0]]
        ws1 = [weights[0]]
        for i in range(1, (n+1) // 2 + 1):
            w1 = (n+1)/(n+1-i) * weights[i] - i/(n+1-i) * ws1[i-1]
            ws1.append(w1)

            v1 = (n+1)/(n+1-i) * weights[i] / ws1[i] * nodes[i] \
                 - i/(n+1-i) * ws1[i-1] / ws1[i] * vs1[-1]
            vs1.append(v1)

        vs2 = [nodes[-1]]
        ws2 = [weights[-1]]
        for i in range((n+1), (n+1) // 2, -1):
            w2 = (n+1)/i * weights[i] - (n+1-i)/i * ws2[-1]

            v2 = (n+1)/i * weights[i] / w2 * nodes[i] \
                 - (n+1-i)/i * ws2[-1] / w2 * vs2[-1]

            ws2.append(w2)
            vs2.append(v2)

        new_nodes = vs1[:-1] + [(vs1[-1] + vs2[-1]) / 2] + vs2[1:-1][::-1]
        self.nodes = list(map(tuple, new_nodes))

        new_weights = ws1[:-1] + [(ws1[-1] + ws2[-1]) / 2] + ws2[1:-1][::-1]
        self.weights = new_weights

    def _raise_degree(self):
        n = len(self.nodes) - 1
        nodes = np.array(self.nodes)
        weights = np.array(self.weights)

        new_nodes = [nodes[0]]
        new_weights = [(n+1) * weights[0]]

        for i in range(1, n+1):
            weight = i * weights[i-1] + (n+1 - i) * weights[i]
            new_weights.append(weight)

            node = i * weights[i-1] * nodes[i-1] + (n+1 - i) * weights[i] * nodes[i]
            node /= weight
            new_nodes.append(node)

        new_nodes.append(nodes[-1])
        new_weights.append((n+1) * weights[-1])

        self.nodes = [tuple(n) for n in new_nodes]
        self.weights = new_weights

    def raise_degree(self, m):
        for _ in range(m):
            self._raise_degree()
        self.calculate_points()

    def calculate_points(self, force=True, fast=False):
        super(BezierCurve, self).calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        nodes, weights = np.array(self.nodes), np.array(self.weights)

        if fast:
            steps = max(20, self.resolution // 10)

            # Horner algorithm
            points = [self.horner(t) for t in np.linspace(0, 1, steps)]
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

    def to_dict(self):
        data = super().to_dict()

        data["weights"] = self.weights
        return data

    @classmethod
    def from_dict(cls, data, calculate=True):
        curve = super().from_dict(data, calculate=False)
        curve.weights = data["weights"]

        if calculate:
            curve.calculate_points()
        return curve
