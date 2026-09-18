from flask import Flask
from config import Config
from models.db import db
from services.parking_service import seed_default_data
from routes import auth_bp, api_bp, admin_bp, views_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # Create tables & seed data on startup
    with app.app_context():
        db.create_all()
        seed_default_data()

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  SMART PARKING - Smart Mall Parking Reservation System")
    print("  Starting Flask Server...")
    print("  URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
