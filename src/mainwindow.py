import logging

logger = logging.getLogger('curve-editor')

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from .canvas import Canvas
from .curvedetails import CurveDetails
from .curves import BezierCurve, PolygonalCurve
from .model import CurvesModel

from .states import SelectCurveState

from .ui.MainWindow import Ui_MainWindow
from .ui.NewCurve import Ui_NewCurve


class NewCurveDialog(QtWidgets.QDialog, Ui_NewCurve):
    def __init__(self, *args, obj=None, **kwargs):
        super(NewCurveDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.typesList.addItems(["Bezier Curve", "Polygonal Curve"])


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
        self.listView.doubleClicked['QModelIndex'].connect(self.curve_details)
        self.listView.clicked['QModelIndex'].connect(self.curve_selected)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(self.canvas)
        self.graphicsView.setScene(scene)

        self.addCurve.clicked.connect(self.add_new_curve)
        self.removeCurve.clicked.connect(self.remove_curve)

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
        curve = BezierCurve('')
        self.model.add(curve, selected=True)

        curve.add_point_action.trigger()

    def select_curve_action(self, state):
        logger.info("select curve mode")
        self.model.state = SelectCurveState()
        pass

    def add_toolbar(self):
        new_bezier_action = QtWidgets.QAction("New Bezier", self)
        # button_action.setStatusTip("This is your button")
        new_bezier_action.triggered.connect(self.new_bezier_action_triggered)
        # new_bezier_action.setCheckable(True)
        self.toolBar.addAction(new_bezier_action)

        select_action = QtWidgets.QAction("Select curve", self)
        select_action.triggered.connect(self.select_curve_action)
        self.toolBar.addAction(select_action)

        # self.addToolBarBreak()

    def curve_details(self, index):
        details = CurveDetails(index.row(), parent=self)
        details.setModel(self.model)
        details.show()

    def curve_selected(self, index):
        index = index.row()
        logger.info(index)

        self.model.select(index)

    def add_new_curve(self):
        dialog = NewCurveDialog(parent=self)
        if dialog.exec_():
            name = dialog.name_line.text()
            type_ = dialog.typesList.currentText()

            if type_ == 'Bezier Curve':
                curve = BezierCurve.from_dict({"name": name, "type": type_})
            else:
                curve = PolygonalCurve.from_dict({"name": name, "type": type_})

            self.model.add(curve)
            self.model.layoutChanged.emit()

    def remove_curve(self):
        self.model.remove_selected()

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
