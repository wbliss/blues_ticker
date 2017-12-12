import requests
import json
import os
from models import Game, db
from config import fav_team, local_tz
from datetime import date, datetime, timedelta
from pytz import timezone

#IF GAME IS ONGOING - PULL FROM API
#IF NO GAME - PULL FROM DB and JSON

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
            if home_team == fav_team or away_team == fav_team:
                blues_games.append(game)

    with open('results/blues_games.json', "w") as outfile:
        json.dump(blues_games, outfile)

def complete_game(game_id, game=None):
    game_url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)
    game_log = requests.get(game_url).json()
    game_status = game_log.get('gameData').get('status').get('abstractGameState')
    
    if game is None:
        game = Game.query.filter_by(game_id=game_id).first()
    
    if "Final" in game.game_status:
        return "Game already completed"
    
    if str(game_log.get('gamePk')) == game_id:
        
        if game_status == 'Final':
            linescore = game_log.get('liveData').get('linescore')
            teams = linescore.get('teams')
            away_score = teams.get('away').get('goals')
            home_score = teams.get('home').get('goals')
            
            if linescore.get('currentPeriodOrdinal') == '3rd':
                game_status = ""
            
            else:
                game_status = "/" + linescore.get('currentPeriodOrdinal')
            
            game.complete_game(away_score, home_score, game_status)
            return "Game completed!"
        
        else:
            return "Game is not complete"
    
    else:
        return "Game not found"
            
def create_db():
    with open('results/blues_games.json', 'r') as games:
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
        complete_game(game_id)

    db.session.commit()

def convert_datetime(date, time, tz):
    date_time = datetime.strptime(date + '.' + time, '%Y-%m-%d.%H:%M')
    old_timezone = timezone('UTC')
    new_timezone = timezone(tz)

    return old_timezone.localize(date_time).astimezone(new_timezone).strftime("%Y-%m-%d.%I:%M%p")

def convert_to_24hour(time):
    """returns time as a 24-hour clock integer"""
    time = time.replace(":", "")
    if "PM" in time and "12" not in time:
        time = int(time[0:-2]) + 1200
        return time
    elif "AM" in time and "12" in time:
        time = time.replace("12", "00")
        return int(time[0:-2])
    else:
        return int(time[0:-2])

def get_current_date_time():
    """returns current date and time as string in format 'YYYY-MM-DD.HHMM'"""
    tz = timezone(local_tz)
    today = datetime.now(tz).strftime("%Y-%m-%d.%I:%M%p")
    return today

def add_minutes(delay):
    """adds x minutes to current time for update"""
    tz = timezone(local_tz)
    update_time = (datetime.now(tz) + timedelta(minutes=delay)).strftime('%Y-%m-%d.%I:%M%p')
    return update_time

def get_live_updates(game):
    """returns gameinfo split on '.' (0 = GameID, 1 = GameTime 2 = AwayTeam 3 = HomeTeam 4 = AwayScore 5 = HomeScore 6 = GameStatus')"""
    game_url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game.game_id)
    game_log = requests.get(game_url).json()
    game_status = game_log.get('gameData').get('status').get('abstractGameState')
    
    if game_status == 'Final':
        complete_game(game.game_id, game)
        return False

    if game_status == 'Preview':
        return False

    #TODO - Will get and return(will need to look at json of ongoing game to study):
    #   Period
    #   Score
    #   Shots
    #   Time 

""" RUN FUNCTION WILL WILL:
    Run on while loop
    Continously check date and time
    If date and time matches that of a game, aka time for a game (24 hour convert) then update every x
        minues to pull stats
    Otherwise, chill, and display prev/next game depending on other criteria 
"""