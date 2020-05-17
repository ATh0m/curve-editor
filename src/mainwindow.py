import logging

logger = logging.getLogger('curve-editor')

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from .canvas import Canvas
from .curves import BezierCurve, PolygonalCurve
from .model import CurvesModel

from .states import SelectCurveState, RemoveCurveState, MoveCurveState, DuplicateCurveState

from .ui.MainWindow import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.actionSave.triggered.connect(self.save)
        self.actionLoad.triggered.connect(self.load)
        self.actionNew.triggered.connect(self.new)
        self.actionScreenshot.triggered.connect(self.screenshot)

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

    def model_changed(self):
        logger.info('Update window')

        if self.selected_curve is not self.model.selected_curve:
            if self.selected_curve is not None:
                self.removeToolBar(self.selected_curve.toolbar)

            self.selected_curve = self.model.selected_curve

            if self.selected_curve is not None:
                if self.selected_curve.toolbar is not None:
                    self.addToolBarBreak()
                    self.addToolBar(Qt.TopToolBarArea,
                                    self.selected_curve.toolbar)
                    self.selected_curve.toolbar.show()
                    logger.info("Added toolbar")

    def new_bezier_action_triggered(self):
        curve = BezierCurve("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()

    def new_polygonal_action_triggered(self):
        curve = PolygonalCurve("")
        self.model.add(curve, selected=True)

        curve.add_node_action.trigger()

    def select_curve_action_triggered(self, state):
        logger.info("select curve mode")
        self.model.state = SelectCurveState()

    def add_toolbar(self):
        new_bezier_action = QtWidgets.QAction("New Bezier", self)
        # button_action.setStatusTip("This is your button")
        new_bezier_action.triggered.connect(self.new_bezier_action_triggered)
        self.toolBar.addAction(new_bezier_action)

        new_polygonal_action = QtWidgets.QAction("New Polygonal", self)
        # button_action.setStatusTip("This is your button")
        new_polygonal_action.triggered.connect(self.new_polygonal_action_triggered)
        self.toolBar.addAction(new_polygonal_action)

        select_action = QtWidgets.QAction("Select curve", self)
        select_action.triggered.connect(self.select_curve_action_triggered)
        self.toolBar.addAction(select_action)

        remove_curve_action = QtWidgets.QAction("Remove curve", self)
        remove_curve_action.triggered.connect(self.remove_curve_action_triggered)
        self.toolBar.addAction(remove_curve_action)

        move_curve_action = QtWidgets.QAction("Move curve", self)
        move_curve_action.triggered.connect(self.move_curve_action_triggered)
        self.toolBar.addAction(move_curve_action)

        duplicate_curve_action = QtWidgets.QAction("Duplicate curve", self)
        duplicate_curve_action.triggered.connect(self.duplicate_curve_action_triggered)
        self.toolBar.addAction(duplicate_curve_action)

        # self.addToolBarBreak()

    def curve_selected(self, index):
        index = index.row()
        logger.info(index)

        self.model.select(index)

    def remove_curve_action_triggered(self, state):
        logger.info("remove curve mode")
        self.model.state = RemoveCurveState()

    def move_curve_action_triggered(self, state):
        logger.info("move curve mode")
        self.model.state = MoveCurveState()

    def duplicate_curve_action_triggered(self, state):
        self.model.state = DuplicateCurveState()

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
