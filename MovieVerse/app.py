from flask import Flask, render_template, request
from recommender import recommend_movies, get_poster

app = Flask(__name__)

# Fixed showcase list for the home page's "Trending Picks" section.
# (Separate from the ML recommendations - this is just a static display.)
TRENDING_MOVIES = [
    {"title": "Inception", "genre": "Sci-Fi • Thriller", "match": 97},
    {"title": "Interstellar", "genre": "Sci-Fi • Drama", "match": 95},
    {"title": "The Dark Knight", "genre": "Action • Crime", "match": 93},
    {"title": "The Matrix", "genre": "Sci-Fi • Action", "match": 90},
    {"title": "Whiplash", "genre": "Drama • Music", "match": 88},
]


@app.route("/")
def home():

    trending = []

    for movie in TRENDING_MOVIES:

        trending.append({
            "title": movie["title"],
            "genre": movie["genre"],
            "match": movie["match"],
            "poster": get_poster(movie["title"])
        })

    return render_template(
        "index.html",
        trending_movies=trending
    )

@app.route("/recommendations")
def recommendations():

    movie = request.args.get("movie", "").strip()

    if not movie:
        return render_template(
            "recommendations.html",
            recommendations=[],
            movie_name=None,
            error=None
        )

    recommendations = recommend_movies(movie)

    if len(recommendations) == 0:
        return render_template(
            "recommendations.html",
            recommendations=[],
            movie_name=movie,
            error="Movie not found! Please try another title."
        )

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        movie_name=movie,
        error=None
    )

if __name__ == "__main__":
    app.run(debug=True)