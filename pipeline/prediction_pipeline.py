from config.path_config import *
from utils.helpers import *


def hybrid_recommendation_system(user_id, user_weight=0.5, content_weight=0.5, top_n=10):
    """
    Hybrid recommendation system combining user-based and content-based recommendations.

    Args:
        user_id (int): The user ID to get recommendations for.
        user_weight (float): Weight for user-based recommendations.
        content_weight (float): Weight for content-based recommendations.
        top_n (int): Number of top recommendations to return.

    Returns:
        List[str]: Top-N recommended anime names.
    """
    similar_users =find_similar_users(user_id,USER_WEIGHTS_PATH,USER2USER_ENCODED,USER2USER_DECODED)
    user_pref = get_user_preferences(user_id,RATING_DF, DF)
    user_recommended_animes =get_user_recommendations(similar_users,user_pref,DF, SYNOPSIS_DF,RATING_DF)
    user_recommended_anime_list = user_recommended_animes["anime_name"].tolist()

    # Content-based recommendations
    content_recommended_animes = []


    for anime in user_recommended_anime_list:
        similar_animes = find_similar_animes(anime, ANIME_WEIGHTS_PATH, ANIME2ANIME_ENCODED, ANIME2ANIME_DECODED, DF)

        if similar_animes is not None and not similar_animes.empty:
            content_recommended_animes.extend(similar_animes["anime_name"].tolist())
        else:
            print(f"No similar anime found {anime}")

    combined_scores = {}

    for anime in user_recommended_anime_list:
        combined_scores[anime] = combined_scores.get(anime,0) + user_weight

    for anime in content_recommended_animes:
        combined_scores[anime] = combined_scores.get(anime,0) + content_weight

    sorted_animes = sorted(combined_scores.items() , key=lambda x:x[1] , reverse=True)

    return [anime for anime , score in sorted_animes[:10]]
