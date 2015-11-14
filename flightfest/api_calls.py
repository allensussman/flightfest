from constants import STUBHUB_EVENT_SEARCH_API, STUBHUB_INVENTORY_SEARCH_API, CONCERT_QUERY, \
    EMIRATES_API, SORT_BY_POPULARITY
from config_local import EMIRATES_API_KEY, STUBHUB_API_KEY
import requests
import json


def get_events(query):
    query = '&'.join([STUBHUB_EVENT_SEARCH_API, CONCERT_QUERY, SORT_BY_POPULARITY,
                      ''.join(['q=', query])])
    headers = {'contentType': 'application/json',
               'Authorization': 'Bearer {}'.format(STUBHUB_API_KEY),
               'Accept': 'application/json'}
    return json.loads(requests.get(query, headers=headers).content)['events']


def get_listings(event_id):
    query = '&'.join([STUBHUB_INVENTORY_SEARCH_API, ''.join(['eventid=', str(event_id)])])
    headers = {'contentType': 'application/json',
               'Authorization': 'Bearer {}'.format(STUBHUB_API_KEY),
               'Accept': 'application/json'}
    return json.loads(requests.get(query, headers=headers).content)


def get_flights(date, origin, destination, flight_class):
    query = ''.join([EMIRATES_API, '&'.join([''.join(['FlightDate=', date.strftime('%Y-%m-%d')]),
                                             ''.join(['Origin=', origin]),
                                             ''.join(['Destination=', destination]),
                                             ''.join(['Class=', flight_class])])])
    headers = {'Authorization': 'Bearer {}'.format(EMIRATES_API_KEY)}
    result = json.loads(requests.get(query, headers=headers, verify=False).content)
    return result['FlightAvailabilityList']
