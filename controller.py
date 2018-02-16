import queue

from flask import flash, redirect, render_template, request, session

from app import app
from models import Game, db
from helpers import get_current_date_time, convert_to_24hour, get_live_updates, get_up_to_date, complete_game


@app.route('/')
def index():
    get_up_to_date()
    return redirect('/ticker')
    
@app.route('/ticker')
def display_ticker():
    current_date_time = get_current_date_time()
    next_game = Game.query.filter_by(next_game=True).first()
    prev_game = Game.query.filter_by(most_recent=True).first()

    #Displays the last game played if date is the same as the game was played
    if current_date_time.split('.')[0] == prev_game.date:
        return render_template('most-recent.html', game=prev_game, game_status="GAME COMPLETED")

    #Displays game if game is live, (or it should be)
    elif ((current_date_time.split('.')[0] == next_game.date) and 
            (convert_to_24hour(current_date_time.split('.')[1]) > convert_to_24hour(next_game.time))):
        
        game_complete = complete_game(next_game.gameid, next_game)
        if not game_complete:

            game_stats = get_live_updates(next_game)
            return render_template('live.html', game=next_game, game_stats=game_stats, game_status="LIVE")
            
        return render_template('most-recent.html', game=next_game, game_status="GAME COMPLETED")
    
    #Otherwise, displays the next game
    else:
        return render_template('next-game.html', game=next_game, game_status="NEXT GAME")

@app.route('/most-recent')
def display_most_recent():
    #Display if game was played on todays date
    most_recent_game = Game.query.filter_by(most_recent=True).first()
    return render_template('most-recent.html', game=most_recent_game)

@app.route('/next-game')
def display_next_game():
    #Display if there was not a game played today
    next_game = Game.query.filter_by(next_game=True).first()
    return render_template('next-game.html', game=next_game)

@app.route('/game')
def display_game():
    id = request.args.get('id')
    current_date_time = get_current_date_time()

    game = Game.query.filter_by(id=id).first()
    if ((current_date_time.split('.')[0] == game.date) and 
            (convert_to_24hour(current_date_time.split('.')[1]) > convert_to_24hour(game.time)) and
            game.most_recent != True):
        game_stats = get_live_updates(game)
        return render_template('live.html', game=game, game_stats=game_stats, game_status="LIVE")
    elif game.game_status == "Unplayed":
        return render_template('next-game.html', game=game, game_status="UPCOMING GAME")
    else:
        return render_template('most-recent.html', game=game, game_status="GAME COMPLETE")

@app.route('/demo')
def display_demo():

    next_game = Game.query.filter_by(next_game=True).first()
    return render_template('demo.html', game=next_game)
    
"""
TODO:
    Player stats - blues
        DB
    Leaderboards
        API
    Standings
        DB
"""


if __name__ == "__main__":
    app.run()
