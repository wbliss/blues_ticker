import json
from datetime import date, datetime, timedelta

from pytz import timezone

from config import fav_team, password, username
from models import Game, db
from ohmysportsfeedspy import MySportsFeeds


def setup_import():
    
    msf = MySportsFeeds(version='1.0')
    msf.authenticate(username, password)
    try:
        output = msf.msf_get_data(league='nhl', season='current', feed='full_game_schedule', team=fav_team, format='json')
        output = msf.msf_get_data(league='nhl', season='current', feed='team_gamelogs', team=fav_team, format='json')
        print("Import succesful")
        return True
    except Warning or FileNotFoundError:
        print("Import failed")
        return False

def import_game(import_date):
    """imports game for the selected date (YYYYMMDD)"""
    
    msf = MySportsFeeds(version='1.0')
    msf.authenticate(username, password)
    try:
        output = msf.msf_get_data(league='nhl', season='current', feed='scoreboard', fordate=import_date, team=fav_team, format='json')
        return True
    except Warning:
        print("Import failed")
        return False

def import_todays_game():
    """imports the game for today's date"""
    today = get_current_date_time()
    today_date = today.split('.')[0]
    return import_game(today_date)

def is_game_today(today_date):
    """checks if there is a game today"""
    with open('results/full_game_schedule-nhl-current.json', 'r') as games:
        all_games = json.load(games)
    
    game_dates = []
    all_games = all_games.pop('fullgameschedule') # creates dict
    all_games = all_games.pop('gameentry') # creates list
    for index, game in enumerate(all_games):
        game_date = game.get('date')
        game_date = game_date.replace("-","")
        game_dates.append(game_date)

    if today_date in game_dates:
        return True
    else:
        return False

def is_game_completed(game_date):
    """checks if game is marked as completed"""
    with open('results/scoreboard-nhl-current-' + game_date + '.json', 'r') as g:
        game = json.load(g)

    game = game.pop('scoreboard') #dict
    game = game.pop('gameScore') #list
    game = game[0]
    game = game.pop('game')

    if game.get("isCompleted") == "true":
        return True
    else:
        return False

def get_current_date_time():
    """returns current UTC date time as string in format 'YYYYMMDD.HHMM'"""
    tz = timezone('UTC')
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

def add_30_minutes():
    """adds 30 minutes to current time EST"""
    tz = timezone('EST')
    update_time = (datetime.now(tz) + timedelta(minutes=5)).strftime('%I:%M%p')
    update_time = convert_to_24hour(update_time)
    return update_time

def get_update_time(today_datetime):
    """returns time to check for update"""
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

def get_game_info(game_date):
    """returns gameinfo split on '.' (0 = GameID, 1 = GameTime 2 = AwayTeam 3 = HomeTeam 4 = AwayScore 5 = HomeScore 6 = GameStatus')"""

    with open('results/scoreboard-nhl-current-' + game_date + '.json', 'r') as g:
        game = json.load(g)

    game = game.pop('scoreboard') #dict
    game = game.pop('gameScore')
    game = game[0]
    game_info = game.pop('game')
    home_team = game_info.pop('homeTeam').get('Abbreviation')
    away_team = game_info.pop('awayTeam').get('Abbreviation')

    game_status = game.pop('periodSummary')
    game_status = game_status[-1]
    if game_status['@number'] == "5":
        game_status = "/SO"
    elif game_status['@number'] == "4":
        game_status = "/OT"
    else:
        game_status = ""

    if game.get('isCompleted') == "true":
        return (game_info.get("ID") + "." + game_info.get("time") + "."
            + away_team + "." + home_team
            + "." + game.get('awayScore') + "." + game.get('homeScore') + "." + game_status)
    else:
        return (game_info.get("ID") + "." + game_info.get("time") + "." + away_team + "." + home_team)

def complete_game(game_date):
    """complete game for the given date"""
    game_id = get_game_info(game_date).split('.')[0]
    away_goals = get_game_info(game_date).split('.')[4]
    home_goals = get_game_info(game_date).split('.')[5]
    game_status = get_game_info(game_date).split('.')[6]
    game = Game.query.filter_by(game_id=game_id)
    game.complete_game(away_goals, home_goals, game_status)
    db.session.add(game)
    db.session.commit()

def check_for_update():
    """continually checks and updates when update is available"""
    is_running = True #keeps app running
    last_import_attempted = get_current_date_time().split('.')[0] #initialized import attempted date
    print("last import attempted: " + last_import_attempted)
    update_date = ""
    update_time = "2401" #impossible for generate current_time to be higher, therefor will not trigger update
    game_date = ""
    game_not_imported_today = None

    if is_game_today(last_import_attempted): #if there is a game today, import
        if import_todays_game():
            game_not_imported_today = False
            print("Game imported successfully")
            update_datetime = get_update_time(last_import_attempted) #gets the time to update the score
            update_date = update_datetime.split('.')[0]
            update_time = update_datetime.split('.')[1]
        else:
            game_not_imported_today = True
            print("Game not imported")
            game_update_time = add_30_minutes()
            print(game_update_time)
        
        
    while is_running:
        current_datetime = get_current_date_time() #gets current datetime
        current_date = current_datetime.split('.')[0] 
        current_time = current_datetime.split('.')[1]

        if ((current_date != last_import_attempted and game_date == "") 
            or (current_date == last_import_attempted and game_not_imported_today 
            and int(current_time) > int(game_update_time))): #if it is a new day and a game hasn't been imported

            if is_game_today(current_date): #attempts to import the game for that given day, if there is it imports and returns true, otherwise returns false and does nothing
                if import_todays_game():
                    game_not_imported_today = False
                    print("Game imported successfully")
                    update_datetime = get_update_time(last_import_attempted) #gets the time to update the score
                    update_date = update_datetime.split('.')[0]
                    update_time = update_datetime.split('.')[1]

                else:
                    game_not_imported_today = True
                    print("Game not imported")
                    game_update_time = add_30_minutes()
                    print(game_update_time)
                    #last_import_attempted = current_date #since game was imported, makes sure that it is not imported again
                    #print("Game imported successfully" + current_time)

            else:
                last_import_attempted = current_date #if there is no game for given day, changes imported date

        elif current_date == update_date and int(current_time) > int(update_time): #if update conditions are met
            print(current_time + "attempting update")
            import_game(game_date)
            if is_game_completed(game_date): #complete the game
                complete_game(game_date)
                print("update complete!" + current_time)
                is_running = False
            else:
                update_time = add_30_minutes()

    return Game.query.filter_by(game_id=get_game_info(game_date).split('.')[0])


#TODO - consolidate some of these fucking functions. Make 1 getter per game........
#TODO - Look up Quartz Scheduler 
#TODO - Events



if __name__ == "__main__":
    check_for_update()