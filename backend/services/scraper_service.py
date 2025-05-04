import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FootballScraper:
    def __init__(self):
        self.base_url = 'https://m.flashscore.co.ke'
        # Rotating user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        ]
        self.session = self._create_session()
    
    def _create_session(self):
        """Create a session with randomized headers to avoid detection"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        return session
    
    def _random_delay(self, min_seconds=1, max_seconds=5):
        """Add a random delay between requests to avoid detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def get_upcoming_matches(self):
        """Scrape upcoming matches for the next 48 hours"""
        try:
            # Refresh session every time to get new headers
            self.session = self._create_session()
            
            # Get the main page
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            matches = []
            
            # Parse matches from the page
            # This is a simplified example and would need to be adjusted based on actual HTML structure
            for match_elem in soup.select('.event__match'):
                try:
                    league_elem = match_elem.find_previous('.event__title')
                    league_name = league_elem.text.strip() if league_elem else 'Unknown League'
                    
                    home_team_elem = match_elem.select_one('.event__participant--home')
                    away_team_elem = match_elem.select_one('.event__participant--away')
                    time_elem = match_elem.select_one('.event__time')
                    
                    match_id = match_elem.get('id', '').replace('g_1_', '')
                    
                    # Get team details including logos and form
                    home_team_name = home_team_elem.text.strip() if home_team_elem else 'Unknown'
                    away_team_name = away_team_elem.text.strip() if away_team_elem else 'Unknown'
                    
                    self._random_delay()
                    home_team_details = self._get_team_details(home_team_name)
                    
                    self._random_delay()
                    away_team_details = self._get_team_details(away_team_name)
                    
                    # Format match time
                    match_time_text = time_elem.text.strip() if time_elem else '00:00'
                    match_time = self._parse_match_time(match_time_text)
                    
                    match = {
                        'id': match_id,
                        'competition': {'name': league_name, 'code': ''},
                        'homeTeam': home_team_details,
                        'awayTeam': away_team_details,
                        'matchTime': match_time.isoformat(),
                        'status': 'SCHEDULED'
                    }
                    
                    matches.append(match)
                except Exception as e:
                    logger.error(f"Error processing match element: {str(e)}")
            
            return matches
        except Exception as e:
            logger.error(f"Error scraping upcoming matches: {str(e)}")
            return []
    
    def _get_team_details(self, team_name):
        """Get team logo and last 5 results"""
        try:
            # This would implement the actual scraping logic for team details
            # For demo purposes, returning mock data
            
            # In a real implementation, you would:
            # 1. Search for the team page
            # 2. Extract the team logo
            # 3. Navigate to the results page
            # 4. Parse the last 5 match results
            
            # Mock data
            last_five = random.choices(['W', 'L', 'D'], k=5)
            
            return {
                'name': team_name,
                'logo': '',  # In real implementation, this would have the actual logo URL
                'lastFiveMatches': last_five
            }
        except Exception as e:
            logger.error(f"Error getting team details: {str(e)}")
            return {'name': team_name, 'logo': '', 'lastFiveMatches': []}
    
    def _parse_match_time(self, time_text):
        """Parse match time string into datetime object"""
        try:
            now = datetime.now()
            
            # If time format is HH:MM
            if ':' in time_text:
                hour, minute = map(int, time_text.split(':'))
                match_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time is in the past, assume it's for tomorrow
                if match_time < now:
                    match_time += timedelta(days=1)
            else:
                # Default to 24 hours from now if can't parse
                match_time = now + timedelta(hours=24)
                
            return match_time
        except Exception as e:
            logger.error(f"Error parsing match time '{time_text}': {str(e)}")
            return datetime.now() + timedelta(hours=24)
