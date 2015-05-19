Ted Similarity Index
==

> This is just a proof of concept app. I believe a ted talk is nothing but a text manuscript of content. We can actually use the manuscripts of ted talks to compare them using nlp and then use the comparision score as a metric. So with this idea, I have created this proof of concept [app](http://ted-sim-index.rajeev-reddy.com/).

The main basis for comparing the manuscripts are the individual important features present in the manuscripts.

## [App's Working Screenshot](https://db.tt/bbqWzHLZ)

A lengthy blog post about the procedure I have followed and the idea behind is available [here](http://blog.rajeev-reddy.com/2015/05/18/ted-talks-similarity-index/)

### Note: To run this app locally you need to have installed scipy, numpy, scikit, nltk (with its data) installed

Local Installation & Running
--------------
```sh
git clone git@github.com:drreddy/tedtalks-similarity-index.git
cd tedtalks-similarity-index
pip install -r requirements.txt
python server.py
```

As I have mentioned this is just a proof of concept app many improvements can be done like:

1. User can search using string instead of using tags (which is implemented now).
2. Implement a CRON like service so that the data gets updated periodically.
3. Feature extraction and processing can be improved.
4. UI improvements and also Client side data validation.
5. Better algorithms for comparing the manuscripts.

Finally coming to technical parts of the app, The app is made of:

1. Python Tornado
2. tornado-sockjs
3. sockjs-client
4. nltk
5. scikit
6. elasticsearch
7. Bootswatch Lumen Template (with some customization)
