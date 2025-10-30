# tools/player_stats.py
from semantic_kernel.functions import kernel_function
import logging
import random

logger = logging.getLogger(__name__)

class PlayerStatsTools:
    @kernel_function(name="get_player_stats", description="Get detailed player statistics for various sports")
    def get_player_stats(self, player_name: str, league: str = "NBA", season: str = "2023-24"):
        """
        Get detailed player statistics for various sports.
        
        Args:
            player_name: Name of the player
            league: The sports league (NBA, NFL, MLB, NHL, etc.)
            season: Season year (e.g., "2023-24", "2024")
            
        Returns:
            Dictionary containing player statistics
        """
        try:
            logger.info(f"Getting player stats for: {player_name}, league: {league}, season: {season}")
            
            # Mock player data - in a real application, this would query a sports API
            mock_players = {
                "NBA": {
                    "LeBron James": {
                        "player_id": "NBA-001",
                        "name": "LeBron James",
                        "team": "Los Angeles Lakers",
                        "position": "Small Forward",
                        "league": "NBA",
                        "season": "2023-24",
                        "age": 39,
                        "height": "6'9\"",
                        "weight": "250 lbs",
                        "stats": {
                            "games_played": 45,
                            "points_per_game": 25.2,
                            "rebounds_per_game": 7.8,
                            "assists_per_game": 8.1,
                            "field_goal_percentage": 52.4,
                            "three_point_percentage": 35.2,
                            "free_throw_percentage": 73.1,
                            "minutes_per_game": 35.2,
                            "plus_minus": 2.3,
                            "steals_per_game": 1.2,
                            "blocks_per_game": 0.5,
                            "turnovers_per_game": 3.8
                        },
                        "recent_form": "Good - 3-game winning streak",
                        "injury_status": "Healthy",
                        "salary": 47.6,
                        "contract_years": 2
                    },
                    "Stephen Curry": {
                        "player_id": "NBA-002",
                        "name": "Stephen Curry",
                        "team": "Golden State Warriors",
                        "position": "Point Guard",
                        "league": "NBA",
                        "season": "2023-24",
                        "age": 35,
                        "height": "6'2\"",
                        "weight": "185 lbs",
                        "stats": {
                            "games_played": 42,
                            "points_per_game": 28.1,
                            "rebounds_per_game": 4.4,
                            "assists_per_game": 5.2,
                            "field_goal_percentage": 45.3,
                            "three_point_percentage": 42.1,
                            "free_throw_percentage": 91.7,
                            "minutes_per_game": 32.8,
                            "plus_minus": 4.1,
                            "steals_per_game": 1.0,
                            "blocks_per_game": 0.4,
                            "turnovers_per_game": 3.2
                        },
                        "recent_form": "Excellent - Leading scorer",
                        "injury_status": "Healthy",
                        "salary": 51.9,
                        "contract_years": 3
                    },
                    "Luka Doncic": {
                        "player_id": "NBA-003",
                        "name": "Luka Doncic",
                        "team": "Dallas Mavericks",
                        "position": "Point Guard",
                        "league": "NBA",
                        "season": "2023-24",
                        "age": 24,
                        "height": "6'7\"",
                        "weight": "230 lbs",
                        "stats": {
                            "games_played": 48,
                            "points_per_game": 32.4,
                            "rebounds_per_game": 8.2,
                            "assists_per_game": 9.1,
                            "field_goal_percentage": 48.7,
                            "three_point_percentage": 37.9,
                            "free_throw_percentage": 78.6,
                            "minutes_per_game": 37.5,
                            "plus_minus": 3.8,
                            "steals_per_game": 1.4,
                            "blocks_per_game": 0.5,
                            "turnovers_per_game": 4.0
                        },
                        "recent_form": "Outstanding - MVP candidate",
                        "injury_status": "Healthy",
                        "salary": 40.1,
                        "contract_years": 4
                    }
                },
                "NFL": {
                    "Patrick Mahomes": {
                        "player_id": "NFL-001",
                        "name": "Patrick Mahomes",
                        "team": "Kansas City Chiefs",
                        "position": "Quarterback",
                        "league": "NFL",
                        "season": "2024",
                        "age": 28,
                        "height": "6'3\"",
                        "weight": "230 lbs",
                        "stats": {
                            "games_played": 17,
                            "passing_yards": 4183,
                            "passing_touchdowns": 27,
                            "interceptions": 14,
                            "completion_percentage": 66.8,
                            "passer_rating": 92.6,
                            "rushing_yards": 389,
                            "rushing_touchdowns": 4,
                            "fumbles": 3,
                            "sacks_taken": 28
                        },
                        "recent_form": "Good - Playoff bound",
                        "injury_status": "Healthy",
                        "salary": 45.0,
                        "contract_years": 8
                    },
                    "Josh Allen": {
                        "player_id": "NFL-002",
                        "name": "Josh Allen",
                        "team": "Buffalo Bills",
                        "position": "Quarterback",
                        "league": "NFL",
                        "season": "2024",
                        "age": 27,
                        "height": "6'5\"",
                        "weight": "237 lbs",
                        "stats": {
                            "games_played": 17,
                            "passing_yards": 4306,
                            "passing_touchdowns": 29,
                            "interceptions": 18,
                            "completion_percentage": 66.5,
                            "passer_rating": 92.2,
                            "rushing_yards": 524,
                            "rushing_touchdowns": 15,
                            "fumbles": 4,
                            "sacks_taken": 25
                        },
                        "recent_form": "Excellent - Dual threat",
                        "injury_status": "Healthy",
                        "salary": 43.0,
                        "contract_years": 6
                    }
                },
                "MLB": {
                    "Aaron Judge": {
                        "player_id": "MLB-001",
                        "name": "Aaron Judge",
                        "team": "New York Yankees",
                        "position": "Right Field",
                        "league": "MLB",
                        "season": "2024",
                        "age": 31,
                        "height": "6'7\"",
                        "weight": "282 lbs",
                        "stats": {
                            "games_played": 106,
                            "batting_average": 0.275,
                            "home_runs": 37,
                            "runs_batted_in": 75,
                            "on_base_percentage": 0.406,
                            "slugging_percentage": 0.613,
                            "ops": 1.019,
                            "stolen_bases": 5,
                            "strikeouts": 98,
                            "walks": 68
                        },
                        "recent_form": "Good - Power hitting",
                        "injury_status": "Healthy",
                        "salary": 40.0,
                        "contract_years": 8
                    }
                },
                "NHL": {
                    "Connor McDavid": {
                        "player_id": "NHL-001",
                        "name": "Connor McDavid",
                        "team": "Edmonton Oilers",
                        "position": "Center",
                        "league": "NHL",
                        "season": "2023-24",
                        "age": 27,
                        "height": "6'1\"",
                        "weight": "194 lbs",
                        "stats": {
                            "games_played": 45,
                            "goals": 18,
                            "assists": 35,
                            "points": 53,
                            "plus_minus": 8,
                            "penalty_minutes": 18,
                            "power_play_goals": 4,
                            "short_handed_goals": 1,
                            "shots": 156,
                            "shooting_percentage": 11.5
                        },
                        "recent_form": "Excellent - Leading scorer",
                        "injury_status": "Healthy",
                        "salary": 12.5,
                        "contract_years": 6
                    }
                }
            }
            
            # Get player data for the specified league
            if league.upper() in mock_players:
                league_players = mock_players[league.upper()]
                
                # Search for player by name (case-insensitive)
                found_player = None
                for player_key, player_data in league_players.items():
                    if player_name.lower() in player_key.lower():
                        found_player = player_data
                        break
                
                if found_player:
                    return found_player
                else:
                    return {
                        "player_id": "UNKNOWN",
                        "name": player_name,
                        "team": "Unknown",
                        "position": "Unknown",
                        "league": league.upper(),
                        "season": season,
                        "age": 0,
                        "height": "Unknown",
                        "weight": "Unknown",
                        "stats": {},
                        "recent_form": "Unknown",
                        "injury_status": "Unknown",
                        "message": f"Player '{player_name}' not found in {league.upper()}"
                    }
            else:
                return {
                    "player_id": "UNKNOWN",
                    "name": player_name,
                    "team": "Unknown",
                    "position": "Unknown",
                    "league": league.upper(),
                    "season": season,
                    "age": 0,
                    "height": "Unknown",
                    "weight": "Unknown",
                    "stats": {},
                    "recent_form": "Unknown",
                    "injury_status": "Unknown",
                    "message": f"No data available for league: {league}"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get player stats: {e}")
            return {
                "player_id": "UNKNOWN",
                "name": player_name,
                "team": "Unknown",
                "position": "Unknown",
                "league": league.upper(),
                "season": season,
                "age": 0,
                "height": "Unknown",
                "weight": "Unknown",
                "stats": {},
                "recent_form": "Unknown",
                "injury_status": "Unknown",
                "message": f"Error retrieving player stats: {e}"
            }
