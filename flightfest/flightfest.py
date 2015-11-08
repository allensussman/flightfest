from flask import Flask
from flask import request
from flask import render_template
from constants import ORIGIN, STUBHUB_BASE_URL
from api_calls import get_events, get_flights

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
        params_dict['name{}'.format(idx+1)] = event['name']
        params_dict['turl{}'.format(idx+1)] = ''.join([STUBHUB_BASE_URL, event['eventUrl']])
        params_dict['city{}'.format(idx+1)] = event['venue']['longitude']
        params_dict['date{}'.format(idx+1)] = event['eventDateLocal'][:10]

    # for date, city in zip(dates, cities):
    #     get_emirates_results(date, ORIGIN, city, 'Economy')
    return render_template("results.html", **params_dict)


@app.route('/slides.html')
def render_slides_page():
    return render_template("slides.html")

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000)
