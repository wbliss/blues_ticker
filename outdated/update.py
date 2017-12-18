import queue

from app import app
from helpers import (add_minutes, convert_to_24hour, get_current_date_time,
                     get_live_updates, get_up_to_date)
from models import Game, db

stats_queue = queue.LifoQueue()

def update():
    update = True
    get_up_to_date()

    while update:
        game = Game.query.filter_by(next_game=True).first()
        have_next_game = True
        print(game.time)
        update_info = game.date + "." + str(convert_to_24hour(game.time))
        update_date = update_info.split('.')[0]
        update_time = int(update_info.split('.')[1])
        print(update_info)
        while have_next_game:
            current_date_time = get_current_date_time()
            current_date = current_date_time.split('.')[0]
            current_time = convert_to_24hour(current_date_time.split('.')[1])
            if current_time > update_time and current_date == update_date:
                game_status = get_live_updates(game)
                if game_status == 'Final':
                    stats_queue.queue.clear()
                    have_next_game = False
                elif game_status == 'Preview':
                    update_info = add_minutes(10, current_date + '.0' +str(current_time))
                    update_date = update_info.split('.')[0]
                    update_time = int(update_info.split('.')[1])
                    stats_queue.put(game_status)
                    print("Game hasn't started. Time: " + str(update_time))
                else:
                    #send game status to controller
                    stats_queue.queue.clear()
                    stats_queue.put(game_status)
                    update_info = add_minutes(1, current_date + '.0' + str(current_time))
                    update_date = update_info.split('.')[0]
                    update_time = int(update_info.split('.')[1])
                    print(game_status)

def main():
    update()

if __name__ == '__main__':
    main()
