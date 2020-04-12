from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

selected = set()

class PointItem:
    def __init__(self, point, parent=None):
        self.parentItem = parent
        self.itemData = [point]
        self.checkedState = False
        self.isCheckable = False

    def childCount(self):
        return 0

    def columnCount(self):
        return 1

    def data(self, column):
        return str(self.itemData[0])

    def parent(self):
        return self.parentItem

    def row(self):
        return self.parentItem.childItems.index(self)

    def setCheckedState(self, value):
        if value == 2:
            self.checkedState = True
            selected.add('/'.join(self.parentItem.path)+'/'+self.itemData[0])
        else:
            self.checkedState = False
            selected.remove('/'.join(self.parentItem.path)+'/'+self.itemData[0])
        print(selected)

    def getCheckedState(self):
        if self.checkedState:
            return Qt.Checked
        else:
            return Qt.Unchecked

class CurveItem():
    def __init__(self, name, parent=None):
        self.parentItem = parent
        self.name = name
        self.type = 'Bezier'
        self.checkedState = False
        self.isCheckable = True
        self.childItems = []

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 2

    def setCheckedState(self, value):
        if value == 2:
            self.checkedState = True
            selected.add('/'.join(self.name))
        else:
            self.checkedState = False
            selected.remove('/'.join(self.name))
        print(selected)

    def getCheckedState(self):
        if self.checkedState:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def data(self, column):
        if column == 0:
            return self.name
        else:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

class CurvesModel(QAbstractItemModel):
    column_names = ['Name', 'Type']

    def __init__(self, parent=None):
        super().__init__(parent)

        self.rootItem = CurveItem(name='root')

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.CheckStateRole and index.column() == 0:
            return item.getCheckedState()
        else:
            return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            item = index.internalPointer()
            item.setCheckedState(value)

        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        item = index.internalPointer()

        if not item.isCheckable:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.column_names[section]

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()
