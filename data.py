from ohmysportsfeedspy import MySportsFeeds
from config import username, password, team
from datetime import datetime, timedelta, date
from pytz import timezone
import json

def import_all():
    msf = MySportsFeeds(version='1.0')
    msf.authenticate(username, password)

    output = msf.msf_get_data(league='nhl', season='current', feed='full_game_schedule', team=team, format='json')
    output = msf.msf_get_data(league='nhl', season='current', feed='team_gamelogs', team=team, format='json')

def import_game(date):
    msf = MySportsFeeds(version='1.0')
    msf.authenticate(username, password)
    output = msf.msf_get_data(league='nhl', season='current', feed='scoreboard', fordate=date, team=team, format='json')

def is_game_today(date):
    """imports game for the selected date (YYYYMMDD)"""

    with open('results/full_game_schedule-nhl-current.json', 'r') as games:
        all_games = json.load(games)
    
    game_dates = []
    all_games = all_games.pop('fullgameschedule') # creates dict
    all_games = all_games.pop('gameentry') # creates list
    for index, game in enumerate(all_games):
        game_date = game.get('date')
        game_date = game_date.replace("-","")
        game_dates.append(game_date)

    if date in game_dates:
        return True
    else:
        return False

def import_todays_game():
    today = get_current_date_time()
    today_date = today.split('.')[0]
    return import_game(today_date)

def get_current_date_time():
    """returns current eastern date time as string in format 'YYYYMMDD.HHMM'"""
    tz = timezone('EST')
    today = datetime.now(tz).strftime("%Y%m%d.%H%M")
    return today

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

def get_update_time(today_datetime):
    
    today_date = today_datetime.split('.')[0]
    with open('results/scoreboard-nhl-current-' + today_date + '.json', 'r') as today_game:
            game = json.load(today_game)
    
    game = game.pop('scoreboard') #dict
    game = game.pop('gameScore') #list
    game = game[0]
    game = game.pop('game')

    game_time = game.get('time')
    update_time = (convert_to_24hour(game_time) + 300) % 2400

    if update_time < 300:
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y%m%d")
        update_datetime = tomorrow + '.' + str(update_time)
    else:
        update_datetime = today_date + '.' + str(update_time)

    return update_datetime

if __name__ == "__main__":
    convert_to_24hour('8:00PM')