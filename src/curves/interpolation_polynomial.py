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

