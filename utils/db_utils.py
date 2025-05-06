import psycopg2
from datetime import datetime
from config.db_config import DB_CONFIG

# Function to retrieve recommendations from the database
def get_recommendations_from_db(user_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        select_query = """
        SELECT recommended_animes, timestamp
        FROM user_recommendations
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 1;
        """
        cur.execute(select_query, (user_id,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if result is None:
            return None
        else:
            return result[0]  # Return the recommendations as a list (already in TEXT or JSON format)
    except Exception as e:
        print(f"Error retrieving recommendations: {e}")
        return None

# Function to save recommendations to the database
def save_recommendations_to_db(user_id, recommendations):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Insert query to save recommendations for the user
        insert_query = """
        INSERT INTO user_recommendations (user_id, recommended_animes, timestamp)
        VALUES (%s, %s, %s)
        """
        cur.execute(insert_query, (
            user_id,
            recommendations,  # This should be a list of recommended anime names
            datetime.now()  # Current timestamp
        ))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Recommendations saved to DB for user {user_id}")
    except Exception as e:
        print(f"Failed to save recommendations: {e}")
