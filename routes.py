from flask import Blueprint, render_template, request, jsonify, current_app
from models import Prediction
from extensions import db
from collections import Counter
from ml_model import DummyModel

main = Blueprint('main', __name__)

# Instantiate the model directly
model = DummyModel()

def predict_genre_for_age(age):
    # Predict for a single age
    prediction = model.predict([[age]])
    return prediction[0]

@main.route('/')
def index():
    predictions = Prediction.query.order_by(Prediction.timestamp.desc()).all()
    genre_counts = Counter(p.predicted_genre for p in predictions)
    popular_genres = genre_counts.most_common(5)
    return render_template('index.html', predictions=predictions, popular_genres=popular_genres)

@main.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    ages = data.get('ages', [])

    if not ages:
        return jsonify({'error': 'No se proporcionaron edades'}), 400

    # Use the executor from the app config to predict for all ages in parallel
    executor = current_app.config['EXECUTOR']
    futures = [executor.submit(predict_genre_for_age, age) for age in ages]
    predicted_genres = [future.result() for future in futures]

    # Save each individual prediction to the database
    for age, genre in zip(ages, predicted_genres):
        new_prediction = Prediction(age=age, predicted_genre=genre)
        db.session.add(new_prediction)
    db.session.commit()

    # Find the most common genre from the predictions
    if not predicted_genres:
        return jsonify({'most_popular_genre': 'No hay suficientes datos'})

    genre_counts = Counter(predicted_genres)
    most_popular_genre = genre_counts.most_common(1)[0][0]
    
    return jsonify({'most_popular_genre': most_popular_genre})
