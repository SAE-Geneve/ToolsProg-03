from PySide2 import QtGui, QtCore
from unittest import TestCase
from player_model_handler import PlayerModelHandler


class TestPlayerModelHandler(TestCase):
    def test_add_player_to_model(self):
        input_text = "Remy"

        model = QtGui.QStandardItemModel()
        PlayerModelHandler.add_player_to_model(model, id=1, name="Remy")
        self.assertEqual(model.rowCount(), 1)

        item: QtGui.QStandardItem = model.item(0, 0)
        displayed_test = item.data(QtCore.Qt.DisplayRole)
        self.assertEqual(displayed_test, input_text)

    def test_add_player_to_model_no_name(self):
        model = QtGui.QStandardItemModel()
        with self.assertRaises(ValueError):
            PlayerModelHandler.add_player_to_model(model)

