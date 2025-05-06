import psycopg2
from datetime import datetime
from config.db_config import DB_CONFIG  # Assuming this is where DB_CONFIG is stored

def save_recommendations_to_db(user_id, recommendations):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        insert_query = """
        INSERT INTO user_recommendations (user_id, recommended_animes, created_at)
        VALUES (%s, %s, %s)
        """
        cur.execute(insert_query, (
            user_id,
            recommendations,  # This should be a Python list
            datetime.now()
        ))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Recommendations saved to DB for user {user_id}")
    except Exception as e:
        print(f"Failed to save recommendations: {e}")
