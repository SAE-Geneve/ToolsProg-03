from typing import List

from behave import fixture, use_fixture
from PySide2 import QtWidgets

from access_api import AccessApi
from models import Player


def before_all(context):
    app = QtWidgets.QApplication()
    context.app = app

    access_api = AccessApi(host="http://127.0.0.1:8000")
    context.api = access_api


def before_scenario(context, scenario):
    all_players: List[Player] = context.api.get_players()
    player_ids = [player.id for player in all_players]
    context.api.delete_players(player_ids)
