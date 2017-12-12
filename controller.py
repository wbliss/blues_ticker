from flask import request, render_template, flash, session, redirect
from sqlalchemy import desc
from app import app, db
from models import db, Game
from data import *

@app.route('/most-recent')
def display_most_recent():
    #Display if game was played on todays date
    most_recent_game = Game.query.filter_by(most_recent=True).first()

@app.route('/next-game')
def display_next_game():
    #Display if there was not a game played today
    next_game = Game.query.filter_by(next_game=True).first()

def main():
    return None


if __name__ == "__main__":
    main()
