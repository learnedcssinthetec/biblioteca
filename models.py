from extensions import db
import datetime

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    age = db.Column(db.Integer, nullable=False)
    predicted_genre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Prediction {self.id}: {self.age} -> {self.predicted_genre}>'
