import json

from flask import Flask
from flask import request
from flask import render_template
from constants import ORIGIN, STUBHUB_BASE_URL, DAYS_AFTER_TO_RETURN, DAYS_BEFORE_TO_DEPART, \
    FLIGHT_CLASS, USE_MOCK_EMIRATES_API_FOR_SPEED, MOCK_FLIGHT_CURRENCY, MOCK_MIN_FLIGHT_PRICE, \
    DATE_FORMAT, FLIGHT_URL_TEMPLATE, AIRPORT_LAT_LONG_FILE, AIRPORT_TIMEZONE_FILE
from api_calls import get_events, get_listings, get_flights
from collections import Counter
from datetime import datetime, timedelta
from dateutil.parser import parse as datepar
from geopy.distance import vincenty
from operator import itemgetter

app = Flask(__name__)

app.debug = True


@app.route('/')
def render_home_page():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def get_and_show_results():
    search_terms = request.form['search_terms']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    all_events = get_events(search_terms)

    # set event time at origin for every event
    for event in all_events:
        event_datetime_utc = datepar(event['eventDateUTC']).replace(tzinfo=None)
        event['eventDateTimeOrigin'] = event_datetime_utc + timedelta(hours=ORIGIN_TIMEZONE)

    # filter events that I can't make it to.
    now_origin = datetime.utcnow() + timedelta(hours=ORIGIN_TIMEZONE)
    # events = filter(lambda x: x['eventDateTimeOrigin'] > now_origin, all_events)

    now_utc = datetime.utcnow()

    events = []
    for event in all_events:
        event_datetime_utc = datepar(event['eventDateUTC']).replace(tzinfo=None)

        venue_dict = event['venue']
        vincenty(ORIGIN)
        if event_datetime_utc > now_utc :


    if not events:
        return render_template("no_results.html")

    params_dict = {}

    for idx, event in enumerate(events):
        params_dict['lat{}'.format(idx+1)] = event['venue']['latitude']
        params_dict['long{}'.format(idx+1)] = event['venue']['longitude']
        params_dict['description{}'.format(idx+1)] = popup_content(event)

    for idx_2 in range(idx, 10):
        params_dict['lat{}'.format(idx_2+1)] = params_dict['lat1']
        params_dict['long{}'.format(idx_2+1)] = params_dict['long1']
        params_dict['description{}'.format(idx_2+1)] = params_dict['description1']

    return render_template("results.html", **params_dict)


def popup_content(event):
    # Set event name
    performers = event.get('performers')
    if performers:
        name = performers[0]['name']
    else:
        performers_collection = event.get('performersCollection')
        if performers_collection:
            name = performers_collection[0]['name']
        else:
            name = event['name']

    # Set location string
    venue_dict = event['venue']
    city, state, country = venue_dict['city'], venue_dict['state'], venue_dict['country']
    if country == 'US':
        geo_parts = [city, state, country]
    else:
        geo_parts = [city, country]
    geo_string = ', '.join(geo_parts)

    # Set venue name
    venue = event['displayAttributes'].get('primaryName')
    if not venue:
        venue = venue_dict['name']

    # Set date string
    date = event['eventDateLocal']
    date_str = '/'.join([date[5:7], date[8:10], date[:4]])

    # Set ticket link
    tlink = ticket_link(event)

    # Set image
    image = '<img src="{}" alt="" style="width:100px">'.format(event['imageUrl'])

    # Set flight string
    f_link = flight_link(venue_dict, event['eventDateTimeOrigin'],
                         event['eventDateLocal'], FLIGHT_CLASS)

    # Build popup content
    content = ' <br> '.join([image, name, venue, geo_string, date_str, f_link, tlink])
    return content


def ticket_link(event):
    # Set ticket url
    ticket_url = ''.join([STUBHUB_BASE_URL, event['eventUrl']])

    # Set ticket link text
    listings_dict = get_listings(event['id'])
    listings = listings_dict['listing']

    if listings:
        currencies = [listing['currentPrice']['currency'] for listing in listings]
        most_common_currency = Counter(currencies).most_common()[0][0]
        min_price = min([listing['currentPrice']['amount'] for listing in listings
                         if listing['currentPrice']['currency'] == most_common_currency])

        link_text = "Tickets from {0:.2f} {1:s} (includes fees)".format(min_price,
                                                                     most_common_currency)
    else:
        link_text = "No tickets currently on StubHub"

    return link(ticket_url, link_text)


def flight_link(venue, event_datetime_origin, event_date_local, flight_class):
    # Determine departure and return dates.
    # Departure time is three days before the concert, in the timezone of the origin airport,
    # or the current time at the origin airport, whichever is later.
    min_departure_datetime_origin = event_datetime_origin - timedelta(days=DAYS_BEFORE_TO_DEPART)
    now_origin = datetime.utcnow() + timedelta(hours=ORIGIN_TIMEZONE)
    departure_datetime_origin = max(min_departure_datetime_origin, now_origin)
    departure_date = departure_datetime_origin.strftime(DATE_FORMAT)

    # Return time is three days after the concert in the concert time zone.
    event_datetime_local = datepar(event_date_local).replace(tzinfo=None)
    return_date = (event_datetime_local + timedelta(days=DAYS_AFTER_TO_RETURN)).strftime(
        DATE_FORMAT)

    # Find nearest airport to venue
    distances = [vincenty((venue['latitude'], venue['longitude']),
                          (airport['lat'], airport['long'])) for airport in AIRPORT_LAT_LONGS]
    destination = min(zip(AIRPORT_LAT_LONGS, distances), key=itemgetter(1))[0]['code']

    # Set flight link text
    link_text = flight_string(departure_date, return_date, destination, flight_class)

    # Set flight url
    flight_url = FLIGHT_URL_TEMPLATE.format(ORIGIN, destination, departure_date, return_date)

    return link(flight_url, link_text)


def flight_string(departure_date, return_date, destination, flight_class):
    if not USE_MOCK_EMIRATES_API_FOR_SPEED:
        departure_flights = get_flights(departure_date, ORIGIN, destination, flight_class)
        return_flights = get_flights(return_date, destination, ORIGIN, flight_class)

        currencies = [flight['Currency'] for flight in departure_flights + return_flights]
        most_common_currency = Counter(currencies).most_common()[0][0]

        min_departure_price = min_flight_price(departure_flights, most_common_currency)
        min_return_price = min_flight_price(return_flights, most_common_currency)
    else:
        most_common_currency = MOCK_FLIGHT_CURRENCY
        min_departure_price = MOCK_MIN_FLIGHT_PRICE
        min_return_price = MOCK_MIN_FLIGHT_PRICE

    min_price = min_departure_price + min_return_price

    return "Flights from {} {}".format(min_price, most_common_currency)


def min_flight_price(flights, currency):
    return min([int(flight['FlightFare'].split(flight['Currency'])[0]) for flight in flights
                if flight['Currency'] == currency])


def link(url, link_text):
    return """<a target="_blank" href="{}">{}<\\a>""".format(url, link_text)

if __name__ == '__main__':
    with open(AIRPORT_LAT_LONG_FILE) as f:
        AIRPORT_LAT_LONGS = json.load(f)

    with open(AIRPORT_TIMEZONE_FILE) as f:
        AIRPORT_TIMEZONES = json.load(f)

    ORIGIN_TIMEZONE = AIRPORT_TIMEZONES[ORIGIN]

    app.run("0.0.0.0", port=5000)
