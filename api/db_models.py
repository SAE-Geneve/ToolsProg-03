from os import environ

from dotenv import load_dotenv

from globals import GameState, GameResult
from peewee import PostgresqlDatabase, Model, CharField, IntegerField, ForeignKeyField


load_dotenv()
db = PostgresqlDatabase(environ.get("DB_NAME"), user=environ.get("DB_USER"), password=environ.get("DB_PASS"), host=environ.get("DB_HOST", "localhost"))


class BaseModel(Model):
    class Meta:
        database = db


class Player(BaseModel):
    name = CharField(unique=True)
    elo = IntegerField(default=0)


class Game(BaseModel):
    state = IntegerField(default=GameState.UNPLAYED.value)


class PlayerGame(BaseModel):
    player = ForeignKeyField(Player, backref="games")
    game = ForeignKeyField(Game, backref="players")
    result = IntegerField(default=GameResult.UNPLAYED.value)

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('player', 'game'), True),
        )

