import logging

logger = logging.getLogger('curve-editor')

import numpy as np
from scipy.special import comb

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog

from .curves import Curve

from src.states import SplitCurveState, DefaultState


class JoinRightSmoothState(DefaultState):
    def __init__(self, curve, method):
        super().__init__()
        self.curve = curve
        self.method = method

        self.controller = self.curve.join_right_action_c1
        if self.method == "G1":
            self.controller = self.curve.join_right_action_g1

    def enable(self):
        if not self.controller.isChecked():
            self.controller.trigger()

    def disable(self):
        self.controller.setChecked(False)

    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()
        curve = self.curve

        index, dist = canvas.model.distance_to_nearest_curve(x, y)

        logger.info("Joining")

        if dist is not None and dist < 10:
            other = canvas.model.curves[index]
            if isinstance(other, BezierCurve):
                curve.join_right_smooth(other, c1=(self.method == "C1"))
                canvas.model.updated()

        canvas.model.state = self.next_state()


class BezierCurve(Curve):
    type = "Bezier Curve"

    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.helper_nodes = {}

    def add_node(self, x, y, calculate=True):
        self.nodes.append((x, y))
        if calculate:
            self.calculate_points(force=False)

    def setup_toolbar(self, parent):
        super().setup_toolbar(parent)

        self.extra_toolbar = QtWidgets.QToolBar()

        self.split_curve_action = QtWidgets.QAction("Split curve", parent)
        self.split_curve_action.triggered.connect(self.split_curve_action_triggered)
        self.split_curve_action.setCheckable(True)
        self.extra_toolbar.addAction(self.split_curve_action)

        self.raise_degree_action = QtWidgets.QAction("Raise degree", parent)
        self.raise_degree_action.triggered.connect(self.raise_degree_action_triggered)
        self.extra_toolbar.addAction(self.raise_degree_action)

        self.drop_degree_button = QtWidgets.QToolButton(parent)
        self.drop_degree_button.setText("Drop degree ▶")
        self.drop_degree_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        drop_degree_menu = QtWidgets.QMenu(self.drop_degree_button)

        self.drop_degree_first_action = QtWidgets.QAction("First method", parent)
        self.drop_degree_first_action.triggered.connect(self.drop_degree_first_action_triggered)
        drop_degree_menu.addAction(self.drop_degree_first_action)

        self.drop_degree_button.setMenu(drop_degree_menu)
        self.extra_toolbar.addWidget(self.drop_degree_button)

        self.join_right_button = QtWidgets.QToolButton(parent)
        self.join_right_button.setText("Join right ▶")
        self.join_right_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        join_right_menu = QtWidgets.QMenu(self.join_right_button)

        self.join_right_action_c1 = QtWidgets.QAction("C1", parent)
        self.join_right_action_c1.triggered.connect(self.join_right_action_c1_triggered)
        self.join_right_action_c1.setCheckable(True)
        join_right_menu.addAction(self.join_right_action_c1)

        self.join_right_action_g1 = QtWidgets.QAction("G1", parent)
        self.join_right_action_g1.triggered.connect(self.join_right_action_g1_triggered)
        self.join_right_action_g1.setCheckable(True)
        join_right_menu.addAction(self.join_right_action_g1)

        self.join_right_button.setMenu(join_right_menu)
        self.extra_toolbar.addWidget(self.join_right_button)

    def split_curve_action_triggered(self, state):
        if state:
            self.model.state = SplitCurveState(self)
        else:
            self.model.state = DefaultState()

    def split_curve(self, index):
        n = len(self.nodes) - 1

        first_nodes = [tuple(self._de_casteljau(k, 0, index))
                       for k in range(n + 1)]

        second_nodes = [tuple(self._de_casteljau(k, n - k, index))
                        for k in range(n + 1)]

        first_curve = self.clone()
        second_curve = self.clone()

        first_curve.nodes = first_nodes
        first_curve.calculate_points(force=True)

        second_curve.nodes = second_nodes
        second_curve.calculate_points(force=True)

        return first_curve, second_curve

    def dist(point_1: QtCore.QPointF, point_2: QtCore.QPointF) -> float:
        return np.sqrt(
            np.power(point_1.x() - point_2.x(), 2) + np.power(point_1.y() - point_2.y(), 2)
        )

    def vector_length(vector: QtCore.QPointF) -> float:
        return np.sqrt(np.power(vector.x(), 2) + np.power(vector.y(), 2))

    def join_right_smooth(self, other, c1=True):
        nodes1 = np.array(self.nodes)
        nodes2 = np.array(other.nodes)

        dx, dy = nodes1[-1] - nodes2[0]
        other.translate(dx, dy, calculate=False)
        nodes2 = np.array(other.nodes)

        if len(nodes1) > 2 and len(nodes2) > 2:
            join_vec = nodes1[-1] - nodes1[-2]
            if not c1:
                join_vec *= np.linalg.norm(nodes2[0] - nodes2[1]) / np.linalg.norm(join_vec)
            other.nodes[1] = tuple(nodes2[0] + join_vec)

        other.calculate_points(force=True)

    def _drop_degree_first_method(self):
        n = len(self.nodes) - 1
        nodes = np.array(self.nodes)

        ws1 = [nodes[0]]
        for k in range(1, n // 2 + 1):
            w1 = (1 + k / (n - k)) * nodes[k] - k / (n - k) * ws1[k - 1]
            ws1.append(w1)

        ws2 = [nodes[-1]]
        for k in range(n, n // 2, -1):
            w2 = n / k * nodes[k] + (1 - n / k) * ws2[-1]
            ws2.append(w2)

        new_nodes = ws1[:-1] + [(ws1[-1] + ws2[-1]) / 2] + ws2[1:-1][::-1]
        new_nodes = list(map(tuple, new_nodes))

        self.nodes = new_nodes

    def drop_degree_first_method(self, m=1):
        for i in range(m):
            self._drop_degree_first_method()
        self.calculate_points()

    def drop_degree_first_action_triggered(self, state):
        degree, ok = QInputDialog().getInt(self.model.parent,
                                           "Drop degree (first method)",
                                           "Drop by:",
                                           value=1,
                                           min=1,
                                           max=100,
                                           step=1)
        if ok and degree > 0:
            logger.info(f"Degree dropping (first method): +{degree}")
            self.drop_degree_first_method(degree)
            self.model.updated()

    def raise_degree(self, m):
        nodes = [np.array(node) for node in self.nodes]
        n = len(nodes) - 1

        new_nodes = []

        for i in range(n + m + 1):
            node = sum(nodes[k] * comb(n, k) * comb(m, i - k) * comb(n + m, i) ** (-1)
                       for k in range(max(0, i - m), min(i, n) + 1))
            new_nodes.append(tuple(node))

        self.nodes = new_nodes
        self.calculate_points()

    def raise_degree_action_triggered(self, state):
        degree, ok = QInputDialog().getInt(self.model.parent,
                                           "Raise degree",
                                           "Raise by:",
                                           value=1,
                                           min=1,
                                           max=100,
                                           step=1)
        if ok and degree > 0:
            logger.info(f"Degree raising: +{degree}")
            self.raise_degree(degree)
            self.model.updated()

    def join_right_action_c1_triggered(self, state):
        if state:
            self.model.state = JoinRightSmoothState(self, "C1")
        else:
            self.model.state = DefaultState()

    def join_right_action_g1_triggered(self, state):
        if state:
            self.model.state = JoinRightSmoothState(self, "G1")
        else:
            self.model.state = DefaultState()

    def __approximate_length(self):
        if len(self.nodes) < 2:
            return 0.0

        length = 0.
        for i in range(len(self.nodes) - 1):
            x, y = self.nodes[i]
            next_x, next_y = self.nodes[i + 1]

            length += np.sqrt((next_x - x) ** 2 + (next_y - y) ** 2)

        return length

    def _de_casteljau(self, k, i, t):
        if (k, i, t) not in self.helper_nodes:
            if k == 0:
                self.helper_nodes[(k, i, t)] = np.array(self.nodes[i])
            else:
                u = t / self.resolution
                self.helper_nodes[(k, i, t)] = (1 - u) * self._de_casteljau(k - 1, i, t) + \
                                               u * self._de_casteljau(k - 1, i + 1, t)
        return self.helper_nodes[(k, i, t)]

    def de_casteljau(self, t):
        return tuple(self._de_casteljau(len(self.nodes) - 1, 0, t))

    def horner(self, t):
        n = len(self.nodes) - 1
        nodes = np.array(self.nodes)

        if t <= 0.5:
            u = t / (1 - t)
            value = nodes[n]
            for i in range(n - 1, -1, -1):
                value = value * u + nodes[i] * comb(n, i)
            value *= (1 - t) ** n
            return tuple(value)

        u = (1 - t) / t
        value = nodes[0]
        for i in range(n - 1, -1, -1):
            value = value * u + nodes[n - i] * comb(n, n - i)
        value *= t ** n
        return tuple(value)

    def calculate_points(self, force=True, fast=False):
        super().calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        if fast:
            steps = max(20, self.resolution // 10)

            # Horner algorithm
            points = [self.horner(t) for t in np.linspace(0, 1, steps)]
            self.points = points
            return self.points

        if force:
            self.helper_nodes = {}

        steps = self.resolution

        # De Casteljau Algorithm
        points = [self.de_casteljau(i) for i in range(steps + 1)]

        self.points = points
        return self.points

    def draw_nodes(self, qp: QtGui.QPainter):
        black_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        red_pen = QtGui.QPen(self.node_color, 1, QtCore.Qt.DashLine)
        red_brush = QtGui.QBrush(self.node_color)

        node_size = self.node_size
        old_point = self.nodes[0]

        qp.setPen(red_pen)
        qp.setBrush(red_brush)
        qp.drawEllipse(QtCore.QPointF(old_point[0] - 3, old_point[1] - 3), node_size, node_size)

        qp.drawText(old_point[0] + 5, old_point[1] - 3, '1')
        for i, point in enumerate(self.nodes[1:]):
            i += 2
            qp.setPen(black_pen)
            qp.drawLine(old_point[0], old_point[1], point[0], point[1])

            qp.setPen(red_pen)
            qp.drawEllipse(QtCore.QPointF(point[0] - 3, point[1] - 3), node_size, node_size)

            qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)
            old_point = point
