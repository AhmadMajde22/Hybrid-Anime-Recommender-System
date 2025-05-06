import pandas as pd
import numpy as np
import joblib
from config.path_config import *

# GET ANIME FRAME

def get_anime_frame(anime, path_df):
    df = pd.read_csv(path_df)
    if isinstance(anime, int):
        return df[df["anime_id"] == anime]
    elif isinstance(anime, str):
        return df[df["eng_version"] == anime]
    return pd.DataFrame()  # Return an empty DataFrame if the anime is neither int nor str


# GET SYNOPSIS

def get_synopsis(anime, path_synopsis_df):
    synopsis_df = pd.read_csv(path_synopsis_df)
    try:
        if isinstance(anime, int):
            return synopsis_df[synopsis_df["MAL_ID"] == anime]["sypnopsis"].values[0]
        elif isinstance(anime, str):
            return synopsis_df[synopsis_df["Name"] == anime]["sypnopsis"].values[0]
    except IndexError:
        return None  # Return None if there's no matching synopsis


# CONTENT RECOMMENDATION

def find_similar_animes(name, path_anime_weights, path_anime2anime_encoded, path_anime2anime_decoded,
                        path_anime_df, n=10, return_dist=False, neg=False):
    anime_weights = joblib.load(path_anime_weights)
    anime2anime_encoded = joblib.load(path_anime2anime_encoded)
    anime2anime_decoded = joblib.load(path_anime2anime_decoded)

    try:
        # Get anime ID from name
        anime_frame = get_anime_frame(name, path_anime_df)
        if anime_frame.empty:
            print(f"Error: Anime '{name}' not found in database")
            return None

        index = anime_frame["anime_id"].values[0]  # type: ignore
        encoded_index = anime2anime_encoded.get(index)
        if encoded_index is None:
            print(f"Error: Anime ID {index} not found in encoded mapping")
            return None

        # Calculate similarities
        dists = np.dot(anime_weights, anime_weights[encoded_index])
        sorted_dists = np.argsort(dists)

        n += 1
        closest = sorted_dists[:n] if neg else sorted_dists[-n:]

        if return_dist:
            return dists, closest

        # Build similarity array
        SimilarityArr = []
        for close in closest:
            try:
                decoded_id = anime2anime_decoded.get(close)
                if decoded_id is None:
                    continue

                anime_frame = get_anime_frame(decoded_id, path_anime_df)
                if anime_frame.empty:
                    continue

                anime_name = anime_frame["eng_version"].values[0]  # type: ignore
                genre = anime_frame["Genres"].values[0]  # type: ignore
                similarity = dists[close]

                SimilarityArr.append({
                    "anime_id": decoded_id,
                    "anime_name": anime_name,
                    "similarity": similarity,
                    "genre": genre
                })
            except Exception as e:
                print(f"Error while processing similar anime: {str(e)}")
                continue

        if not SimilarityArr:
            print("Error: No similar animes found")
            return None

        Frame = pd.DataFrame(SimilarityArr)
        Frame = Frame.sort_values(by=["similarity"], ascending=False)
        return Frame[Frame["anime_id"] != index].drop(["anime_id"], axis=1)

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


# FIND SIMILAR USERS

def find_similar_users(item_input, path_user_weights, path_user2user_encoded,
                       path_user2user_decoded, n=10, return_dist=False, neg=False):
    user_weights = joblib.load(path_user_weights)
    user2user_encoded = joblib.load(path_user2user_encoded)
    user2user_decoded = joblib.load(path_user2user_decoded)

    try:
        # Get encoded index for input user
        encoded_index = user2user_encoded.get(item_input)
        if encoded_index is None:
            print(f"Error: User '{item_input}' not found in encoded mapping")
            return None

        # Calculate similarities
        dists = np.dot(user_weights, user_weights[encoded_index])
        sorted_dists = np.argsort(dists)

        # Get n closest users
        n += 1  # Add 1 to include the input user
        closest = sorted_dists[:n] if neg else sorted_dists[-n:]  # Sort based on neg parameter

        if return_dist:
            return dists, closest

        # Build similarity array
        SimilarityArr = []
        for close in closest:
            similarity = dists[close]
            decoded_id = user2user_decoded.get(close)
            if decoded_id is not None:
                SimilarityArr.append({
                    "user_id": decoded_id,
                    "similarity": similarity
                })

        # Create and sort DataFrame
        similar_users = pd.DataFrame(SimilarityArr)
        similar_users = similar_users.sort_values(by=["similarity"], ascending=False)

        # Remove the input user and return
        return similar_users[similar_users["user_id"] != item_input]

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


# USER PREFERENCES

def get_user_preferences(user_id, path_rating_df, path_anime_df, verbose=0, plot=False):
    rating_df = pd.read_csv(path_rating_df)
    df = pd.read_csv(path_anime_df)

    try:
        # Get all animes watched by user
        animes_watched_by_user = rating_df[rating_df["user_id"] == user_id]

        if verbose:
            print(f"User {user_id} has watched {len(animes_watched_by_user)} animes")

        if len(animes_watched_by_user) == 0:
            print(f"Error: User {user_id} has not watched any animes")
            return None

        # Get top rated animes (75th percentile)
        user_rating_perctile = np.percentile(animes_watched_by_user["rating"], 75)
        top_rated_animes = animes_watched_by_user[animes_watched_by_user["rating"] >= user_rating_perctile]

        if verbose:
            print(f"Found {len(top_rated_animes)} top rated animes")

        # Get anime details
        top_anime_ids = top_rated_animes.sort_values(by="rating", ascending=False)["anime_id"].values
        anime_df_rows = df[df["anime_id"].isin(top_anime_ids)]
        anime_df_rows = anime_df_rows[["eng_version", "Genres"]]

        return anime_df_rows

    except Exception as e:
        print(f"Error getting user preferences: {str(e)}")
        return None


# GET USER RECOMMENDATION

def get_user_recommendations(similar_users, user_pref, path_anime_df, path_synopsis_df, path_rating_df, n=10):
    recommended_animes = []
    anime_list = []

    for user_id in similar_users.user_id.values:
        pref_list = get_user_preferences(int(user_id), path_rating_df, path_anime_df)
        if pref_list is not None:
            pref_list = pref_list[~pref_list.eng_version.isin(user_pref.eng_version.values)]  # type: ignore
            if not pref_list.empty:
                anime_list.append(pref_list.eng_version.values)

    if anime_list:
        # Flatten and count frequency
        flat_anime_list = [anime for sublist in anime_list for anime in sublist]
        sorted_list = pd.Series(flat_anime_list).value_counts().head(n)

        for anime_name, n_users_pref in sorted_list.items():
            if isinstance(anime_name, str):
                frame = get_anime_frame(anime_name, path_anime_df)
                if not frame.empty:
                    anime_id = frame.anime_id.values[0]
                    genre = frame.Genres.values[0]
                    synopsis = get_synopsis(int(anime_id), path_synopsis_df)
                    recommended_animes.append({
                        "n": n_users_pref,
                        "anime_name": anime_name,
                        "Genres": genre,
                        "synopsis": synopsis,
                    })

        return pd.DataFrame(recommended_animes).head(n)
    else:
        return pd.DataFrame(columns=["n", "anime_name", "Genres", "synopsis"])
