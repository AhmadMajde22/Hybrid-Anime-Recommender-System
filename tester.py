from utils.helpers import *
from config.path_config import *
from pipeline.prediction_pipeline import hybrid_recommendation_system


# similar_users = find_similar_users(11880,USER_WEIGHTS_PATH,USER2USER_ENCODED,USER2USER_DECODED)

# user_pref = get_user_preferences(11880,RATING_DF,DF)

# similar_animes = find_similar_animes("Dragon Ball Z",ANIME_WEIGHTS_PATH,ANIME2ANIME_ENCODED,ANIME2ANIME_DECODED,DF)

# user_recommendation = get_user_recommendations(
#     similar_users=similar_users,
#     user_pref=user_pref,
#     path_anime_df=DF,
#     path_synopsis_df=SYNOPSIS_DF,
#     path_rating_df=RATING_DF
# )
# print(user_recommendation)

rec = hybrid_recommendation_system(11880)
print(rec)
