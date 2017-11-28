import json
from models import Game

with open('results/team_gamelogs-nhl-current.json', 'r') as completed:
    completed_games = json.load(completed)

with open('results/full_game_schedule-nhl-current.json', 'r') as games:
    all_games = json.load(games)
    

def create_all_games(game_data, gamelog):
    
    all_games = []

    #populates game id, date, time, teams
    game_data = game_data.pop('fullgameschedule') # creates dict
    game_data = game_data.pop('gameentry') # creates list

    for data_index, unplayed_game in enumerate(game_data):
        new_game = Game(game_data[data_index])
        all_games.append(new_game)

    #checks via game id if game is completed. If it is, populates game with the final score
    gamelog = gamelog.pop('teamgamelogs') # creates dict
    gamelog = gamelog.pop('gamelogs') # creates list
    
    for score_index, completed_game in enumerate(gamelog):
        completed_game_info = completed_game.pop('game')
        completed_game_stats = completed_game.pop('stats')
        game = all_games[score_index]
        if game.id == completed_game_info.get('id'):
            game.complete_game(completed_game_stats)
            all_games.remove(game)
            all_games.insert(score_index, game)

    return all_games

def main():
    print(create_all_games(all_games, completed_games))

if __name__ == "__main__":
    main()



