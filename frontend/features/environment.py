from PySide2 import QtWidgets
from access_api import AccessApi


def before_all(context):
    context.app = QtWidgets.QApplication()
    context.access_api = AccessApi()


def before_scenario(context, scenario):
    api: AccessApi = context.access_api

    players = api.get_players()
    ids = [player.id for player in players]

    api.delete_players(ids)
