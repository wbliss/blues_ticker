from helpers import get_current_date_time, convert_to_24hour, add_minutes
import requests
import json


def main():
    game_uploaded = True
    game_date_time = "2017-12-13.02:00AM"
    update_date_time = add_minutes(25, game_date_time)
    update_date = update_date_time.split('.')[0]
    update_time = convert_to_24hour(update_date_time.split('.')[1])
    game_id = "2017020471"
    print(update_date_time)
    while game_uploaded:
        date_time = get_current_date_time()
        current_time = convert_to_24hour(date_time.split('.')[1])
        current_date = date_time.split('.')[0]

        if current_time > update_time and current_date == update_date:
            url = 'https://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)
            game_log = requests.get(url).json()   

            with open('data/' + game_id + '.json', "w") as outfile:
                json.dump(game_log, outfile) 
            
            print("Game successfully updated")
            game_uploaded = False

main()