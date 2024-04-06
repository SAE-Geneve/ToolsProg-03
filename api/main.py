from fastapi import FastAPI, Request, HTTPException, status
from peewee import Query, JOIN
from playhouse.shortcuts import model_to_dict

from globals import GameState
from db_models import db, Player, Game, PlayerGame
from http_models import Player as HTTPPlayer, Game as HTTPGame


app = FastAPI()
with db:
    db.create_tables([Player, Game, PlayerGame])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    db.connect()
    response = await call_next(request)
    db.close()
    return response


@app.get("/players")
async def get_players(request: Request):
    players_query: Query = Player.select()
    return players_query.dicts()


@app.get("/games")
async def get_players(request: Request):
    games_query: Query = Game.select()
    return games_query.dicts()


@app.post("/player")
async def create_player(player: HTTPPlayer):
    if not player.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A new player should have a name!")
    created_player: Player = Player.create(name=player.name, elo=player.elo)
    return model_to_dict(created_player)


@app.post("/game")
async def create_game(game: HTTPGame):
    created_game: Game = Game.create(state=game.state)
    return model_to_dict(created_game)


@app.get("/")
async def root():
    for player in Player.select():
        print(player.name)

    query = Player.select().where(Player.elo > 500)
    for player in query:
        print(player.name, player.elo)

    query = (Player.select(Player.name)
             .join(PlayerGame, JOIN.LEFT_OUTER)
             .join(Game, JOIN.LEFT_OUTER)
             .where(Game.state == GameState.ABORTED.value)
             .group_by(Player.name)
             )
    for player in query:
        print(player.name)

    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
