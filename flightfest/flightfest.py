from flask import Flask
from flask import request
from flask import render_template
from constants import ORIGIN, STUBHUB_BASE_URL
from api_calls import get_events, get_listings, get_flights
from collections import Counter

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

    events = get_events(search_terms)

    params_dict = {}

    for idx, event in enumerate(events):
        params_dict['lat{}'.format(idx+1)] = event['venue']['latitude']
        params_dict['long{}'.format(idx+1)] = event['venue']['longitude']
        params_dict['description{}'.format(idx+1)] = popup_content(event)

        # # get min ticket price
        # import json
        # with open('listing.json', 'w') as f:
        #     json.dump(get_listings(event['id']), f)

        # for date, city in zip(dates, cities):
        #     get_emirates_results(date, ORIGIN, city, 'Economy')
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

    # Set venue name
    venue = event['displayAttributes']['primaryName']

    # Set location string
    venue_dict = event['venue']
    city, state, country = venue_dict['city'], venue_dict['state'], venue_dict['country']
    if country == 'US':
        geo_parts = [city, state]
    else:
        geo_parts = [city, country]
    geo_string = ', '.join(geo_parts)

    # Set ticket link
    tlink = ticket_link(event)

    # Set date string
    date = event['eventDateLocal']
    date_str = '/'.join([date[5:7], date[8:10], date[:4]])

    # Build popup content
    content = ' <br> '.join([name, venue, geo_string, date_str, tlink])
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

    return """<a href="{}">{}<\\a>""".format(ticket_url, link_text)


if __name__ == '__main__':
    app.run("0.0.0.0", port=5000)
