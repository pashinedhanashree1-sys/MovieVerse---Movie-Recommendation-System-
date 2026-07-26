import os
import re
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = "c44b5476203bd6d69af25dc61eb6afd9"

FALLBACK_POSTER = "https://placehold.co/500x750/1e1e1e/e50914?text=No+Poster"

# MovieLens titles look like "Dark Knight, The (2008)" - strip the year and
# flip the trailing article for a clean search query.
_YEAR_PATTERN = re.compile(r"\s*\((\d{4})\)\s*$")
_ARTICLE_PATTERN = re.compile(r"^(.*),\s*(The|A|An)$", re.IGNORECASE)


def get_poster(movie_title):

    # Remove the release year
    movie_title = re.sub(r"\s*\(\d{4}\)$", "", movie_title)

    # Remove aliases like (a.k.a. Se7en)
    movie_title = re.sub(r"\s*\(a\.k\.a\.[^)]+\)", "", movie_title)

    # Convert "Dark Knight, The" -> "The Dark Knight"
    if movie_title.endswith(", The"):
        movie_title = "The " + movie_title[:-5]
    elif movie_title.endswith(", A"):
        movie_title = "A " + movie_title[:-3]
    elif movie_title.endswith(", An"):
        movie_title = "An " + movie_title[:-4]

    url = "https://api.themoviedb.org/3/search/movie"

    response = requests.get(
        url,
        params={
            "api_key": API_KEY,
            "query": movie_title
        },
        timeout=10
    )

    if response.status_code != 200:
        return FALLBACK_POSTER

    data = response.json()

    if data.get("results"):

        poster = data["results"][0].get("poster_path")

        if poster:
            return f"https://image.tmdb.org/t/p/w500{poster}"

    return FALLBACK_POSTER
    
from sklearn.neighbors import NearestNeighbors
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
print(movies.head())

print(ratings.head())
movie_genres = movies.set_index("title")["genres"].to_dict()
print(movies.shape)
print(ratings.shape)

movie_data = pd.merge(ratings, movies, on="movieId")

print(movie_data.head())
print(movie_data.isnull().sum())

movies["clean_title"] = movies["title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)

movie_rating_count = movie_data.groupby("title")["rating"].count().reset_index()

movie_rating_count.rename(
    columns={"rating": "totalRatings"},
    inplace=True
)

movie_data = movie_data.merge(
    movie_rating_count,
    on="title"
)

movie_data = movie_data[
    movie_data["totalRatings"] >= 50
]

user_movie_matrix = movie_data.pivot_table(
    index="title",
    columns="userId",
    values="rating"
)

user_movie_matrix.fillna(0, inplace=True)
print(user_movie_matrix.shape)

model = NearestNeighbors(
    metric="cosine",
    algorithm="brute",
    n_neighbors=6
)

model.fit(user_movie_matrix)

print("Model trained successfully!")

def recommend_movies(movie_name):

    matching_movies = [
    title for title in user_movie_matrix.index
    if movie_name.lower() in title.lower()
    ]

    if len(matching_movies) == 0:
        return []

    movie_name = matching_movies[0]

    movie_vector = user_movie_matrix.loc[movie_name].values.reshape(1,-1)

    distances, indices = model.kneighbors(movie_vector)

    recommendations = []

    for i in range(1, len(distances[0])):

        recommended_movie = user_movie_matrix.index[indices[0][i]]

        similarity = 1 - distances[0][i]

        genre = movie_genres.get(recommended_movie,"Unknown")
        genre = genre.replace("|"," • ")

        poster = get_poster(recommended_movie)

        print(recommended_movie)
        print(poster)

        recommendations.append({
            "title": recommended_movie,
            "genre": genre,
            "match": round(similarity * 100, 1),
            "poster": poster
        })

    return recommendations