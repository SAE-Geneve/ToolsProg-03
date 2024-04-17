from typing import Optional, List, Tuple

from fastapi import FastAPI, Request, HTTPException, status
from peewee import Query, JOIN
from playhouse.shortcuts import model_to_dict

from globals import GameState, GameResult
from db_models import db, Player, Game, PlayerGame
from http_models import NewPlayer, ExistingPlayer, Game as HTTPGame


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
    return list(players_query.dicts())


@app.get("/games")
async def get_games(request: Request):
    games_query: Query = Game.select()
    return list(games_query.dicts())


@app.post("/player")
async def create_player(player: NewPlayer):
    if player.name is None or player.name == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A new player should have a name!")
    created_player: Player = Player.create(name=player.name, elo=player.elo)
    return model_to_dict(created_player)


@app.delete("/players")
async def delete_players(player_ids: List[int]):
    Player.delete().where(Player.id.in_(player_ids)).execute()
    return {"Deleted players": player_ids}


@app.delete("/games")
async def delete_games(game_ids: List[int]):
    Game.delete().where(Game.id.in_(game_ids)).execute()
    return {"Deleted games": game_ids}


def check_game_consistency(game: HTTPGame) -> None:
    code400 = status.HTTP_400_BAD_REQUEST
    if game.id is not None:
        raise HTTPException(status_code=code400, detail="A new game should not already have an id!")
    if len(game.players) == 0:
        raise HTTPException(status_code=code400, detail="A game should have at least one player!")
    if game.state not in GameState:
        game_states = {i.name: i.value for i in GameState}
        raise HTTPException(status_code=code400, detail=f"Unknown game state! The game state must be one of the following: {game_states}")
    if game.state in [GameState.PLAYING, GameState.FINISHED] and len(game.players) != 2:
        raise HTTPException(status_code=code400, detail="A game that is playing or has been played must have exactly two players!")
    if game.state == GameState.FINISHED and game.winner is None:
        raise HTTPException(status_code=code400, detail=f"A finished game should have exactly one winner!")
    if game.winner is not None and game.winner not in game.players:
        raise HTTPException(status_code=code400, detail="The winner of a game must the one who played it!")


def check_player_existence(game: HTTPGame) -> Tuple[Optional[Player], List[Optional[Player]]]:
    db_winner: Optional[Player] = None
    players_in_game_ids: List[int] = [player.id for player in game.players]
    db_players: List[Optional[Player]] = Player.select().where(Player.id.in_(players_in_game_ids)).execute()
    if None in db_players or len(db_players) != len(game.players):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested player(s) do not exist!")
    if game.winner is not None:
        db_winner = Player.select().where(Player.id == game.winner.id).get()
        if db_winner is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested winner does not exist!")
        if db_winner not in db_players:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The winner of a game must the one who played it!")
    return db_winner, db_players


def create_game_linked(game: HTTPGame, db_players: List[Player], db_winner: Optional[Player]) -> Game:
    with db.atomic() as transaction:
        created_game: Game = Game.create(state=game.state)
        for db_player in db_players:
            result_state: GameResult = GameResult.UNPLAYED
            is_winner = db_winner is not None and db_player.id == db_winner.id
            winner_game_state = [game.state, is_winner]
            match winner_game_state:
                case [GameState.UNPLAYED, *_]:
                    result_state = GameResult.UNPLAYED
                case [GameState.PLAYING, *_]:
                    result_state = GameResult.PLAYING
                case [GameState.ABORTED, *_]:
                    result_state = GameResult.ABORTED
                case [GameState.FINISHED, True]:
                    result_state = GameResult.WON
                case [GameState.FINISHED, False]:
                    result_state = GameResult.LOST
                case _:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid game and winner state!")
            PlayerGame.create(player=db_player, game=created_game, result=result_state.value)

    return created_game


@app.post("/game")
async def create_game(game: HTTPGame):
    # Checking data consistency
    check_game_consistency(game)

    # Checking data existence in the database
    db_winner, db_players = check_player_existence(game)

    # Creating the game and linking the player(s) accordingly
    return model_to_dict(create_game_linked(game, db_players, db_winner))


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
