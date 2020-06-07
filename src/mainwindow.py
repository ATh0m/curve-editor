import logging

logger = logging.getLogger('curve-editor')

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from .canvas import Canvas
from .curves import BezierCurve, PolygonalCurve, InterpolationPolynomialCurve, RationalBezierCurve, CubicSpline
from .model import CurvesModel

from .states import SelectCurveState, RemoveCurveState, MoveCurveState, DuplicateCurveState, DefaultState

from .ui.MainWindow import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.actionSave.triggered.connect(self.save)
        self.actionLoad.triggered.connect(self.load)
        self.actionNew.triggered.connect(self.new)
        self.actionScreenshot.triggered.connect(self.screenshot)

        self.actionToggleCurvesList.triggered.connect(self.toggle_curves_list)

        self.selected_curve = None

        self.model = CurvesModel(parent=self)
        self.model.layoutChanged.connect(self.model_changed)

        self.canvas = Canvas()
        self.canvas.setModel(self.model)

        self.listView.setModel(self.model)
        self.listView.clicked['QModelIndex'].connect(self.curve_selected)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(self.canvas)
        self.graphicsView.setScene(scene)

        self.model.updated()
        self.add_toolbar()

        self.dockWidget.hide()

    def model_changed(self):
        logger.info('Update window')

        if self.selected_curve is not self.model.selected_curve:
            if self.selected_curve is not None:
                self.removeToolBar(self.selected_curve.toolbar)
                if self.selected_curve.extra_toolbar is not None:
                    self.removeToolBar(self.selected_curve.extra_toolbar)

            self.selected_curve = self.model.selected_curve

            if self.selected_curve is not None:
                if self.selected_curve.toolbar is not None:
                    self.addToolBarBreak()
                    self.addToolBar(Qt.LeftToolBarArea,
                                    self.selected_curve.toolbar)
                    self.selected_curve.toolbar.show()

                    if self.selected_curve.extra_toolbar is not None:
                        self.addToolBarBreak()
                        self.addToolBar(Qt.LeftToolBarArea,
                                        self.selected_curve.extra_toolbar)
                        self.selected_curve.extra_toolbar.show()

                    logger.info("Added toolbar")

    def new_bezier_action_triggered(self):
        curve = BezierCurve("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()
        curve.show_nodes_action.trigger()

    def new_rational_bezier_action_triggered(self):
        curve = RationalBezierCurve("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()
        curve.show_nodes_action.trigger()

    def new_polygonal_action_triggered(self):
        curve = PolygonalCurve("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()
        curve.show_nodes_action.trigger()

    def new_polynomial_action_triggered(self):
        curve = InterpolationPolynomialCurve("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()
        curve.show_nodes_action.trigger()

    def new_cubic_spline_action_triggered(self):
        curve = CubicSpline("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()
        curve.show_nodes_action.trigger()

    def select_curve_action_triggered(self, state):
        if state:
            logger.info("select curve mode")
            self.model.state = SelectCurveState(self)
        else:
            self.model.state = DefaultState()

    def add_toolbar(self):
        new_curve_button = QtWidgets.QToolButton(self)
        new_curve_button.setText("New Curve ▼")
        new_curve_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        new_curve_menu = QtWidgets.QMenu(new_curve_button)

        new_bezier_action = QtWidgets.QAction("New Bezier", self)
        new_bezier_action.triggered.connect(self.new_bezier_action_triggered)
        new_curve_menu.addAction(new_bezier_action)

        new_rational_bezier_action = QtWidgets.QAction("New Rational Bezier", self)
        new_rational_bezier_action.triggered.connect(self.new_rational_bezier_action_triggered)
        new_curve_menu.addAction(new_rational_bezier_action)

        new_polygonal_action = QtWidgets.QAction("New Polygonal", self)
        new_polygonal_action.triggered.connect(self.new_polygonal_action_triggered)
        new_curve_menu.addAction(new_polygonal_action)

        new_polynomial_action = QtWidgets.QAction("New Polynomial", self)
        new_polynomial_action.triggered.connect(self.new_polynomial_action_triggered)
        new_curve_menu.addAction(new_polynomial_action)

        new_cubic_spline_action = QtWidgets.QAction("New Cubic Spline", self)
        new_cubic_spline_action.triggered.connect(self.new_cubic_spline_action_triggered)
        new_curve_menu.addAction(new_cubic_spline_action)

        new_curve_button.setMenu(new_curve_menu)
        self.toolBar.addWidget(new_curve_button)

        self.select_action = QtWidgets.QAction("Select curve", self)
        self.select_action.triggered.connect(self.select_curve_action_triggered)
        self.select_action.setCheckable(True)
        self.toolBar.addAction(self.select_action)

        self.remove_curve_action = QtWidgets.QAction("Remove curve", self)
        self.remove_curve_action.triggered.connect(self.remove_curve_action_triggered)
        self.remove_curve_action.setCheckable(True)
        self.toolBar.addAction(self.remove_curve_action)

        self.move_curve_action = QtWidgets.QAction("Move curve", self)
        self.move_curve_action.triggered.connect(self.move_curve_action_triggered)
        self.move_curve_action.setCheckable(True)
        self.toolBar.addAction(self.move_curve_action)

        self.duplicate_curve_action = QtWidgets.QAction("Duplicate curve", self)
        self.duplicate_curve_action.triggered.connect(self.duplicate_curve_action_triggered)
        self.duplicate_curve_action.setCheckable(True)
        self.toolBar.addAction(self.duplicate_curve_action)

        # self.addToolBarBreak()

    def curve_selected(self, index):
        index = index.row()
        logger.info(index)

        self.model.select(index)

    def remove_curve_action_triggered(self, state):
        if state:
            logger.info("remove curve mode")
            self.model.state = RemoveCurveState(self)
        else:
            self.model.state = DefaultState()

    def move_curve_action_triggered(self, state):
        if state:
            logger.info("move curve mode")
            self.model.state = MoveCurveState(self)
        else:
            self.model.state = DefaultState()

    def duplicate_curve_action_triggered(self, state):
        if state:
            self.model.state = DuplicateCurveState(self)
        else:
            self.model.state = DefaultState()

    def toggle_curves_list(self):
        if self.dockWidget.isHidden():
            self.dockWidget.show()
        else:
            self.dockWidget.hide()

    def screenshot(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            "Screenshot",
                                                            "",
                                                            "PNG (*.png)",
                                                            options=options)

        if filename:
            if not filename.endswith(".png"):
                filename += ".png"

            self.canvas.screenshot(filename)

    def new(self):
        self.model.new()

    def save(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            "Save",
                                                            "",
                                                            "JSON (*.json)",
                                                            options=options)

        if filename:
            if not filename.endswith(".json"):
                filename += ".json"

            self.model.save(filename)

    def load(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            "Open",
                                                            "",
                                                            "JSON (*.json)",
                                                            options=options)

        if filename:
            if not filename.endswith(".json"):
                filename += ".json"

            self.model.load(filename)
