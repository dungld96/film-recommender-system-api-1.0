from flask import Flask, request,jsonify
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
from surprise.model_selection import cross_validate
from film_recom.Film_Recommender import *
import pandas as pd
from collections import OrderedDict
import json

# Pre
app = Flask(__name__)
mysql = MySQL()

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'movie_lens'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# Init
mysql.init_app(app)
api = Api(app)
class Film_recommender(Resource):

    def get(self, userId):
        conn = mysql.connect()
        cur = conn.cursor()
        df = pd.read_sql('SELECT * FROM ratings', conn)
        df = df[list(df.columns)[0:]]

        user_id = userId

        # Init Recommender
        recom = Film_Recommender()
        recom.set_base_data(df)
        recom.set_scale_range(1, 5)
        movie_id_not_rated = recom.get_movie_id_not_rated(cur, user_id)

        rating_pred = recom.get_pre_rating(movie_id_not_rated, user_id)
        top_ten_pred = sorted(rating_pred.items(), key=operator.itemgetter(1), reverse=True)[0:20]
        return jsonify(top_ten_pred)

api.add_resource(Film_recommender, '/')
Film_recommender =  Film_recommender.as_view('Film_recommender')
app.add_url_rule(
    '/user/<int:userId>', view_func=Film_recommender, methods=['GET']
)
if __name__ == '__main__':
    app.run(debug=True)
