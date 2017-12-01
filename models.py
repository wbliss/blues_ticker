class Game():
    def __init__(self, id, date, time, away_team, home_team):
        """Scrapes game information from API"""
        
        self.id = id
        self.date = date
        self.time = time
        self.away_team = away_team
        self.home_team = home_team
        self.away_goals = 0
        self.home_goals = 0
        self.game_status = "Unplayed"

    def complete_game(self, away_goals, home_goals, game_status):
        """Marks game as completed, populates score"""

        self.away_goals = away_goals
        self.home_goals = home_goals
        self.game_status = "Final{}".format(game_status)

 

    def __repr__(self):
       
        if self.game_status == "Unplayed":
            return ("\nID: " + self.id 
            + "\nDate: " + self.date 
            + "\nTime: " + self.time 
            + " ET\nAway Team: " + self.away_team 
            + "\nHome Team: " + self.home_team 
            + "\nStatus: " + self.game_status + "\n")

        else:
            return ("\nID: " + self.id 
            + "\nDate: " + self.date 
            + "\nTime: " + self.time 
            + " ET\nAway Team: " + self.away_team +"-" + str(self.away_goals) 
            + "\nHome Team: " + self.home_team + "-" + str(self.home_goals) 
            + "\nStatus: " + self.game_status + "\n")