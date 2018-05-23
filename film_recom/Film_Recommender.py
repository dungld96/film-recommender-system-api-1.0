from surprise import SVD
from surprise import Dataset
from surprise import Reader
import operator

class Film_Recommender:
    base_data = None
    reader = None

    # -- Set Base Data
    def set_base_data(self, base_data):
        self.base_data = base_data

    def set_scale_range(self, lowest_rating, highest_rating):
        self.reader = Reader(rating_scale=(lowest_rating, highest_rating))

    def get_movie_id_not_rated(self, cur, user_id):
        # phim da xem boi userId 1
        query = "SELECT movieId FROM ratings WHERE userId = " + str(user_id)
        cur.execute(query)
        movieId_rated = ()
        for movieId in cur.fetchall():
            movieId_rated = movieId_rated + movieId

        # all phim
        cur.execute("SELECT movieId FROM movies")
        movieId_all = ()
        for movieId in cur.fetchall():
            movieId_all = movieId_all + movieId
        # print(movieId_all, movieId_rated)

        # phim chua danh gia boi user 1
        movie_id_not_rated = []
        for movie_id_in_movieId_all in movieId_all:
            if movie_id_in_movieId_all not in movieId_rated:
                movie_id_not_rated.append(movie_id_in_movieId_all)

        return movie_id_not_rated

    def get_pre_rating(self, movie_id_not_rated, user_id):

        df = self.base_data
        df = Dataset.load_from_df(df[['userId', 'movieId', 'rating']], self.reader)
        trainset = df.build_full_trainset()

        # Build an algorithm, and train it.
        algo = SVD(n_factors=160, n_epochs=100, lr_all=0.005, reg_all=0.1)
        algo.fit(trainset)

        rating_pred = {}
        for movie_id in movie_id_not_rated:
            pred = algo.predict(user_id, movie_id)
            rating_pred[movie_id] = pred.est
        return rating_pred
