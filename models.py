class Game():
    def __init__(self, game_info):
        """Scrapes game information from API"""
        game_data = {}
        game_necessary_values = ['id', 'date', 'time', 'awayTeam', 'homeTeam']


        for game_value in game_necessary_values:
            if game_value == 'awayTeam' or game_value == 'homeTeam':
                team = game_info.get(game_value)
                game_data[game_value] = team.get('Abbreviation')
            else:
                game_data[game_value] = game_info.get(game_value)

        self.id = game_data.get('id')
        self.date = game_data.get('date')
        self.time = game_data.get('time')
        self.away_team = game_data.get('awayTeam')
        self.home_team = game_data.get('homeTeam')
        self.game_status = "Unplayed"

    def complete_game(self, stats):
        """Marks game as completed, populates score"""

        stat_list = {}
        stats_necessary_values = ['Wins', 'Losses','GoalsFor', 'GoalsAgainst', 'OvertimeWins', 'OvertimeLosses']
        for stat_value in stats_necessary_values:
            stat = stats.get(stat_value)
            stat_list[stat_value] = stat.get('#text')

        self.game_status = "Final"

        #Populates final score/checks if shootout
        if self.home_team == 'STL':
            self.home_goals = int(stat_list.get('GoalsFor'))
            self.away_goals = int(stat_list.get('GoalsAgainst'))
            if stat_list['Wins'] == "1" and self.home_goals == self.away_goals:
                self.game_status = "Final/SO"
                self.home_goals += 1
            elif stat_list['Losses'] == "1" and self.home_goals == self.away_goals:
                self.game_status = "Final/SO"
                self.away_goals += 1
        else: 
            self.home_goals = int(stat_list.get('GoalsAgainst'))
            self.away_goals = int(stat_list.get('GoalsFor'))
            if stat_list['Wins'] == "1" and self.home_goals == self.away_goals:
                self.game_status = "Final/SO"
                self.away_goals += 1
            elif stat_list['Losses'] == "1" and self.home_goals == self.away_goals:
                self.game_status = "Final/SO"
                self.home_goals += 1

        #Checks if Overtime
        if stat_list.get('OvertimeWins') == '1' or stat_list.get('OvertimeLosses') == '1':
            self.game_status = "Final/OT"
        

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