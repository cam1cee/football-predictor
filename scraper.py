"""
SoccerStats.com Web Scraper
Collects historical match data for Serie A, Serie B, and La Liga

Usage:
    python scraper.py --league seria_a --seasons 3
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
from datetime import datetime
import os

class SoccerStatsScraper:
    def __init__(self):
        self.base_url = "https://www.soccerstats.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.delay = 2  # Seconds between requests (be respectful!)
        
    def get_league_url(self, league, season):
        """
        Get the URL for a specific league and season
        Note: You'll need to verify these URLs on SoccerStats.com
        """
        league_codes = {
            'seria_a': 'italy1',
            'serie_b': 'italy2', 
            'laliga': 'spain1'
        }
        
        code = league_codes.get(league)
        if not code:
            raise ValueError(f"Unknown league: {league}")
            
        # Example URL structure (verify on actual site)
        return f"{self.base_url}/results.asp?league={code}&pmtype=bydate"
    
    def scrape_matches(self, league, seasons=3):
        """
        Scrape match results for specified league and number of seasons
        
        Returns:
            DataFrame with columns: date, home_team, away_team, home_goals, away_goals, season
        """
        all_matches = []
        current_year = datetime.now().year
        
        print(f"🔍 Scraping {league.upper()} data...")
        print(f"📅 Seasons: {seasons} (this is a template - adapt to actual SoccerStats structure)")
        
        for season_offset in range(seasons):
            season_year = current_year - season_offset
            print(f"\n⚽ Processing {season_year-1}/{season_year} season...")
            
            try:
                # Get league page
                url = self.get_league_url(league, season_year)
                print(f"🌐 Fetching: {url}")
                
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # TODO: Adapt these selectors to actual SoccerStats HTML structure
                # This is a TEMPLATE - you need to inspect the actual site
                
                # Example: Find match result tables
                match_tables = soup.find_all('table', class_='matches')  # Adjust selector
                
                matches_this_season = 0
                
                for table in match_tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) >= 5:  # Adjust based on actual structure
                            try:
                                match_data = {
                                    'date': cells[0].text.strip(),
                                    'home_team': cells[1].text.strip(),
                                    'score': cells[2].text.strip(),  # e.g., "2-1"
                                    'away_team': cells[3].text.strip(),
                                    'season': f"{season_year-1}/{season_year}",
                                    'league': league
                                }
                                
                                # Parse score
                                if '-' in match_data['score']:
                                    home_goals, away_goals = match_data['score'].split('-')
                                    match_data['home_goals'] = int(home_goals.strip())
                                    match_data['away_goals'] = int(away_goals.strip())
                                    
                                    all_matches.append(match_data)
                                    matches_this_season += 1
                                    
                            except Exception as e:
                                print(f"⚠️ Error parsing row: {e}")
                                continue
                
                print(f"✅ Found {matches_this_season} matches")
                
                # Be respectful - delay between requests
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"❌ Error scraping season {season_year}: {e}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(all_matches)
        
        if not df.empty:
            # Clean and standardize
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['home_goals', 'away_goals'])
            df = df.sort_values('date')
            
        print(f"\n✨ Total matches collected: {len(df)}")
        return df
    
    def save_data(self, df, league, output_dir='data/raw'):
        """Save scraped data to CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/{league}_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        
        print(f"💾 Data saved to: {filename}")
        return filename

def create_sample_data(league, num_matches=100):
    """
    Create sample/demo data for testing
    Use this while you're setting up the real scraper
    """
    print(f"🎲 Generating {num_matches} sample matches for {league}...")
    
    teams = {
        'seria_a': ["AC Milan", "Inter Milan", "Juventus", "Napoli", "AS Roma", 
                    "Lazio", "Atalanta", "Fiorentina", "Bologna", "Torino"],
        'serie_b': ["Parma", "Como", "Venezia", "Cremonese", "Catanzaro",
                    "Palermo", "Brescia", "Sampdoria", "Pisa", "Spezia"],
        'laliga': ["Real Madrid", "Barcelona", "Atlético Madrid", "Real Sociedad",
                   "Athletic Bilbao", "Real Betis", "Villarreal", "Valencia"]
    }
    
    import numpy as np
    
    matches = []
    for i in range(num_matches):
        home_team = np.random.choice(teams[league])
        away_team = np.random.choice([t for t in teams[league] if t != home_team])
        
        # Simulate realistic scores
        home_goals = np.random.poisson(1.5)
        away_goals = np.random.poisson(1.2)
        
        matches.append({
            'date': pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(1, 365)),
            'home_team': home_team,
            'away_team': away_team,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'season': '2023/2024',
            'league': league
        })
    
    df = pd.DataFrame(matches)
    df = df.sort_values('date')
    
    print(f"✅ Sample data created!")
    return df

def main():
    parser = argparse.ArgumentParser(description='Scrape football match data from SoccerStats')
    parser.add_argument('--league', type=str, required=True, 
                       choices=['seria_a', 'serie_b', 'laliga'],
                       help='League to scrape')
    parser.add_argument('--seasons', type=int, default=3,
                       help='Number of seasons to scrape')
    parser.add_argument('--demo', action='store_true',
                       help='Generate demo data instead of scraping')
    
    args = parser.parse_args()
    
    if args.demo:
        # Create sample data for testing
        df = create_sample_data(args.league, num_matches=200)
    else:
        # Real scraping
        print("⚠️ IMPORTANT: Before running this scraper:")
        print("1. Check SoccerStats.com Terms of Service")
        print("2. Inspect the actual HTML structure of the site")
        print("3. Update the CSS selectors in scrape_matches()")
        print("4. Test with small requests first")
        print("\nThis is a TEMPLATE that needs customization!\n")
        
        scraper = SoccerStatsScraper()
        df = scraper.scrape_matches(args.league, args.seasons)
    
    if not df.empty:
        # Save data
        scraper = SoccerStatsScraper()
        scraper.save_data(df, args.league)
        
        # Show preview
        print("\n📊 Data Preview:")
        print(df.head(10))
        print("\n📈 Summary:")
        print(df.describe())
    else:
        print("❌ No data collected")

if __name__ == "__main__":
    main()
