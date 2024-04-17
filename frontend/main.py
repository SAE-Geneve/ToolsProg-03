from PySide2 import QtCore, QtGui, QtWidgets
from typing import List, Optional, Any
from models import Player, Game
from globals import Role
from access_api import AccessApi
from filtered_list import FilteredListWidget
from asset_creation import CreatePlayerDialog, CreateGameDialog



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('API Testing tool')

        self.api = AccessApi(host="http://127.0.0.1:8000")

        self.selected_players_id: List[int] = []
        self.selected_games_id: List[int] = []

        self.player_list = FilteredListWidget()
        self.game_list = FilteredListWidget()
        self.main_splitter = QtWidgets.QSplitter(parent=self)
        self.log = QtWidgets.QTextBrowser(parent=self)

        self.create_player_button = QtWidgets.QPushButton("Create Player")
        self.create_player_button.clicked.connect(self.open_create_player_dialog)
        self.create_game_button = QtWidgets.QPushButton("Create Game")
        self.create_game_button.clicked.connect(self.open_create_game_dialog)

        self.player_list.selection_changed.connect(self.on_player_selection_changed)
        self.game_list.selection_changed.connect(self.on_game_selection_changed)

        self.create_player_dialog = CreatePlayerDialog(parent=self)
        self.create_player_dialog.new_player.connect(self.api.create_player)
        self.create_game_dialog = CreateGameDialog(players_model=self.player_list.model, parent=self)
        self.create_game_dialog.new_game.connect(self.api.create_game)

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
        self.update_games()

    @QtCore.Slot()
    def open_create_player_dialog(self):
        self.create_player_dialog.exec_()
        self.update_players()

    @QtCore.Slot()
    def open_create_game_dialog(self):
        self.create_game_dialog.exec_()
        self.update_games()

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
                    self.log_message(self.api.delete_players(self.selected_players_id))
                    self.update_players()
                case [QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier, False]:
                    self.log_message(self.api.delete_games(self.selected_games_id))
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
        for player in self.api.get_players():
            item = QtGui.QStandardItem()
            item.setData(player.name, QtCore.Qt.DisplayRole)
            item.setData(player, Role.WHOLE_DATA_ROLE.value)
            item.setData(player.id, Role.ID_ROLE.value)
            self.player_list.model.appendRow([item])

    def update_games(self):
        self.game_list.model.clear()
        for game in self.api.get_games():
            game: Game
            item = QtGui.QStandardItem()
            item.setData(game.id, QtCore.Qt.DisplayRole)
            item.setData(game, Role.WHOLE_DATA_ROLE.value)
            item.setData(game.id, Role.ID_ROLE.value)
            self.game_list.model.appendRow([item])


def main():
    app = QtWidgets.QApplication()
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
