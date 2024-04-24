from behave import *
from PySide2 import QtGui

from main import MainWindow
from access_api import AccessApi
from models import Player

use_step_matcher("re")


@given("there are players in the database")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    api: AccessApi = context.api
    player = {"name": "test", "elo": 0}
    # This will create an error if the player already exists
    # Solution1: change the feature to give a valid state
    # Solution2: try / except block to prevent editing the db since there's already something in there
    # Solution3: clean the db before every scenario
    created_player = api.create_player(player)
    assert created_player.name == player["name"]
    assert created_player.elo == player["elo"]
    context.created_player = created_player


@when("the tool is opened")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    main_window = MainWindow()
    context.main_window = main_window


@then("player list is not empty")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    main_window: MainWindow = context.main_window
    model: QtGui.QStandardItemModel = main_window.player_list.model
    item: QtGui.QStandardItem = model.item(0, 0)
    assert item is not None
