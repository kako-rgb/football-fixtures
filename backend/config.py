import os

class Config:
    # API configuration
    USE_API = os.environ.get('USE_API', 'True') == 'True'
    API_KEY = os.environ.get('FOOTBALL_API_KEY', 'your_default_api_key')
    API_BASE_URL = 'https://api.football-data.org/v4'
    
    # App configuration
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Data update frequency
    UPDATE_INTERVAL = 24  # hours
    
    # Temporary file storage
    TEMP_FOLDER = os.environ.get('TEMP_FOLDER', '/tmp')
    
    # Anti-bot detection
    USE_ROTATING_PROXIES = os.environ.get('USE_PROXIES', 'False') == 'True'
    RANDOM_DELAY_MIN = 1  # seconds
    RANDOM_DELAY_MAX = 3  # seconds
