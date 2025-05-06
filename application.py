from flask import Flask, render_template, request
from pipeline.prediction_pipeline import hybrid_recommendation_system
from utils.db_utils import get_recommendations_from_db, save_recommendations_to_db

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = None
    error_message = None

    if request.method == 'POST':
        try:
            user_id = int(request.form["userID"])
            recommendations = get_recommendations_from_db(user_id)

            if recommendations is None:
                recommendations = hybrid_recommendation_system(user_id)

                if not recommendations:
                    error_message = f"User ID {user_id} not found or has no recommendations."
                else:
                    save_recommendations_to_db(user_id, recommendations)

        except ValueError:
            error_message = "Invalid input. Please enter a valid User ID."
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"

    return render_template('index.html', recommendations=recommendations, error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
