from app import db, app

class Game(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(120))
    date = db.Column(db.String(120))
    time = db.Column(db.String(120))
    away_team = db.Column(db.String(120))
    home_team = db.Column(db.String(120))
    away_goals = db.Column(db.String(120))
    home_goals = db.Column(db.String(120))
    game_status = db.Column(db.String(120))
    most_recent = db.Column(db.Boolean)
    next_game = db.Column(db.Boolean)

    def __init__(self, game_id, date, time, away_team, home_team, next_game=False):
        """Scrapes game information from API"""
        
        self.game_id = game_id
        self.date = date
        self.time = time
        self.away_team = away_team
        self.home_team = home_team
        self.away_goals = 0
        self.home_goals = 0
        self.game_status = "Unplayed"
        self.most_recent = False
        self.next_game = next_game

    def complete_game(self, away_goals, home_goals, game_status):
        """Marks game as completed, populates score"""

        game = Game.query.filter_by(game_id=self.game_id)
        self.away_goals = away_goals
        self.home_goals = home_goals
        self.game_status = "Final{}".format(game_status)
        
        game = Game.query.filter_by(game_id=self.game_id).first()
        self.most_recent = True
        self.next_game = False
        
        if game.id != 1:
            prev_game = Game.query.filter_by(id=(game.id-1)).first()
            prev_game.most_recent = False
        
        if game.id != 82:
            next_game = Game.query.filter_by(id=(game.id+1)).first()
            next_game.next_game = True
            
        
    def __repr__(self):
       
        if self.game_status == "Unplayed":
            return ("\nID: " + self.game_id 
            + "\nDate: " + self.date 
            + "\nTime: " + self.time 
            + " ET\nAway Team: " + self.away_team 
            + "\nHome Team: " + self.home_team 
            + "\nStatus: " + self.game_status + "\n")

        else:
            return ("\nID: " + self.game_id 
            + "\nDate: " + self.date 
            + "\nTime: " + self.time 
            + " ET\nAway Team: " + self.away_team +"-" + str(self.away_goals) 
            + "\nHome Team: " + self.home_team + "-" + str(self.home_goals) 
            + "\nStatus: " + self.game_status + "\n")