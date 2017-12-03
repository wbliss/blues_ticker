import json
from models import db, Game

with open('results/team_gamelogs-nhl-current.json', 'r') as completed:
   completed_games = json.load(completed)

with open('results/full_game_schedule-nhl-current.json', 'r') as games:
    all_games = json.load(games)
    
def create_all_games(game_data, gamelog):
    """for use on initial setup, creates all games for season"""
    db.create_all()
    all_games = []

    #populates game id, date, time, teams
    game_data = game_data.pop('fullgameschedule') # creates dict
    game_data = game_data.pop('gameentry') # creates list


    for data_index, unplayed_game in enumerate(game_data):
        game_data = {}
        game_necessary_values = ['id', 'date', 'time', 'awayTeam', 'homeTeam']


        for game_value in game_necessary_values:
            if game_value == 'awayTeam' or game_value == 'homeTeam':
                team = unplayed_game.get(game_value)
                game_data[game_value] = team.get('Abbreviation')
            else:
                game_data[game_value] = unplayed_game.get(game_value)

        game_id = game_data.get('id')
        date = game_data.get('date')
        time = game_data.get('time')
        away_team = game_data.get('awayTeam')
        home_team = game_data.get('homeTeam')
        new_game = Game(game_id, date, time, away_team, home_team)
        db.session.add(new_game)
        all_games.append(new_game)

    #checks via game id if game is completed. If it is, populates game with the final score
    gamelog = gamelog.pop('teamgamelogs') # creates dict
    gamelog = gamelog.pop('gamelogs') # creates list
    
    for score_index, completed_game in enumerate(gamelog):
        completed_game_info = completed_game.pop('game')
        completed_game_stats = completed_game.pop('stats')
        
        stat_list = {}
        stats_necessary_values = ['Wins', 'Losses','GoalsFor', 'GoalsAgainst', 'OvertimeWins', 'OvertimeLosses']
        for stat_value in stats_necessary_values:
                stat = completed_game_stats.get(stat_value)
                stat_list[stat_value] = stat.get('#text')

        #Populates final score/checks if shootout
        game = all_games[score_index]
        game_status = ""
        home_team = game.home_team
        away_team = game.away_team
        if home_team == team:
            home_goals = int(stat_list.get('GoalsFor'))
            away_goals = int(stat_list.get('GoalsAgainst'))
            if stat_list['Wins'] == "1" and home_goals == away_goals:
                game_status = "/SO"
                home_goals += 1
            elif stat_list['Losses'] == "1" and home_goals == away_goals:
                game_status = "/SO"
                away_goals += 1
        else: 
            home_goals = int(stat_list.get('GoalsAgainst'))
            away_goals = int(stat_list.get('GoalsFor'))
            if stat_list['Wins'] == "1" and home_goals == away_goals:
                game_status = "/SO"
                away_goals += 1
            elif stat_list['Losses'] == "1" and home_goals == away_goals:
                game_status = "/SO"
                home_goals += 1

        #Checks if game went to overtime
        if stat_list.get('OvertimeWins') == '1' or stat_list.get('OvertimeLosses') == '1':
            game_status = "/OT"

        if game.game_id == completed_game_info.get('id'):
            game.complete_game(away_goals, home_goals, game_status)
            all_games.remove(game)
            all_games.insert(score_index, game)
    
    db.session.commit()
    return all_games

if __name__ == "__main__":
    create_all_games(all_games, completed_games)
