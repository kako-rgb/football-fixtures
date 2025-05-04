import requests
import random
import time
import logging
from datetime import datetime, timedelta

from services.scraper_service import FootballScraper

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self, use_api=True, api_key=None):
        self.use_api = use_api
        self.api_key = api_key
        self.base_url = 'https://api.football-data.org/v4'
        self.scraper = FootballScraper()
        self.matches_data = []
        self.last_updated = None
        
        # Rotating user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        ]
    
    def _get_headers(self):
        """Generate randomized headers to avoid detection"""
        return {
            'X-Auth-Token': self.api_key,
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache'
        }
    
    def _random_delay(self, min_seconds=1, max_seconds=3):
        """Add a random delay between requests to avoid detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def update_match_data(self):
        """Fetch and update match data"""
        logger.info(f"Updating match data at {datetime.now()}")
        
        try:
            if self.use_api:
                matches = self._fetch_from_api()
            else:
                matches = self._fetch_from_scraper()
                
            self.matches_data = matches
            self.last_updated = datetime.now()
            
            logger.info(f"Successfully updated match data. {len(matches)} matches found.")
        except Exception as e:
            logger.error(f"Failed to update match data: {str(e)}")
    
    def _fetch_from_api(self):
        """Fetch match data from football-data.org API"""
        processed_matches = []
        
        try:
            # Get date range for next 48 hours
            today = datetime.now().strftime('%Y-%m-%d')
            day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            
            # API request for matches
            url = f"{self.base_url}/matches"
            params = {
                'dateFrom': today,
                'dateTo': day_after_tomorrow
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get('matches', [])
            
            # Process each match
            for match in matches:
                home_team = match.get('homeTeam', {})
                away_team = match.get('awayTeam', {})
                competition = match.get('competition', {})
                
                # Add a delay before fetching team details
                self._random_delay()
                
                # Get last 5 matches for home team
                home_form = self._get_team_form(home_team.get('id'))
                
                # Add a delay before next request
                self._random_delay()
                
                # Get last 5 matches for away team
                away_form = self._get_team_form(away_team.get('id'))
                
                processed_match = {
                    'id': match.get('id'),
                    'competition': {
                        'name': competition.get('name', ''),
                        'code': competition.get('code', '')
                    },
                    'homeTeam': {
                        'id': home_team.get('id'),
                        'name': home_team.get('name', ''),
                        'logo': home_team.get('crest', ''),
                        'lastFiveMatches': home_form
                    },
                    'awayTeam': {
                        'id': away_team.get('id'),
                        'name': away_team.get('name', ''),
                        'logo': away_team.get('crest', ''),
                        'lastFiveMatches': away_form
                    },
                    'matchTime': match.get('utcDate', ''),
                    'status': match.get('status', '')
                }
                
                processed_matches.append(processed_match)
            
            return processed_matches
        except Exception as e:
            logger.error(f"API fetch error: {str(e)}")
            return []
    
    def _get_team_form(self, team_id):
        """Get last 5 match results for a team from API"""
        try:
            url = f"{self.base_url}/teams/{team_id}/matches"
            params = {
                'status': 'FINISHED',
                'limit': 5
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get('matches', [])
            
            form = []
            for match in matches:
                home_team = match.get('homeTeam', {})
                away_team = match.get('awayTeam', {})
                score = match.get('score', {}).get('fullTime', {})
                
                home_goals = score.get('home')
                away_goals = score.get('away')
                
                if home_goals is None or away_goals is None:
                    continue
                
                if team_id == home_team.get('id'):
                    if home_goals > away_goals:
                        form.append('W')
                    elif home_goals < away_goals:
                        form.append('L')
                    else:
                        form.append('D')
                else:
                    if home_goals < away_goals:
                        form.append('W')
                    elif home_goals > away_goals:
                        form.append('L')
                    else:
                        form.append('D')
            
            return form
        except Exception as e:
            logger.error(f"Error fetching team form: {str(e)}")
            return []
    
    def _fetch_from_scraper(self):
        """Fetch match data using web scraper as fallback"""
        return self.scraper.get_upcoming_matches()
    
    def get_matches(self):
        """Get cached match data"""
        if not self.matches_data or not self.last_updated or \
           (datetime.now() - self.last_updated).total_seconds() > 3600:
            # If no data or data is older than 1 hour, refresh
            self.update_match_data()
        
        return self.matches_data
