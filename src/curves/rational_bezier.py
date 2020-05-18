import math
import numpy as np
from scipy.special import comb

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog

from . import BezierCurve

from src.states import SplitCurveState, DefaultState

import logging

logger = logging.getLogger('curve-editor')


class RationalBezierCurve(BezierCurve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.weights = []
        self.type = "Rational Bezier Curve"

    def add_node(self, x, y):
        self.nodes.append((x, y))
        self.weight.append(1.0)
        self.calculate_points(force=False)