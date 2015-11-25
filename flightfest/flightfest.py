import json
import traceback

from flask import Flask
from flask import request
from flask import render_template
from constants import STUBHUB_BASE_URL, DAYS_AFTER_TO_RETURN, DAYS_BEFORE_TO_DEPART, \
    FLIGHT_CLASS, USE_EMIRATES_API, USE_MIN_TICKET_PRICE_IN_EVENT, DATE_FORMAT, \
    FLIGHT_URL_TEMPLATE, AIRPORT_LAT_LONG_FILE, AIRPORT_TIMEZONE_FILE, NO_TICKETS_STR
from api_calls import get_events, get_listings, get_flights
from collections import Counter
from datetime import datetime, timedelta
from dateutil.parser import parse as datepar
from geopy.distance import vincenty
from operator import itemgetter

app = Flask(__name__)

app.debug = True

with open(AIRPORT_LAT_LONG_FILE) as f:
    AIRPORT_LAT_LONGS = json.load(f)

with open(AIRPORT_TIMEZONE_FILE) as f:
    AIRPORT_TIMEZONES = json.load(f)


@app.route('/')
def render_home_page():
    return render_template("index.html")


@app.route('/about.html')
def render_about_page():
    return render_template("about.html")


@app.route('/', methods=['POST'])
def get_and_show_results():
    try:
        origin = request.form['origin']
        search_terms = request.form['search_terms']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        events = get_events(search_terms, stubhub_date(start_date), stubhub_date(end_date))

        if not events:
            return render_template("no_results.html")

        params_dict = {}

        idx = 0
        for idx, event in enumerate(events):
            params_dict['lat{}'.format(idx+1)] = event['venue']['latitude']
            params_dict['long{}'.format(idx+1)] = event['venue']['longitude']
            params_dict['description{}'.format(idx+1)] = popup_content(event, origin)

        for idx_2 in range(idx, 10):
            params_dict['lat{}'.format(idx_2+1)] = params_dict['lat1']
            params_dict['long{}'.format(idx_2+1)] = params_dict['long1']
            params_dict['description{}'.format(idx_2+1)] = params_dict['description1']

        params_dict['search_terms'] = html_string(search_terms)

        return render_template("results.html", **params_dict)
    except:
        traceback.print_exc()
        return render_template("error.html")


def popup_content(event, origin):
    # Set event name.  The following seems to be the order of display-friendliness.
    performers = event.get('performers')
    if performers:
        raw_name = performers[0]['name']
    else:
        performers_collection = event.get('performersCollection')
        if performers_collection:
            raw_name = performers_collection[0]['name']
        else:
            raw_name = event['name']
    name = html_string(raw_name)

    # Set location string
    venue_dict = event['venue']
    city, state, country = venue_dict['city'], venue_dict['state'], venue_dict['country']
    if country == 'US':
        geo_parts = [city, state, country]
    else:
        geo_parts = [city, country]
    geo_string = html_string(', '.join(geo_parts))

    # Set venue name.  The following seems to be the order of display-friendliness.
    venue = event['displayAttributes'].get('primaryName')
    if not venue:
        venue = html_string(venue_dict['name'])

    # Set date string
    date = event['eventDateLocal']
    date_str = '/'.join([date[5:7], date[8:10], date[:4]])

    # Set ticket link
    tlink = ticket_link(event)

    # Set image
    image = '<img src="{}" alt="" style="width:100px">'.format(event['imageUrl'])

    # Set flight link
    f_link = flight_link(origin, venue_dict, event['eventDateUTC'], FLIGHT_CLASS)

    # Build popup content
    content = ' <br> '.join([image, name, venue, geo_string, date_str, f_link, tlink])
    return content


def ticket_link(event):
    # Set ticket url
    ticket_url = ''.join([STUBHUB_BASE_URL, event['eventUrl']])

    # Set ticket link text
    if USE_MIN_TICKET_PRICE_IN_EVENT:
        # Get min ticket price from event
        ticket_info = event.get('ticketInfo', {})
        min_price = ticket_info.get('minListPrice')
        currency = ticket_info.get('currencyCode')
        num_listings = ticket_info.get('totalListings')
        if min_price and currency and num_listings:
            link_text = "{0:d} tickets from {1:.2f} {2:s}".format(num_listings, min_price, currency)
        else:
            link_text = NO_TICKETS_STR
    else:
        # Get min ticket price by using StubHub Inventory Search API
        listings_dict = get_listings(event['id'])
        listings = listings_dict['listing']

        if listings:
            # Find most common currency and min of prices with that currency
            currencies = [listing['currentPrice']['currency'] for listing in listings]
            most_common_currency = Counter(currencies).most_common()[0][0]
            min_price = min([listing['currentPrice']['amount'] for listing in listings
                             if listing['currentPrice']['currency'] == most_common_currency])

            link_text = "Tickets from {0:.2f} {1:s} (includes fees)".format(min_price,
                                                                            most_common_currency)
        else:
            link_text = NO_TICKETS_STR

    return link(ticket_url, link_text)


def flight_link(origin, venue, concert_datetime_utc_str, flight_class):
    # Determine departure and return dates.  Departure time is three days before the concert,
    # in the timezone of the origin airport, or the current time at the origin airport, whichever
    # is later.
    concert_datetime_utc = datepar(concert_datetime_utc_str).replace(tzinfo=None)
    min_departure_datetime_utc = (concert_datetime_utc - timedelta(days=DAYS_BEFORE_TO_DEPART))
    now_utc = datetime.utcnow()
    departure_datetime_utc = max(min_departure_datetime_utc, now_utc)
    departure_datetime_local = departure_datetime_utc + timedelta(hours=AIRPORT_TIMEZONES[origin])
    departure_date = departure_datetime_local.strftime(DATE_FORMAT)

    return_datetime = concert_datetime_utc + timedelta(days=DAYS_AFTER_TO_RETURN)
    return_date = return_datetime.strftime(DATE_FORMAT)

    # Find nearest airport to venue
    lat_longs_and_distances = []
    for airport in AIRPORT_LAT_LONGS:
        try:
            distance = vincenty((venue['latitude'], venue['longitude']),
                                (airport['lat'], airport['long']))
            lat_longs_and_distances += [(airport, distance)]
        except ValueError:
            # Vincenty has a bug and will (very infrequently) not converge and throw a ValueError
            pass
    destination = min(lat_longs_and_distances, key=itemgetter(1))[0]['code']

    # Set flight link text
    link_text = flight_string(departure_date, return_date, origin, destination, flight_class)

    # Set flight url
    flight_url = FLIGHT_URL_TEMPLATE.format(origin, destination, departure_date, return_date)

    return link(flight_url, link_text)


def flight_string(departure_date, return_date, origin, destination, flight_class):
    if USE_EMIRATES_API:
        departure_flights = get_flights(departure_date, origin, destination, flight_class)
        return_flights = get_flights(return_date, destination, origin, flight_class)

        # Find most common currency and min of prices with that currency
        currencies = [flight['Currency'] for flight in departure_flights + return_flights]
        most_common_currency = Counter(currencies).most_common()[0][0]

        min_departure_price = min_flight_price(departure_flights, most_common_currency)
        min_return_price = min_flight_price(return_flights, most_common_currency)

        min_price = min_departure_price + min_return_price

        return "Flights from {} {}".format(min_price, most_common_currency)
    else:
        return "Find flights..."


def stubhub_date(date):
    month, day, year = date.split('/')
    return '-'.join([year, month, day])


def min_flight_price(flights, currency):
    """Of flights using a certain currency, returns the min price.

    Args:
        flights (list of dicts): list of flights e.g.
            [{'FlightFare': '1200AED', 'Currency': 'AED', 'FlightNo': 'EK542', ...},
             {'FlightFare': '1000USD', 'Currency': 'USD', 'FlightNo': 'EK545', ....},
             ...]
        currency (string): only consider flights with this currency

    """
    # flight dict looks like e.g. {'FlightFare': '1200AED', 'Currency': 'AED'}
    return min([int(flight['FlightFare'].split(flight['Currency'])[0]) for flight in flights
                if flight['Currency'] == currency])


def html_string(string):
    return string.replace('\'', '&#39;')


def link(url, link_text):
    return """<a target="_blank" href="{}">{}<\\a>""".format(url, link_text)

if __name__ == '__main__':

    app.run("0.0.0.0", port=5000)
