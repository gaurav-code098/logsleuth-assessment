import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from flask import Flask, jsonify
from flask_cors import CORS
from app.database import engine, Base
from app.routes import api_blueprint

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# Enable CORS for the Vercel frontend and local testing
CORS(app, resources={r"/api/*": {"origins": ["https://logsleuth.vercel.app", "http://localhost:5173"]}}, supports_credentials=True)

# Register the routes from routes.py
app.register_blueprint(api_blueprint, url_prefix="/api")

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "database": "connected"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
