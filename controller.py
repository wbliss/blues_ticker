import queue

from flask import flash, redirect, render_template, request, session

from app import app
from models import Game, db
from update import stats_queue


@app.route('/')
def index():
    return None
    #Gets current date/time
    #If day of next game and time of: display live
        #refresh after 5 minutes
    #If day of game and not time of: display next
        #refresh every 30 minutes
    #If not day of game: display most recent
        #refresh every day


@app.route('/most-recent')
def display_most_recent():
    #Display if game was played on todays date
    most_recent_game = Game.query.filter_by(most_recent=True).first()
    return render_template('live.html', game_stats=most_recent_game)

@app.route('/next-game')
def display_next_game():
    #Display if there was not a game played today
    next_game = Game.query.filter_by(next_game=True).first()
    return render_template('live.html', game_stats=next_game)

@app.route('/live')
def display_live_game():
    if stats_queue.empty():
        return render_template('live.html', game_status="Empty")
    game_stats = stats_queue.get()
    return render_template('live.html', game_stats=game_stats)

if __name__ == "__main__":
    app.run()
