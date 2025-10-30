# tools/sports_scores.py
from semantic_kernel.functions import kernel_function
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class SportsScoresTools:
    @kernel_function(name="get_sports_scores", description="Get recent sports scores for various leagues and teams")
    def get_sports_scores(self, league: str = "NBA", team: str = None, days_back: int = 1):
        """
        Get recent sports scores for various leagues and teams.
        
        Args:
            league: The sports league (NBA, NFL, MLB, NHL, Premier League, etc.)
            team: Optional team name to filter results
            days_back: Number of days back to look for games (default: 1)
            
        Returns:
            Dictionary containing sports scores information
        """
        try:
            logger.info(f"Getting sports scores for league: {league}, team: {team}, days_back: {days_back}")
            
            # Mock sports data - in a real application, this would query a sports API
            mock_scores = {
                "NBA": [
                    {
                        "game_id": "NBA-001",
                        "date": "2024-01-15",
                        "home_team": "Los Angeles Lakers",
                        "away_team": "Boston Celtics",
                        "home_score": 112,
                        "away_score": 108,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "Crypto.com Arena",
                        "attendance": 18997
                    },
                    {
                        "game_id": "NBA-002", 
                        "date": "2024-01-15",
                        "home_team": "Golden State Warriors",
                        "away_team": "Miami Heat",
                        "home_score": 98,
                        "away_score": 105,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "Chase Center",
                        "attendance": 18064
                    },
                    {
                        "game_id": "NBA-003",
                        "date": "2024-01-15",
                        "home_team": "Chicago Bulls",
                        "away_team": "New York Knicks",
                        "home_score": 89,
                        "away_score": 87,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "United Center",
                        "attendance": 20917
                    },
                    {
                        "game_id": "NBA-004",
                        "date": "2024-01-16",
                        "home_team": "Dallas Mavericks",
                        "away_team": "Phoenix Suns",
                        "home_score": 95,
                        "away_score": 98,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "American Airlines Center",
                        "attendance": 19200
                    }
                ],
                "NFL": [
                    {
                        "game_id": "NFL-001",
                        "date": "2024-01-14",
                        "home_team": "Kansas City Chiefs",
                        "away_team": "Buffalo Bills",
                        "home_score": 27,
                        "away_score": 24,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "Arrowhead Stadium",
                        "attendance": 76416
                    },
                    {
                        "game_id": "NFL-002",
                        "date": "2024-01-14", 
                        "home_team": "San Francisco 49ers",
                        "away_team": "Dallas Cowboys",
                        "home_score": 31,
                        "away_score": 28,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "Levi's Stadium",
                        "attendance": 71599
                    },
                    {
                        "game_id": "NFL-003",
                        "date": "2024-01-15",
                        "home_team": "Tampa Bay Buccaneers",
                        "away_team": "Philadelphia Eagles",
                        "home_score": 32,
                        "away_score": 9,
                        "status": "final",
                        "quarter": "4th",
                        "time_remaining": "0:00",
                        "venue": "Raymond James Stadium",
                        "attendance": 65878
                    }
                ],
                "MLB": [
                    {
                        "game_id": "MLB-001",
                        "date": "2024-01-15",
                        "home_team": "New York Yankees",
                        "away_team": "Boston Red Sox",
                        "home_score": 6,
                        "away_score": 4,
                        "status": "final",
                        "inning": "9th",
                        "time_remaining": "0:00",
                        "venue": "Yankee Stadium",
                        "attendance": 47629
                    },
                    {
                        "game_id": "MLB-002",
                        "date": "2024-01-15",
                        "home_team": "Los Angeles Dodgers",
                        "away_team": "San Francisco Giants",
                        "home_score": 8,
                        "away_score": 3,
                        "status": "final",
                        "inning": "9th",
                        "time_remaining": "0:00",
                        "venue": "Dodger Stadium",
                        "attendance": 52000
                    }
                ],
                "NHL": [
                    {
                        "game_id": "NHL-001",
                        "date": "2024-01-15",
                        "home_team": "Toronto Maple Leafs",
                        "away_team": "Montreal Canadiens",
                        "home_score": 4,
                        "away_score": 2,
                        "status": "final",
                        "period": "3rd",
                        "time_remaining": "0:00",
                        "venue": "Scotiabank Arena",
                        "attendance": 19800
                    },
                    {
                        "game_id": "NHL-002",
                        "date": "2024-01-15",
                        "home_team": "Boston Bruins",
                        "away_team": "New York Rangers",
                        "home_score": 3,
                        "away_score": 1,
                        "status": "final",
                        "period": "3rd",
                        "time_remaining": "0:00",
                        "venue": "TD Garden",
                        "attendance": 17565
                    }
                ],
                "Premier League": [
                    {
                        "game_id": "EPL-001",
                        "date": "2024-01-15",
                        "home_team": "Manchester United",
                        "away_team": "Liverpool",
                        "home_score": 2,
                        "away_score": 1,
                        "status": "final",
                        "minute": "90+3",
                        "time_remaining": "0:00",
                        "venue": "Old Trafford",
                        "attendance": 74310
                    },
                    {
                        "game_id": "EPL-002",
                        "date": "2024-01-15",
                        "home_team": "Arsenal",
                        "away_team": "Chelsea",
                        "home_score": 3,
                        "away_score": 0,
                        "status": "final",
                        "minute": "90",
                        "time_remaining": "0:00",
                        "venue": "Emirates Stadium",
                        "attendance": 60260
                    }
                ]
            }
            
            # Get scores for the specified league
            if league.upper() in mock_scores:
                league_scores = mock_scores[league.upper()]
                
                # Filter by team if specified
                if team:
                    filtered_scores = []
                    for game in league_scores:
                        if team.lower() in game["home_team"].lower() or team.lower() in game["away_team"].lower():
                            filtered_scores.append(game)
                    league_scores = filtered_scores
                
                return {
                    "league": league.upper(),
                    "team_filter": team,
                    "days_back": days_back,
                    "games": league_scores,
                    "total_games": len(league_scores)
                }
            else:
                return {
                    "league": league.upper(),
                    "team_filter": team,
                    "days_back": days_back,
                    "games": [],
                    "total_games": 0,
                    "message": f"No data available for league: {league}"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get sports scores: {e}")
            return {
                "league": league,
                "team_filter": team,
                "days_back": days_back,
                "games": [],
                "total_games": 0,
                "message": f"Error retrieving sports scores: {e}"
            }
