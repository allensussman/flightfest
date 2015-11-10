from flask import Flask
from flask import request
from flask import render_template
from constants import ORIGIN, STUBHUB_BASE_URL
from api_calls import get_events, get_listings, get_flights

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

        performers = event.get('performers')
        if performers:
            name = performers[0]['name']
        else:
            performers_collection = event.get('performersCollection')
            if performers_collection:
                name = performers_collection[0]['name']
            else:
                name = event['name']

        venue = event['displayAttributes']['primaryName']

        venue_dict = event['venue']
        city, state, country = venue_dict['city'], venue_dict['state'], venue_dict['country']
        if country == 'US':
            geo_parts = [city, state]
        else:
            geo_parts = [city, country]
        geo_string = ', '.join(geo_parts)

        ticket_url = ''.join([STUBHUB_BASE_URL, event['eventUrl']])
        ticket_link = """<a href="{}">Buy show tickets<\\a>""".format(ticket_url)

        date = event['eventDateLocal']
        date_str = '/'.join([date[5:7], date[8:10], date[:4]])

        description = ' <br> '.join([name, venue, geo_string, date_str, ticket_link])
        params_dict['description{}'.format(idx+1)] = description

        print get_listings(event['id'])

        # for date, city in zip(dates, cities):
        #     get_emirates_results(date, ORIGIN, city, 'Economy')
    return render_template("results.html", **params_dict)


@app.route('/slides.html')
def render_slides_page():
    return render_template("slides.html")

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000)
