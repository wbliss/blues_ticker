import json
import requests

from models import db, Game
from config import fav_team, local_tz
from datetime import datetime, timedelta
from pytz import timezone

#IF GAME IS ONGOING - PULL FROM API
#IF NO GAME - PULL FROM DB and JSON

def complete_game(game_id, game=None, mass_import=False):
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
            if mass_import:
                return "Game completed!"
            else:
                db.session.commit()
                return "Game completed!"
        
        else:
            return "Game is not complete"
    
    else:
        return "Game not found"
        
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

def main():
    return None

if __name__ == '__main__':
    main()