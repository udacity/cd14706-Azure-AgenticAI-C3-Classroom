# tools/sports_scores.py - Sports Scores and Game Information Tool

from semantic_kernel.functions import kernel_function
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

class SportsScoresTools:
    """Tools for retrieving sports scores and game information"""
    
    def __init__(self):
        self.mock_games = {
            "lakers_warriors": {
                "game_id": "LAL_GSW_20241215",
                "league": "NBA",
                "date": "2024-12-15",
                "home_team": "Los Angeles Lakers",
                "away_team": "Golden State Warriors",
                "home_score": 120,
                "away_score": 115,
                "status": "final",
                "venue": "Crypto.com Arena",
                "attendance": 19068,
                "highlights": ["LeBron's 30-point game", "Curry's clutch 3-pointer"]
            },
            "celtics_heat": {
                "game_id": "BOS_MIA_20241214",
                "league": "NBA",
                "date": "2024-12-14",
                "home_team": "Boston Celtics",
                "away_team": "Miami Heat",
                "home_score": 108,
                "away_score": 102,
                "status": "final",
                "venue": "TD Garden",
                "attendance": 19156,
                "highlights": ["Tatum's 35-point performance", "Heat's late comeback attempt"]
            },
            "nuggets_suns": {
                "game_id": "DEN_PHX_20241213",
                "league": "NBA",
                "date": "2024-12-13",
                "home_team": "Denver Nuggets",
                "away_team": "Phoenix Suns",
                "home_score": 112,
                "away_score": 105,
                "status": "final",
                "venue": "Ball Arena",
                "attendance": 19520,
                "highlights": ["Jokic's triple-double", "Booker's 40-point game"]
            }
        }
    
    @kernel_function(name="get_game_scores", description="Get scores and information for specific games")
    def get_game_scores(self, team1: str = "", team2: str = "", league: str = "NBA") -> Dict[str, Any]:
        """
        Get game scores and information for specified teams or league.
        
        Args:
            team1: First team name (optional)
            team2: Second team name (optional)
            league: Sports league (default: NBA)
        
        Returns:
            Dictionary containing game information
        """
        try:
            if team1 and team2:
                # Look for specific matchup
                team1_lower = team1.lower()
                team2_lower = team2.lower()
                
                for game_id, game_data in self.mock_games.items():
                    home_lower = game_data["home_team"].lower()
                    away_lower = game_data["away_team"].lower()
                    
                    if ((team1_lower in home_lower and team2_lower in away_lower) or
                        (team1_lower in away_lower and team2_lower in home_lower)):
                        return {
                            "api_source": "mock_sports_api",
                            "game_data": game_data,
                            "success": True
                        }
            
            # Return all games if no specific teams requested
            all_games = list(self.mock_games.values())
            return {
                "api_source": "mock_sports_api",
                "games": all_games,
                "total_games": len(all_games),
                "success": True
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve game scores: {e}",
                "success": False
            }
    
    @kernel_function(name="get_team_schedule", description="Get upcoming games for a specific team")
    def get_team_schedule(self, team: str, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get upcoming games for a specific team.
        
        Args:
            team: Team name
            days_ahead: Number of days to look ahead (default: 7)
        
        Returns:
            Dictionary containing upcoming games
        """
        try:
            team_lower = team.lower()
            upcoming_games = []
            
            # Mock upcoming games
            mock_upcoming = [
                {
                    "game_id": "LAL_PHX_20241216",
                    "league": "NBA",
                    "date": "2024-12-16",
                    "home_team": "Los Angeles Lakers",
                    "away_team": "Phoenix Suns",
                    "status": "scheduled",
                    "venue": "Crypto.com Arena",
                    "time": "8:00 PM PST"
                },
                {
                    "game_id": "GSW_SAC_20241217",
                    "league": "NBA",
                    "date": "2024-12-17",
                    "home_team": "Golden State Warriors",
                    "away_team": "Sacramento Kings",
                    "status": "scheduled",
                    "venue": "Chase Center",
                    "time": "7:30 PM PST"
                }
            ]
            
            for game in mock_upcoming:
                if team_lower in game["home_team"].lower() or team_lower in game["away_team"].lower():
                    upcoming_games.append(game)
            
            return {
                "api_source": "mock_sports_api",
                "team": team,
                "upcoming_games": upcoming_games,
                "total_games": len(upcoming_games),
                "success": True
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve team schedule: {e}",
                "success": False
            }
    
    @kernel_function(name="get_league_standings", description="Get current league standings")
    def get_league_standings(self, league: str = "NBA", conference: str = "") -> Dict[str, Any]:
        """
        Get current league standings.
        
        Args:
            league: Sports league (default: NBA)
            conference: Conference name (optional)
        
        Returns:
            Dictionary containing league standings
        """
        try:
            # Mock standings data
            mock_standings = {
                "western": [
                    {"team": "Minnesota Timberwolves", "wins": 18, "losses": 5, "win_pct": 0.783},
                    {"team": "Oklahoma City Thunder", "wins": 16, "losses": 8, "win_pct": 0.667},
                    {"team": "Denver Nuggets", "wins": 16, "losses": 10, "win_pct": 0.615},
                    {"team": "Sacramento Kings", "wins": 14, "losses": 10, "win_pct": 0.583},
                    {"team": "Los Angeles Lakers", "wins": 15, "losses": 10, "win_pct": 0.600}
                ],
                "eastern": [
                    {"team": "Boston Celtics", "wins": 20, "losses": 5, "win_pct": 0.800},
                    {"team": "Milwaukee Bucks", "wins": 18, "losses": 7, "win_pct": 0.720},
                    {"team": "Philadelphia 76ers", "wins": 16, "losses": 9, "win_pct": 0.640},
                    {"team": "Miami Heat", "wins": 15, "losses": 11, "win_pct": 0.577},
                    {"team": "Orlando Magic", "wins": 14, "losses": 11, "win_pct": 0.560}
                ]
            }
            
            if conference.lower() == "western":
                standings = mock_standings["western"]
            elif conference.lower() == "eastern":
                standings = mock_standings["eastern"]
            else:
                standings = mock_standings["western"] + mock_standings["eastern"]
            
            return {
                "api_source": "mock_sports_api",
                "league": league,
                "conference": conference or "all",
                "standings": standings,
                "total_teams": len(standings),
                "success": True
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve league standings: {e}",
                "success": False
            }
