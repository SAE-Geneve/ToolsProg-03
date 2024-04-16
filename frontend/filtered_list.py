from PySide2 import QtCore, QtGui, QtWidgets


class FilteredListWidget(QtWidgets.QWidget):
    selection_changed = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.filter_box = QtWidgets.QLineEdit(parent=self)

        self.source_model = QtGui.QStandardItemModel(parent=self)
        self.proxy_model = QtCore.QSortFilterProxyModel(parent=self)

        self.list_view = QtWidgets.QListView(parent=self)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.proxy_model.setSourceModel(self.source_model)
        self.list_view.setModel(self.proxy_model)

        self.filter_box.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.list_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.filter_box)
        main_layout.addWidget(self.list_view)
        self.setLayout(main_layout)

    @QtCore.Slot(QtCore.QItemSelection)
    def on_selection_changed(self, newly_selected_items: QtCore.QItemSelection):
        current_selection = self.list_view.selectionModel().selection()
        source_selection = self.proxy_model.mapSelectionToSource(current_selection)
        source_indexes = source_selection.indexes()
        selected_items = [self.source_model.itemFromIndex(index) for index in source_indexes]
        self.selection_changed.emit(selected_items)

    @property
    def filter_widget(self) -> QtWidgets.QLineEdit:
        return self.filter_box

    @property
    def proxy(self) -> QtCore.QSortFilterProxyModel:
        return self.proxy_model

    @property
    def model(self) -> QtGui.QStandardItemModel:
        return self.source_model

    @property
    def view(self) -> QtWidgets.QListView:
        return self.list_view