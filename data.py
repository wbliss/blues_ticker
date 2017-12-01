from ohmysportsfeedspy import MySportsFeeds
from config import username, password

msf = MySportsFeeds(version='1.0')
msf.authenticate(username, password)

def import_all():
    output = msf.msf_get_data(league='nhl', season='current', feed='full_game_schedule', team='stl', format='json')
    output = msf.msf_get_data(league='nhl', season='current', feed='team_gamelogs', team='stl', format='json')

if __name__ == "__main__":
    output = msf.msf_get_data(league='nhl', season='current', feed='scoreboard', fordate='20171129', team='stl', format='json')
