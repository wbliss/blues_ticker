import json
import os

import requests

from config import fav_team, local_tz
from helpers import complete_game, convert_datetime
from models import Game, db


def import_games():
    """Imports all games of favorite team as a json to the data directory"""
    all_games_url = ('https://statsapi.web.nhl.com/api/v1/schedule?startDate=2017-10-04&endDate=2018-04-07&expand=schedule.teams')
    blues_games = []
    data = requests.get(all_games_url).json()
    data = data.pop('dates')
    if not os.path.isdir('data'):
        os.mkdir('data')
    for date in data:
        games = date.pop('games')
        for game in games:
            teams = game.get('teams')
            away_team = teams.get('away').get('team').get('name')
            home_team = teams.get('home').get('team').get('name')

            if home_team == fav_team or away_team == fav_team:
                blues_games.append(game)
                break

    with open('data/blues_games.json', "w") as outfile:
        json.dump(blues_games, outfile)

def create_db():
    """creates the mysql database"""
    with open('data/blues_games.json', 'r') as games:
        all_games = json.load(games)
    
    for game in all_games:
        game_id = str(game.get('gamePk'))
        game_date = game.get('gameDate')[0:10]
        game_time = game.get('gameDate')[11:16]
        date_time = convert_datetime(game_date, game_time, local_tz)
        game_date = date_time.split('.')[0]
        game_time = date_time.split('.')[1]
        away_team = game.get('teams').get('away').get('team').get('name')
        home_team = game.get('teams').get('home').get('team').get('name')
        new_game = Game(game_id, game_date, game_time, away_team, home_team)
        db.session.add(new_game)
    
    for game in all_games:
        game_id = str(game.get('gamePk'))
        complete_game(game_id, mass_import=True)

    db.session.commit()

def main():
    db.create_all()
    import_games()
    create_db()

if __name__ == '__main__':
    main()
