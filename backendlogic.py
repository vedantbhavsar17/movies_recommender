"""Load and use the compact movie recommender artifacts."""

from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"
movies_df = pd.read_csv(DATA_DIR / "df_model.csv")
ranked_matches = np.load(DATA_DIR / "similarity_top100.npz")
ranked_indices = ranked_matches["indices"]
ranked_scores = ranked_matches["scores"]


def _recommend_movie(title, movies_df, n=5):
    title_key = title.strip().casefold()
    matches = movies_df.index[
        movies_df["title"].fillna("").str.strip().str.casefold() == title_key
    ].tolist()

    if not matches:
        raise LookupError(f'"{title.strip()}" was not found. Please choose a title from the list.')

    movie_index = matches[0]
    recommendations = []
    seen_titles = {title_key}

    for index, score in zip(
        ranked_indices[movie_index], ranked_scores[movie_index]
    ):
        movie = movies_df.iloc[int(index)]
        movie_title = str(movie["title"]).strip()
        if movie_title.casefold() in seen_titles:
            continue

        seen_titles.add(movie_title.casefold())
        duration = movie.get("duration")
        recommendations.append(
            {
                "title": movie_title,
                "release_year": int(movie["release_year"])
                if pd.notna(movie.get("release_year")) else None,
                "type": "TV Show" if movie.get("type_TV Show", 0) else "Movie",
                "duration": int(duration) if pd.notna(duration) else None,
                "description": str(movie.get("description", "")).strip(),
                "score": round(float(score) * 100, 1),
            }
        )
        if len(recommendations) == n:
            break

    return recommendations


def get_movie_titles():
    return movies_df["title"].dropna().drop_duplicates().sort_values().tolist()


def recommend_movie(title, n=5):
    if not title or not title.strip():
        raise ValueError("Please enter a movie or series title.")
    if n < 1:
        return []
    if n > ranked_indices.shape[1] - 1:
        raise ValueError(f"A maximum of {ranked_indices.shape[1] - 1} recommendations is supported.")
    return _recommend_movie(title, movies_df, n)
