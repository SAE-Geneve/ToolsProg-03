from PySide2 import QtCore, QtGui, QtWidgets
import requests
from typing import List, Optional, Any
from enum import Enum
from globals import GameState
from pydantic import BaseModel


class Role(Enum):
    WHOLE_DATA_ROLE = QtCore.Qt.UserRole + 1
    ID_ROLE = QtCore.Qt.UserRole + 2


class Player(BaseModel):
    id: int
    name: str
    elo: int = 0

    def __hash__(self):
        return hash(self.id)


class Game(BaseModel):
    id: int
    state: GameState = GameState.UNPLAYED
    players: List[Player] = []
    winner: Optional[Player] = None

    def __hash__(self):
        return hash(self.id)


def get_players() -> List[Player]:
    request: requests.Response = requests.get("http://127.0.0.1:8000/players")
    request_body = request.json()
    players: List[Player] = [Player.parse_obj(player) for player in request_body]
    return players


def get_games() -> List[Game]:
    request: requests.Response = requests.get("http://127.0.0.1:8000/games")
    request_body = request.json()
    games: List[Game] = [Game.parse_obj(game) for game in request_body]
    return games


def delete_players(player_ids: List[int]):
    request: requests.Response = requests.delete("http://127.0.0.1:8000/players", json=player_ids)
    return request.json()


def delete_games(game_ids: List[int]):
    request: requests.Response = requests.delete("http://127.0.0.1:8000/games", json=game_ids)
    return request.json()


class CreatePlayerDialog(QtWidgets.QDialog):
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

    def showEvent(self, *args, **kwargs):
        self.input_name.clear()
        self.input_elo.setText("0")
        super().showEvent(*args, **kwargs)

    @QtCore.Slot()
    def dialog_accepted(self):
        name = self.input_name.text()
        elo = int(self.input_elo.text())
        result: bool = self.create_player(name, elo)
        if result:
            self.close()

    @QtCore.Slot()
    def dialog_cancelled(self):
        self.close()

    def create_player(self, name: str, elo: int = 0) -> bool:
        if name == "":
            QtWidgets.QMessageBox.warning(self, "Error", "Name cannot be empty")
            return False

        requests.post("http://127.0.0.1:8000/player", json={"name": name, "elo": elo})
        return True


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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Window')
        self.resize(QtGui.QGuiApplication.primaryScreen().availableGeometry().size() * 0.7)

        self.selected_players_id: List[int] = []
        self.selected_games_id: List[int] = []

        self.main_splitter = QtWidgets.QSplitter(parent=self)
        self.create_player_dialog = CreatePlayerDialog(parent=self)
        self.player_list = FilteredListWidget()
        self.game_list = FilteredListWidget()
        self.log = QtWidgets.QTextBrowser(parent=self)

        self.create_player_button = QtWidgets.QPushButton("Create Player")
        self.create_player_button.clicked.connect(self.open_create_player_dialog)
        self.create_game_button = QtWidgets.QPushButton("Create Game")
        self.create_game_button.clicked.connect(self.open_create_player_dialog)

        self.player_list.selection_changed.connect(self.on_player_selection_changed)
        self.game_list.selection_changed.connect(self.on_game_selection_changed)

        self.setCentralWidget(self.create_ui())
        self.populate()
        self.restore_settings()

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def save_settings(self):
        settings = QtCore.QSettings("SAE", "APITestingTool")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("players_filter_text", self.player_list.filter_widget.text())
        settings.setValue("games_filter_text", self.game_list.filter_widget.text())
        settings.setValue("main_splitter", self.main_splitter.saveState())

    def restore_settings(self):
        settings = QtCore.QSettings("SAE", "APITestingTool")
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        if settings.contains("players_filter_text"):
            self.player_list.filter_widget.setText(settings.value("players_filter_text"))
        if settings.contains("games_filter_text"):
            self.game_list.filter_widget.setText(settings.value("games_filter_text"))
        if settings.contains("main_splitter"):
            self.main_splitter.restoreState(settings.value("main_splitter"))

    def create_ui(self) -> QtWidgets.QWidget:
        player_head_label = QtWidgets.QLabel("All players")
        player_list_layout = QtWidgets.QVBoxLayout()
        player_list_layout.addWidget(player_head_label)
        player_list_layout.addWidget(self.player_list)
        player_list_widget = QtWidgets.QWidget()
        player_list_widget.setLayout(player_list_layout)

        player_details_layout = QtWidgets.QVBoxLayout()
        player_details_layout.addWidget(QtWidgets.QLabel("Details come here"))
        player_details_widget = QtWidgets.QWidget()
        player_details_widget.setLayout(player_details_layout)

        player_browsing_splitter = QtWidgets.QSplitter()
        player_browsing_splitter.addWidget(player_list_widget)
        player_browsing_splitter.addWidget(player_details_widget)

        player_tab_layout = QtWidgets.QVBoxLayout()
        player_tab_layout.addWidget(player_browsing_splitter)
        player_tab_layout.addWidget(self.create_player_button)
        player_tab_widget = QtWidgets.QWidget(parent=self)
        player_tab_widget.setLayout(player_tab_layout)

        game_head_label = QtWidgets.QLabel("All games")
        game_list_layout = QtWidgets.QVBoxLayout()
        game_list_layout.addWidget(game_head_label)
        game_list_layout.addWidget(self.game_list)
        game_list_widget = QtWidgets.QWidget()
        game_list_widget.setLayout(game_list_layout)

        game_details_layout = QtWidgets.QVBoxLayout()
        game_details_layout.addWidget(QtWidgets.QLabel("Details come here"))
        game_details_widget = QtWidgets.QWidget()
        game_details_widget.setLayout(game_details_layout)

        game_browsing_splitter = QtWidgets.QSplitter()
        game_browsing_splitter.addWidget(game_list_widget)
        game_browsing_splitter.addWidget(game_details_widget)

        game_tab_layout = QtWidgets.QVBoxLayout()
        game_tab_layout.addWidget(game_browsing_splitter)
        game_tab_layout.addWidget(self.create_game_button)
        game_tab_widget = QtWidgets.QWidget(parent=self)
        game_tab_widget.setLayout(game_tab_layout)

        tab_widget = QtWidgets.QTabWidget(parent=self)
        tab_widget.addTab(player_tab_widget, "Players")
        tab_widget.addTab(game_tab_widget, "Games")

        self.main_splitter.addWidget(tab_widget)
        self.main_splitter.addWidget(self.log)
        self.main_splitter.setOrientation(QtCore.Qt.Vertical)
        return self.main_splitter

    def populate(self):
        self.update_players()

    @QtCore.Slot()
    def open_create_player_dialog(self):
        self.create_player_dialog.exec_()
        self.update_players()

    @QtCore.Slot(list)
    def on_player_selection_changed(self, selected_players: List[QtGui.QStandardItem]):
        self.selected_players_id = [selected_item.data(Role.ID_ROLE.value) for selected_item in selected_players]

    @QtCore.Slot(list)
    def on_game_selection_changed(self, selected_games: List[QtGui.QStandardItem]):
        self.selected_games_id = [selected_item.data(Role.ID_ROLE.value) for selected_item in selected_games]

    @QtCore.Slot(str)
    def log_message(self, message: Any):
        self.log.append(str(message))

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        is_player = self.player_list.view.hasFocus()
        key_combination = [event.key(), event.modifiers(), is_player]
        try:
            match key_combination:
                case [QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier, True]:
                    self.log_message(delete_players(self.selected_players_id))
                    self.update_players()
                case [QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier, False]:
                    self.log_message(delete_games(self.selected_games_id))
                    self.update_games()
                case [QtCore.Qt.Key_A, *_]:
                    print("Voila")
                case _:
                    # https://www.youtube.com/watch?v=ij0XZ3BbvlQ&t=3s
                    pass
        except Exception as e:
            self.log_message(e)

    def update_players(self):
        self.player_list.model.clear()
        for player in get_players():
            item = QtGui.QStandardItem()
            item.setData(player.name, QtCore.Qt.DisplayRole)
            item.setData(player, Role.WHOLE_DATA_ROLE.value)
            item.setData(player.id, Role.ID_ROLE.value)
            self.player_list.model.appendRow([item])

    def update_games(self):
        self.game_list.model.clear()
        for game in get_games():
            game: Game
            item = QtGui.QStandardItem()
            players = ", ".join([player.name for player in game.players])
            item.setData(f"{game.id} - Players: {players}", QtCore.Qt.DisplayRole)
            item.setData(game, Role.WHOLE_DATA_ROLE.value)
            item.setData(game.id, Role.ID_ROLE.value)
            self.player_list.model.appendRow([item])


def main():
    app = QtWidgets.QApplication()
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
