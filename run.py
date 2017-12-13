from helpers import *
from config import fav_team_id
from models import db, Game
import json
import requests

""" RUN FUNCTION WILL WILL:
    Run on while loop
    Continously check date and time
    If date and time matches that of a game, aka time for a game (24 hour convert) then update every x
        minues to pull stats
    Otherwise, chill, and display prev/next game depending on other criteria
"""
def run():
    run = True
    get_up_to_date()
    while run:
        game = Game.query.filter_by(next_game=True).first()
        have_next_game = True
        update_info = add_minutes(0, game.date + '.' + str(convert_to_24hour(game.time)))
        update_date = update_info.split('.')[0]
        update_time = int(update_info.split('.')[1])
        while have_next_game:
            current_date_time = get_current_date_time()
            current_date = current_date_time.split('.')[0]
            current_time = convert_to_24hour(current_date_time.split('.')[1])
            if current_time > update_time and current_date == update_date:
                game_status = get_live_updates(game)
                if game_status == 'Final':
                    have_next_game = False
                elif game_status == 'Preview':
                    update_info = add_minutes(10, current_date + '.' + str(current_time))
                    update_date = update_info.split('.')[0]
                    update_time = int(update_info.split('.')[1])
                else:
                    #send game status to handler
                    update_info = add_minutes(1, current_date + '.' + str(current_time))
                    update_date = update_info.split('.')[0]
                    update_time = int(update_info.split('.')[1])






def main():
    run()

if __name__ == '__main__':
    main()