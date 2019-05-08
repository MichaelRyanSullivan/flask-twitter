from flask import *
import datetime as dt
import re
import pandas as pd
import datetime as dt
import csv
from twitterscraper import query_tweets
from flask import send_file

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['.csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Routes

# @app.route('/submit', methods=['GET', 'POST'])
# def submit():
#     if request.method == 'GET':
#         return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    query = query_from_request(request)
    startList = map(int, request.form['start'].split('-'))
    endList = map(int, request.form['end'].split('-'))

    startDate = dt.date(*startList)
    endDate = dt.date(*endList)

    output_name = 'outputs/o.csv'
    query_and_write(query, output_name, begindate=startDate,
            enddate=endDate)
    flash("done")
    return send_file(output_name)


def query_from_request(request):
    """ 
    Takes an HTTP request and constructs the query
    to be entered into twitterscraper module. 
    """
    query = ""
    ands = str(request.form['ands'])
    exact = str(request.form['exact'])
    ors = str(request.form['ors'])
    none = str(request.form['none'])
    hashtags = str(request.form['hashtags'])
    from_acct = str(request.form['from'])
    to_acct = str(request.form['to'])
    mentioning = str(request.form['mention'])

    # format the query
    query = query + ands
    if exact != '':
        exact = '\"{}\"'.format(exact)
        query = query + " " + exact
    if ors != '':
        ors =  ' OR '.join(ors.split(' '))
        query = query + " " + ors
    if none != '':
        none = ' '.join(map(lambda s: '-{}'.format(s), none.split(' ')))
        query = query + " " + none
    if hashtags != '':
        hashtags = ' '.join(map(lambda s: "#" + s, hashtags.split(' ')))
        query = query + " " + hashtags
    if from_acct != '':
        from_acct = ' OR '.join(map(lambda s: "from:" + s, from_acct.split(' ')))
        query = query + " " + from_acct
    if to_acct != '':
        to_acct = ' OR '.join(map(lambda s: "to:" + s, to_acct.split(' ')))
        query = query + " " + to_acct
    if mentioning != '':
        mentioning = ' OR '.join(map(lambda s: "@" + s, mentioning.split(' ')))
        query = query + " " + mentioning

    return query

def query_and_write(query, output_name, limit=2000,
                        begindate=dt.date(2006, 3, 21),
                        enddate=dt.date.today(),
                        poolsize=20,
                        lang=''):
    # perform query
    tweets = query_tweets(query, limit, begindate, enddate, poolsize, lang)
    # construct csv
    if tweets:
        with open(output_name, 'w+', encoding="utf-8") as output:
            f = csv.writer(output)
            f.writerow(["timestamp", "user", "fullname", "text", "hashtags", "id", "url", "retweets", "favorites", "replies"])
            for x in tweets:
                # parse text for hashta * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)gs
                tag_set = set(re.findall('\#\w+', x.text))
                tag_values = " ".join(tag_set)
                # add row for tweet in csv
                f.writerow([x.timestamp, x.user, x.fullname, x.text, tag_values, x.id, x.url, x.retweets, x.likes, x.replies])
    return 

@app.route('/credits', methods=['GET'])
def credits():
    return render_template('credits.html')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()

