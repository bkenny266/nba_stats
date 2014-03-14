#!/usr/bin/python

import sys
from StringIO import StringIO
import urllib
import urllib2
import gzip
import json
import datetime
import dateutil.parser
import time

#pulled out XMLstats token
access_token = ""

# Replace with your bot name and email/website to contact if there is a problem
# e.g., "mybot/0.1 (https://erikberg.com/)"
user_agent = "test (bkenny@gmail.com)"


def get_game_ids(date):
    """Accepts a date argument as datetime.date or string
    Returns a list of completed game_ids
    """
    data = get_events(date)
    games = []

    for game in data['event']:
        if game['event_status'] == "completed":
            games.append(game['event_id'])

    return games


def get_events(date):
    """Date argument can be datetime.date or string
        Returns requested dictionary of events on date
    """
    if date == datetime.date:
        date = date.strftime("%Y%m%d")

    return process_request("events", date=date)


def get_boxscore(event_id):
    """Returns requested dictionary of boxscore for event_id"""
    return process_request("boxscore", event_id)


def process_request(*args, **kwargs):
    """intermediary function to control request flow"""
    while True:
        returned = request_json(*args, **kwargs)
        if type(returned) == float:
            if returned > 0:
                print "Request limit exceeded - pausing for {0} seconds".format(returned)
                time.sleep(returned)
            print "resuming..."
        else:
            return returned
            

def request_json(method, event_id=None, parameters=None, date=None):
    """Processes json requests to the XMLstats api, 
    Returns a dictionary of requested data or a (False, time_left)
    tuple if need to wait for time limit to expire.
    
    Currently implemented for boxscore and events methods
    method="boxscore" - requires event_id argument
    method="events" - requires date argument
    """
    host = "erikberg.com"
    format = "json"
    
    sport = None
    if method == "boxscore":
        sport = "nba"
        if event_id == None:
            raise Exception("boxscore method requires id argument")
    elif method == "events":
        if date == None:
            raise Exception("events method requires date argument")
        parameters = {'date' : date,
                        'sport' : 'nba'}
    else:
        raise Exception("not a valid method")

    # Pass method, format, and parameters to build request url
    url = build_url(host, sport, method, event_id, format, parameters)

    req = urllib2.Request(url)
    # Set Authorization header
    req.add_header("Authorization", "Bearer " + access_token)
    # Set user agent
    req.add_header("User-agent", user_agent)
    # Tell server we can handle gzipped content
    req.add_header("Accept-encoding", "gzip")

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, err:
        if err.code == 429:
            time_left = float(err.headers['xmlstats-api-reset']) - time.time()
            return time_left
        else:
            print "Error retrieving file: {}".format(err.code)
            sys.exit(1)
    except urllib2.URLError, err:
        print "Error retrieving file: {}".format(err.reason)
        sys.exit(1)

    data = None
    if "gzip" == response.info().get("Content-encoding"):
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        return json.loads(data)

    return json.loads(data)


def build_url(host, sport, method, id, format, parameters):
    """Builds URL string for requested data"""
    path = "/".join(filter(None, (sport, method, id)));
    url = "https://" + host + "/" + path + "." + format
    if parameters:
        paramstring = urllib.urlencode(parameters)
        url = url + "?" + paramstring
    return url


