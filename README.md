# Flightfest
Search for concerts, view concert details, and buy tickets and flights to them.  [See it live.]
(http://www.flightfest.co)

## Installation
1. Clone repo.
2. Install virtualenv.  In terminal: `[sudo] pip install virtualenv`
3. Navigate to repo.
4. Install requirements into virtual environment: `make setup`
5. Setup StubHub credentials.
    1. Get [StubHub API key](https://developer.stubhub.com/store/).  
    2. Create `flightfest/config_local.py` 
    3. Add the line `STUBHUB_API_KEY = "<your StubHub API key>"` to `flightfest/config_local.py`.
6. (Not needed at this time) Setup Emirates credentials.
    1. Get [Emirates API key](https://ec2-54-77-6-21.eu-west-1.compute.amazonaws.com/store/site/pages/sign-up.jag?), proceeding past invalid certificate warning.
    2. Add the line `EMIRATES_API_KEY = "<your Emirates API key>"` to `flightfest/config_local.py`.

## Usage
1. In terminal, navigate to top level of repo. 
2. Activate virtual environment: `source venv/bin/activate` 
3. Start app: `python flightfest/flightfest.py`
4. Navigate to `0.0.0.0:5000` in your favorite browser and enjoy!

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request.

## Credits
- Allen Sussman worked on back-end and some front-end.
- Kelly Dern worked on design and some front-end.

## License
The MIT License (MIT)

Copyright (c) [2015] [Allen Sussman, Kelly Dern]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.