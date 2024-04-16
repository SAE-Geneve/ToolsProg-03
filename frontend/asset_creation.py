import itertools

from PySide2 import QtCore, QtWidgets, QtGui
from globals import GameState, Role
from models import Player, Game
from typing import List, Dict

class CreatePlayerDialog(QtWidgets.QDialog):
    new_player = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent,
                         f=QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Create new Player")

        name_label = QtWidgets.QLabel("Name")
        self.input_name = QtWidgets.QLineEdit()
        self.input_name.setPlaceholderText("Enter a name")

        elo_label = QtWidgets.QLabel("Elo")
        elo_validator = QtGui.QIntValidator()
        elo_validator.setBottom(0)
        self.input_elo = QtWidgets.QLineEdit()
        self.input_elo.setValidator(elo_validator)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.input_name)

        elo_layout = QtWidgets.QHBoxLayout()
        elo_layout.addWidget(elo_label)
        elo_layout.addWidget(self.input_elo)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.dialog_accepted)
        button_box.rejected.connect(self.dialog_cancelled)

        box_layout_3 = QtWidgets.QVBoxLayout(self)
        box_layout_3.addLayout(name_layout)
        box_layout_3.addLayout(elo_layout)
        box_layout_3.addWidget(button_box)

    def reset_ui(self):
        self.input_elo.setText("0")
        self.input_name.clear()
        self.input_name.setFocus()

    def showEvent(self, *args, **kwargs):
        self.reset_ui()
        super().showEvent(*args, **kwargs)

    @QtCore.Slot()
    def dialog_accepted(self):
        name = self.input_name.text()
        elo = int(self.input_elo.text())
        if name == "":
            QtWidgets.QMessageBox.warning(self, "Error", "Name cannot be empty")
            return

        self.new_player.emit({"name": name, "elo": elo})
        self.close()

    @QtCore.Slot()
    def dialog_cancelled(self):
        self.close()


class CreateGameDialog(QtWidgets.QDialog):
    new_game = QtCore.Signal(dict)

    def __init__(self, players_model: QtGui.QStandardItemModel, parent=None):
        super().__init__(parent,
                         f=QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Create new Game")

        self.players_model = players_model

        first_player_label = QtWidgets.QLabel("First player")
        second_player_label = QtWidgets.QLabel("Second player")
        winner_label = QtWidgets.QLabel("Winner (if any)")
        game_state_label = QtWidgets.QLabel("Game state")

        self.first_player_combo_box = QtWidgets.QComboBox()
        self.second_player_combo_box = QtWidgets.QComboBox()
        self.winner_combo_box = QtWidgets.QComboBox()
        self.game_state_combo_box = QtWidgets.QComboBox()
        self.game_state_combo_box.addItems([state.name for state in GameState])

        table_layout = QtWidgets.QGridLayout()

        table_layout.addWidget(first_player_label, 0, 0)
        table_layout.addWidget(second_player_label, 1, 0)
        table_layout.addWidget(winner_label, 2, 0)
        table_layout.addWidget(game_state_label, 3, 0)

        table_layout.addWidget(self.first_player_combo_box, 0, 1)
        table_layout.addWidget(self.second_player_combo_box, 1, 1)
        table_layout.addWidget(self.winner_combo_box, 2, 1)
        table_layout.addWidget(self.game_state_combo_box, 3, 1)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.dialog_accepted)
        button_box.rejected.connect(self.dialog_cancelled)

        box_layout_3 = QtWidgets.QVBoxLayout(self)
        box_layout_3.addLayout(table_layout)
        box_layout_3.addWidget(button_box)

    def get_players(self) -> List[Player]:
        player_items: List[QtGui.QStandardItem] = [self.players_model.item(row, 0) for row in range(self.players_model.rowCount())]
        return [item.data(Role.WHOLE_DATA_ROLE.value) for item in player_items]

    def reset_ui(self):
        player_names = [player.name for player in self.get_players()]
        self.first_player_combo_box.addItems(player_names)
        self.second_player_combo_box.addItems(player_names)
        self.winner_combo_box.addItems(list(itertools.chain(player_names, ["No winner"])))

    def showEvent(self, *args, **kwargs):
        self.reset_ui()
        super().showEvent(*args, **kwargs)

    @QtCore.Slot()
    def dialog_accepted(self):
        players: Dict[str, Player] = {player.name: player for player in self.get_players()}

        player_one = players[self.first_player_combo_box.currentText()]
        player_two = players[self.second_player_combo_box.currentText()]
        winner = players.get(self.winner_combo_box.currentText())
        game_state = GameState[self.game_state_combo_box.currentText()]

        self.new_game.emit({"state": game_state.value, "winner": dict(winner),
                            "players": [dict(player_one), dict(player_two)]})
        self.close()

    @QtCore.Slot()
    def dialog_cancelled(self):
        self.close()
