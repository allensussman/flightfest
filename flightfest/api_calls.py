from constants import STUBHUB_API, CONCERT_QUERY, EMIRATES_API
from config_local import EMIRATES_API_KEY, STUBHUB_API_KEY
import requests
import json


def get_events(query):
    query = '&'.join([STUBHUB_API, CONCERT_QUERY, ''.join(['q=', query])])
    headers = {'contentType': 'application/json',
               'Authorization': 'Bearer {}'.format(STUBHUB_API_KEY),
               'Accept': 'application/json'}
    return json.loads(requests.get(query, headers=headers).content)['events']


def get_flights(date, origin, destination, flight_class):
    query = ''.join([EMIRATES_API, '&'.join([''.join(['FlightDate=', date]),
                                             ''.join(['Origin=', origin]),
                                             ''.join(['Destination=', destination]),
                                             ''.join(['Class=', flight_class])])])
    headers = {'Authorization': 'Bearer {}'.format(EMIRATES_API_KEY)}
    return json.loads(requests.get(query, headers=headers, verify=False).content)
