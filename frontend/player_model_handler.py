from PySide2 import QtGui, QtCore


class PlayerModelHandler:
    @staticmethod
    def add_player_to_model(model: QtGui.QStandardItemModel, **data):
        name: str = data.get("name")
        if name is None:
            raise ValueError("Player should have a name!")

        item = QtGui.QStandardItem()
        item.setData(name, QtCore.Qt.DisplayRole)
        model.appendRow([item])


