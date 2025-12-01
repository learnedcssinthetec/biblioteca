from flask import Flask
from concurrent.futures import ThreadPoolExecutor
import os
from extensions import db

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Create a thread pool for model predictions and store it in the app config
    app.config['EXECUTOR'] = ThreadPoolExecutor(max_workers=5)
    
    with app.app_context():
        # Import and register blueprints
        # Deferring this import is key to avoiding circular dependencies
        from routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        # Create database tables
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
