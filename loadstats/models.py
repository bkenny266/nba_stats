from django.db import models
from util.getjson import get_game_ids, get_boxscore
import datetime

##models.py

class Team(models.Model):
    name = models.CharField(max_length=50)
    initials = models.CharField(max_length=3)

    def __unicode__(self):
        return self.name

class Player(models.Model):

    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    team = models.ForeignKey(Team)

    def __unicode__(self):
        return u"%s %s" % (self.last_name, self.first_name)

class PlayerGame(models.Model):
    date = models.DateField()
    player = models.ForeignKey(Player)
    fg_percentage = models.DecimalField(decimal_places=1, max_digits=4)
    fg_attempted = models.IntegerField()
    fg_made = models.IntegerField() 
    points = models.IntegerField()
    assists = models.IntegerField()
    blocks = models.IntegerField()
    ft_percentage = models.DecimalField(decimal_places=1, max_digits=4)
    ft_attempted = models.IntegerField()
    ft_made = models.IntegerField()
    three_percentage = models.DecimalField(decimal_places=1, max_digits=4)
    three_attempted = models.IntegerField()
    three_made = models.IntegerField()
    minutes = models.IntegerField()
    defensive_rebounds = models.IntegerField()
    offensive_rebounds = models.IntegerField()
    personal_fouls = models.IntegerField()
    rebounds = models.IntegerField()
    steals = models.IntegerField()
    turnovers = models.IntegerField()



    def __unicode__(self):
        return u"%s"%self.points


def load_dates(start_date, end_date):
    """load all dates between start_date and end_date (inclusive)"""
    id_list = []
    d = start_date

    while d <= end_date:
        id_list = get_game_ids(d)
        for game in id_list:
            load_game(game)
        d += datetime.timedelta(days=1)


def load_game(gameid):
    """loads all of the game data from gameid to datebase"""
    data = get_boxscore(gameid)
    datestr = data['event_information']['start_date_time'][0:10]
    date = datetime.date(int(datestr[0:4]), int(datestr[5:7]), int(datestr[8:10]))

    teams=["home_stats", "away_stats"]
    for team in teams:
        for pl in data[team]:
            load_player_data(pl, date)



def load_player_data(playerdata, date):
    """loads player data to model from dictionary"""
    pg = PlayerGame()
    pg.fg_attempted = playerdata['field_goals_attempted']
    pg.fg_made = playerdata['field_goals_made']
    pg.points = playerdata['points']
    pg.assists = playerdata['assists']
    pg.blocks = playerdata['blocks']
    pg.fg_percentage = playerdata['field_goal_percentage']
    pg.ft_percentage = playerdata['free_throw_percentage']
    pg.ft_attempted = playerdata['free_throws_attempted']
    pg.ft_made = playerdata['free_throws_made']
    pg.three_percentage = playerdata['three_point_percentage']
    pg.three_attempted = playerdata['three_point_field_goals_attempted']
    pg.three_made = playerdata['three_point_field_goals_made']
    pg.minutes = playerdata['minutes']
    pg.defensive_rebounds = playerdata['defensive_rebounds']
    pg.offensive_rebounds = playerdata['offensive_rebounds']
    pg.personal_fouls = playerdata['personal_fouls']
    pg.rebounds = playerdata['rebounds']
    pg.steals = playerdata['steals']
    pg.turnovers = playerdata['turnovers']
    pg.date = date

    team = playerdata['team_abbreviation']

    #gets Player from database, or creates a new Player if doesn't exist
    try:
        pg.player = Player.objects.get(last_name=playerdata['last_name'], first_name=playerdata['first_name'], team__initials=team)
    except Player.DoesNotExist:
        pl = create_player(playerdata['last_name'], playerdata['first_name'], team=team)
        pg.player = pl

    pg.save()

def create_player(last_name, first_name, team):
    '''Creates a new Player object
    Raises an exception if the player already exists
    '''
    try:
        p = Player.objects.get(last_name='last_name', first_name=first_name, team__initials=team)
        raise Exception("Player already exists")
    except Player.DoesNotExist:
        p = Player()
        t = Team.objects.get(initials=team)
        p.team = t
        p.last_name = last_name
        p.first_name = first_name
        p.save()
        return p

def create_fake_player():
    p = Player()
    t = Team()
    t.name = "bks"
    t.save()
    p.team = t
    p.last_name = "kenny"
    p.first_name = "brian"
    p.save()

def get_stats():
    stat_list = []
    for i in range(1,60):
        ret = PlayerGame.objects.filter(fg_attempted=i)
        stat_list.append((i, ret.aggregate(models.Avg('points'))['points__avg'], len(ret)))

    return stat_list

def print_stats():
    fmt = u"{0:<8}{1:<8}{2:<8}"
    print fmt.format("FGA", "PTS", "FREQ")
    for i in get_stats():
        try:
            print fmt.format(i[0], round(i[1],1), i[2])
        except:
            pass

