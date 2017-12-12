import requests
import json
import os
from models import Game, db


url = 'https://statsapi.web.nhl.com/api/v1/game/2017020202/feed/live'
def import_games():
    all_games_url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate=2017-10-04&endDate=2018-04-07&expand=schedule.teams'
    blues_games = []
    r = requests.get(all_games_url)
    data = r.json()
    dates = data.pop('dates')
    if not os.path.isdir('results'):
        os.mkdir('results')
    for dates_index, date in enumerate(dates):
        games = date.pop('games')
        for games_index, game in enumerate(games):
            teams = game.get('teams')
            away = teams.get('away')
            home = teams.get('home')
            away_team = away.get('team')
            home_team = home.get('team')
            away_team = away_team.get('name')
            home_team = home_team.get('name')
            if home_team == "St. Louis Blues" or away_team == "St. Louis Blues":
                blues_games.append(game)

    with open('results/blues_games.json', "w") as outfile:
        json.dump(blues_games, outfile)

def complete_game(game_id, game=None):
    game_url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)
    print(game_url)
    game_log = requests.get(game_url).json()
    game_status = game_log.get('gameData').get('status').get('abstractGameState')
    print(game_status)
    if game is None:
        game = Game.query.filter_by(game_id=game_id).first()
    if str(game_log.get('gamePk')) == game_id:
        if game_status == 'Final':
            linescore = game_log.get('liveData').get('linescore')
            print(linescore)
            teams = linescore.get('teams')
            away_score = teams.get('away').get('goals')
            print(away_score)
            home_score = teams.get('home').get('goals')
            print(home_score)
            if linescore.get('currentPeriodOrdinal') == '3rd':
                game_status = ""
            else:
                game_status = "/" + linescore.get('currentPeriodOrdinal')
            game.complete_game(away_score, home_score, game_status)
            return "Game updated!"
        else:
            return "Game is not complete"
    else:
        return "Game not found"
            

def create_db():
    with open('results/blues_games.json', 'r') as games:
        all_games = json.load(games)
    for game in all_games:
        game_id = str(game.get('gamePk'))
        date = game.get('gameDate')[0:10]
        time = game.get('gameDate')[12:19]
        away_team = game.get('teams').get('away').get('team').get('name')
        home_team = game.get('teams').get('home').get('team').get('name')
        new_game = Game(game_id, date, time, away_team, home_team)
        complete_game(game_id, new_game)
        db.session.add(new_game)
        
    db.session.commit()

create_db()


            

            
