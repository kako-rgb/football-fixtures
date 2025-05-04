import csv
import os
import pandas as pd
from datetime import datetime
import logging

from config import Config

logger = logging.getLogger(__name__)

def generate_csv(matches):
    """
    Generate a CSV file from matches data
    Returns the path to the generated CSV file
    """
    try:
        csv_data = []
        
        for match in matches:
            home_team = match.get('homeTeam', {})
            away_team = match.get('awayTeam', {})
            competition = match.get('competition', {})
            
            # Format match time
            match_time = match.get('matchTime', '')
            if match_time:
                try:
                    dt = datetime.fromisoformat(match_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = match_time
            else:
                formatted_time = 'Unknown'
            
            # Format team form
            home_form = ''.join(home_team.get('lastFiveMatches', []))
            away_form = ''.join(away_team.get('lastFiveMatches', []))
            
            row = {
                'Match ID': match.get('id', ''),
                'Competition': competition.get('name', ''),
                'Home Team': home_team.get('name', ''),
                'Away Team': away_team.get('name', ''),
                'Match Time': formatted_time,
                'Home Team Form': home_form,
                'Away Team Form': away_form
            }
            
            csv_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(csv_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(Config.TEMP_FOLDER, f'football_matches_{timestamp}.csv')
        
        # Write to CSV
        df.to_csv(filename, index=False)
        
        return filename
    except Exception as e:
        logger.error(f"Error generating CSV: {str(e)}")
        raise
