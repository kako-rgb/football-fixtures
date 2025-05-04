from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from services.data_service import DataService
from utils.csv_generator import generate_csv

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)

# Initialize services
data_service = DataService(app.config['USE_API'], app.config['API_KEY'])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure scheduler for daily updates
scheduler = BackgroundScheduler()
scheduler.add_job(data_service.update_match_data, 'interval', 
                 hours=24, 
                 start_date='2025-05-05 00:00:00')
scheduler.start()

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get upcoming matches for the next 48 hours"""
    try:
        matches = data_service.get_matches()
        return jsonify(matches)
    except Exception as e:
        logger.error(f"Error fetching matches: {str(e)}")
        return jsonify({"error": "Failed to fetch matches"}), 500

@app.route('/api/matches/csv', methods=['GET'])
def download_matches_csv():
    """Download matches data as CSV"""
    try:
        matches = data_service.get_matches()
        csv_path = generate_csv(matches)
        return send_file(csv_path, as_attachment=True, 
                        download_name='upcoming_matches.csv')
    except Exception as e:
        logger.error(f"Error generating CSV: {str(e)}")
        return jsonify({"error": "Failed to generate CSV"}), 500

@app.route('/', methods=['GET'])
def index():
    """Serve the main page"""
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # Initial data fetch
    data_service.update_match_data()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=app.config['PORT'])
