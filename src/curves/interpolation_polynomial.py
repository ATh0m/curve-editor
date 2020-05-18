import logging

logger = logging.getLogger('curve-editor')

import math
import numpy as np
from scipy.special import comb

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog

from .curves import Curve

from src.states import SplitCurveState, DefaultState

class InterpolationPolynomialCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Interpolation Polynomial Curve"

    def calculate_points(self, force=False):
        super().calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        steps = self.resolution

        n = len(self.nodes) - 1
        ts = np.array([np.cos((2*i + 1) * np.pi / (2*n + 2)) for i in range(n+1)])

        # Chebyshev nodes
        omegas = [(-1)**i * 2**(-3*n) * (n+1) * np.sin((2*i+1) * np.pi / (2*n+2))**(-1)
                  for i in range(n+1)]

        xs = [x for x, _ in self.nodes]
        ys = [y for _, y in self.nodes]

        nodes = np.array(self.nodes)

        def p(t):
            k = np.argmin(np.abs(ts - t))
            if abs(ts[k] - t) < 1e-5:
                return nodes[k]

            denominator = sum(omegas[i] / (t - ts[i]) for i in range(n+1))
            numerator = sum(nodes[i] * omegas[i] / (t - ts[i]) for i in range(n+1))

            return numerator / denominator

        steps = self.resolution
        points = [tuple(p(t)) for t in np.linspace(ts[0], ts[-1], steps)]

        self.points = points
        return self.points