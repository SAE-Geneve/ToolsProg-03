from behave import *
from main import MainWindow
from PySide2 import QtWidgets, QtGui, QtCore
from typing import List
from access_api import AccessApi

use_step_matcher("re")


@given("the db is empty")
def step_impl(context):
    pass


@when("the app is opened")
def step_impl(context):
    window = MainWindow()
    context.window = window


@then("the list appears empty")
def step_impl(context):
    window: MainWindow = context.window
    assert window.player_list.model.rowCount() == 0


@given("the db is not empty")
def step_impl(context):
    context.name_list: List[str] = ["Pedro", "Juan", "Carlos"]

    for name in context.name_list:
        context.access_api.create_player({"name": name, "elo": 300})


@then("the list shows player names")
def step_impl(context):
    window: MainWindow = context.window
    player_nbr = window.player_list.model.rowCount()
    players: List[QtGui.QStandardItem] = [window.player_list.model.item(i, 0) for i in range(player_nbr)]
    names: List[str] = [item.data(QtCore.Qt.DisplayRole) for item in players]
    for i, name in enumerate(context.name_list):
        assert name == names[i]
