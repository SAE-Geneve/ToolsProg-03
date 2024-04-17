import requests
from PySide2 import QtCore
from typing import List, Optional, Any
from models import Player, Game
from globals import GameState


class AccessApi(QtCore.QObject):
    def __init__(self, host="http://127.0.0.1:8000", parent=None):
        super().__init__(parent=parent)
        self.host = host

    def to_host(self, path: str) -> str:
        if not path.startswith("/") and not self.host.endswith("/"):
            path = "/" + path
        return f"{self.host}{path}"

    def get_players(self) -> List[Player]:
        request: requests.Response = requests.get(self.to_host("/players"))
        request_body = request.json()
        players: List[Player] = [Player.parse_obj(player) for player in request_body]
        return players

    def get_games(self) -> List[Game]:
        request: requests.Response = requests.get(self.to_host("/games"))
        request_body = request.json()
        games: List[Game] = [Game.parse_obj(game) for game in request_body]
        return games

    @QtCore.Slot(dict)
    def create_player(self, new_player: dict) -> Player:
        request: requests.Response = requests.post(self.to_host("/player"), json=new_player)
        return Player.parse_obj(request.json())

    @QtCore.Slot(dict)
    def create_game(self, new_game: dict) -> Game:
        request: requests.Response = requests.post(self.to_host("/game"), json=new_game)
        return Game.parse_obj(request.json())

    @QtCore.Slot(list)
    def delete_players(self, player_ids: List[int]):
        request: requests.Response = requests.delete(self.to_host("/players"), json=player_ids)
        return request.json()

    @QtCore.Slot(list)
    def delete_games(self, game_ids: List[int]):
        request: requests.Response = requests.delete(self.to_host("/games"), json=game_ids)
        return request.json()
