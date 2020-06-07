from .curves import Curve


class PolygonalCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Polygonal Curve"

        self.highlight_color.setAlpha(100)

    def calculate_points(self, force=True, fast=False):
        super().calculate_points()

        self.points = self.nodes
        return self.points
