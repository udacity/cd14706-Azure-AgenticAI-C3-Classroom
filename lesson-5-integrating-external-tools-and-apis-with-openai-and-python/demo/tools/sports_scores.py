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
                        "status": "Final",
                        "quarter": "4th",
                        "time_remaining": "0:00"
                    },
                    {
                        "game_id": "NBA-002", 
                        "date": "2024-01-15",
                        "home_team": "Golden State Warriors",
                        "away_team": "Miami Heat",
                        "home_score": 98,
                        "away_score": 105,
                        "status": "Final",
                        "quarter": "4th",
                        "time_remaining": "0:00"
                    },
                    {
                        "game_id": "NBA-003",
                        "date": "2024-01-15",
                        "home_team": "Chicago Bulls",
                        "away_team": "New York Knicks",
                        "home_score": 89,
                        "away_score": 87,
                        "status": "Final",
                        "quarter": "4th",
                        "time_remaining": "0:00"
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
                        "status": "Final",
                        "quarter": "4th",
                        "time_remaining": "0:00"
                    },
                    {
                        "game_id": "NFL-002",
                        "date": "2024-01-14", 
                        "home_team": "San Francisco 49ers",
                        "away_team": "Dallas Cowboys",
                        "home_score": 31,
                        "away_score": 28,
                        "status": "Final",
                        "quarter": "4th",
                        "time_remaining": "0:00"
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
                        "status": "Final",
                        "inning": "9th",
                        "inning_half": "Bottom"
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
                        "status": "Final",
                        "period": "3rd",
                        "time_remaining": "0:00"
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
                        "status": "Full Time",
                        "minute": "90+3"
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
