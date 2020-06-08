import logging

import numpy as np
from PyQt5 import QtWidgets

from .curves import Curve

logger = logging.getLogger('curve-editor')


class InterpolationPolynomialCurve(Curve):
    type = "Interpolation Polynomial Curve"

    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.nodes_type = "chebyshev"  # "equidistant"

    def chebyshev_type_action_triggered(self, state):
        if self.nodes_type != "chebyshev":
            self.nodes_type = "chebyshev"
            self.calculate_points()
            self.model.updated()

    def equidistant_type_action_triggered(self, state):
        if self.nodes_type != "equidistant":
            self.nodes_type = "equidistant"
            self.calculate_points()
            self.model.updated()

    def setup_toolbar(self, parent):
        super().setup_toolbar(parent)

        self.extra_toolbar = QtWidgets.QToolBar()

        self.nodes_type_button = QtWidgets.QToolButton(parent)
        self.nodes_type_button.setText("Nodes type ▶")
        self.nodes_type_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        nodes_type_menu = QtWidgets.QMenu(self.nodes_type_button)

        self.chebyshev_type_action = QtWidgets.QAction("Chebyshev", parent)
        self.chebyshev_type_action.triggered.connect(self.chebyshev_type_action_triggered)
        self.chebyshev_type_action.setCheckable(True)
        nodes_type_menu.addAction(self.chebyshev_type_action)

        self.equidistant_type_action = QtWidgets.QAction("Equidistant", parent)
        self.equidistant_type_action.triggered.connect(self.equidistant_type_action_triggered)
        self.equidistant_type_action.setCheckable(True)
        nodes_type_menu.addAction(self.equidistant_type_action)

        self.nodes_type_button.setMenu(nodes_type_menu)
        self.extra_toolbar.addWidget(self.nodes_type_button)

    def calculate_points(self, force=True, fast=False):
        super().calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        n = len(self.nodes) - 1
        nodes = np.array(self.nodes)

        if self.nodes_type == "equidistant":
            # Equidistant nodes
            ts = np.linspace(0, 1, n + 1)
            omegas = [(-1) ** i * n ** n / (np.math.factorial(i) * np.math.factorial(n - i))
                      for i in range(n + 1)]
        else:
            # Chebyshev nodes
            ts = np.array([np.cos((2 * i + 1) * np.pi / (2 * n + 2)) for i in range(n + 1)])
            omegas = [(-1) ** i * 2 ** (-3 * n) * (n + 1) * np.sin((2 * i + 1) * np.pi / (2 * n + 2)) ** (-1)
                      for i in range(n + 1)]

        def p(t):
            k = np.argmin(np.abs(ts - t))
            if abs(ts[k] - t) < 1e-5:
                return nodes[k]

            denominator = sum(omegas[i] / (t - ts[i]) for i in range(n + 1))
            numerator = sum(nodes[i] * omegas[i] / (t - ts[i]) for i in range(n + 1))

            return numerator / denominator

        steps = self.resolution
        if fast:
            steps = max(20, self.resolution // 10)
        points = [tuple(p(t)) for t in np.linspace(ts[0], ts[-1], steps)]

        self.points = points
        return self.points

    def to_dict(self):
        data = super().to_dict()

        data["nodes_type"] = self.nodes_type
        return data

    @classmethod
    def from_dict(cls, data, calculate=True):
        curve = super().from_dict(data, calculate=False)
        curve.nodes_type = data["nodes_type"]

        if calculate:
            curve.calculate_points()
        return curve
