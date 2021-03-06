import os

STUBHUB_API = 'https://api.stubhub.com/'

STUBHUB_EVENT_SEARCH_API = ''.join([STUBHUB_API, '/search/catalog/events/v3?&'])
CONCERT_QUERY = 'categoryId=1'
SORT_BY_POPULARITY = 'sort=popularity desc'
FIELD_LIST = 'fieldList=venue,name,displayAttributes,eventDateLocal,imageUrl,eventDateUTC,' \
            'eventUrl,id,ticketInfo'
STUBHUB_INVENTORY_SEARCH_API = ''.join([STUBHUB_API, '/search/inventory/v1?&'])

STUBHUB_BASE_URL = 'http://www.stubhub.com/'

EMIRATES_API = \
    'https://ec2-54-77-6-21.eu-west-1.compute.amazonaws.com:8143/flightavailability/1.0/?'

DAYS_BEFORE_TO_DEPART = 3
DAYS_AFTER_TO_RETURN = 3

FLIGHT_CLASS = 'Economy'

USE_EMIRATES_API = False
USE_MIN_TICKET_PRICE_IN_EVENT = True

DATE_FORMAT = '%Y-%m-%d'

FLIGHT_URL_TEMPLATE = 'http://www.kayak.com/flights/{},nearby-{},nearby/{}-flexible/{}-flexible'

AIRPORT_JSONS_DIR = os.path.join(os.path.dirname(__file__), 'static')
AIRPORT_LAT_LONG_FILE = os.path.join(AIRPORT_JSONS_DIR, 'airport_lat_longs.json')
AIRPORT_TIMEZONE_FILE = os.path.join(AIRPORT_JSONS_DIR, 'airport_timezone.json')

NO_TICKETS_STR = "No tickets currently on StubHub"
