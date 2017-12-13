import json
import requests

from models import db, Game
from config import fav_team_id, local_tz
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

def add_minutes(delay, date_time):
    """adds x minutes to current time for update"""
    update_time = (datetime.strptime(date_time,'%Y-%m-%d.%H%M') + timedelta(minutes=delay)).strftime('%Y-%m-%d.%H%M')
    return update_time

def get_live_updates(game):
    """returns gameinfo split on '.' (0 = GameID, 1 = GameTime 2 = AwayTeam 3 = HomeTeam 4 = AwayScore 5 = HomeScore 6 = GameStatus')"""
    game_url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game.game_id)
    game_log = requests.get(game_url).json()
    game_status = game_log.get('gameData').get('status').get('abstractGameState')
    
    if game_status == 'Final':
        complete_game(game.game_id, game)
        return game_status

    if game_status == 'Preview':
        return game_status

    if game_status == 'Live':
        game_details = {}
        linescore = game_log.get('liveData').get('linescore')
        game_details['game_time'] = linescore.get('currentPeriodTimeRemaining')
        game_details['period'] = linescore.get('currentPeriodOrdinal')
        game_details['away_score'] = linescore.get('teams').get('away').get('goals')
        game_details['home_score'] = linescore.get('teams').get('home').get('goals')
        game_details['away_shots'] = linescore.get('teams').get('away').get('shotsOnGoal')
        game_details['home_shots'] = linescore.get('teams').get('home').get('shotsOnGoal')

        return game_details

def get_up_to_date():
    not_up_to_date = True
    next_game_url = 'https://statsapi.web.nhl.com/api/v1/teams/{}?expand=team.schedule.next'.format(fav_team_id)
    api_next_game = requests.get(next_game_url).json()
    api_next_game_id = str(api_next_game.get('teams')[0].get('nextGameSchedule').get('dates')[0].get('games')[0].get('gamePk'))
    while not_up_to_date:
        db_next_game = Game.query.filter_by(next_game=True).first()
        if db_next_game.game_id != api_next_game_id:
            complete_game(db_next_game.game_id, db_next_game, mass_import=True)
        else:
            db.session.commit()
            not_up_to_date = False
            return 'Games are up-to-date!'

def main():
    return None

if __name__ == '__main__':
    main()