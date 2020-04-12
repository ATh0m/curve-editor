from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from .ui.MainWindow import Ui_MainWindow
from .canvas import Canvas

class PointsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, points=None, **kwargs):
        super(PointsModel, self).__init__(*args, **kwargs)
        self.points = points or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure.
            x, y = self.points[index.row()]
            # Return the todo text only.
            return f"({x}, {y})"

    def rowCount(self, index):
        return len(self.points)

data = [
    ("Curve #1", [
        ("(100, 200)", []),
    ]),
]

class Food(object):
    def __init__(self, name, shortDescription, note, parent = None):
        self.data = (name, shortDescription, note);
        self.parentIndex = parent

class FavoritesTableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)
        self.foods = []
        self.loadData()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.foods[index.row()].data[index.column()]
        return None

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.foods)

    def columnCount(self, index=QtCore.QModelIndex()):
        return 3

    # def index(self, row, column, parent = QtCore.QModelIndex()):
    #     return self.createIndex(row, column, parent)

    def loadData(self):
        allFoods=("Apples", "Pears", "Grapes", "Cookies", "Stinkberries")
        allDescs = ("Red", "Green", "Purple", "Yummy", "Huh?")
        allNotes = ("Bought recently", "Kind of delicious", "Weird wine grapes",
                    "So good...eat with milk", "Don't put in your nose")
        for name, shortDescription, note in zip(allFoods, allDescs, allNotes):
            food = Food(name, shortDescription, note)
            self.foods.append(food)

class Model(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.items=[]
        self.modelDict={}

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, index=QtCore.QModelIndex()):
        return 3

    def data(self, index, role):
        if not index.isValid() or not (0<=index.row()<len(self.items)): return QtCore.QVariant()
        if role==QtCore.Qt.DisplayRole:          return QtCore.QVariant(self.items[index.row()])

    def buildItems(self):
        totalItems=self.rowCount()
        for key in self.modelDict:
            self.beginInsertRows(QtCore.QModelIndex(), totalItems+1, 0)
            self.items.append(key)
            self.endInsertRows()

elements={'Animals':{1:'Bison',2:'Panther',3:'Elephant'},'Birds':{1:'Duck',2:'Hawk',3:'Pigeon'},'Fish':{1:'Shark',2:'Salmon',3:'Piranha'}}



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.model = PointsModel(points=[(100, 200)])
        # self.listView.setModel(self.model)

        # self.model = QtGui.QStandardItemModel()
        # self.addItems(self.model, data)

        # self.model = FavoritesTableModel()

        self.model = Model()
        self.model.modelDict = elements
        self.model.buildItems()

        self.treeView.setModel(self.model)

        self.canvas = Canvas(self.model)
        self.layout.addWidget(self.canvas)

    def addItems(self, parent, elements):
        for text, children in elements:
            item = QtGui.QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.addItems(item, children)