# tools/player_stats.py - Player Statistics and Performance Tool

from semantic_kernel.functions import kernel_function
from typing import Dict, Any, List
import json

class PlayerStatsTools:
    """Tools for retrieving player statistics and performance data"""
    
    def __init__(self):
        self.mock_players = {
            "lebron_james": {
                "player_id": "lebron_james_001",
                "name": "LeBron James",
                "team": "Los Angeles Lakers",
                "position": "Small Forward",
                "league": "NBA",
                "season": "2024-25",
                "age": 39,
                "height": "6'9\"",
                "weight": "250 lbs",
                "stats": {
                    "points_per_game": 25.2,
                    "rebounds_per_game": 7.8,
                    "assists_per_game": 6.8,
                    "field_goal_percentage": 0.485,
                    "three_point_percentage": 0.382,
                    "free_throw_percentage": 0.875,
                    "steals_per_game": 1.2,
                    "blocks_per_game": 0.8,
                    "turnovers_per_game": 3.1,
                    "minutes_per_game": 35.4
                },
                "recent_form": "Excellent",
                "injury_status": "Healthy",
                "salary": 47.6,
                "contract_years": 2
            },
            "stephen_curry": {
                "player_id": "stephen_curry_001",
                "name": "Stephen Curry",
                "team": "Golden State Warriors",
                "position": "Point Guard",
                "league": "NBA",
                "season": "2024-25",
                "age": 35,
                "height": "6'2\"",
                "weight": "185 lbs",
                "stats": {
                    "points_per_game": 28.1,
                    "rebounds_per_game": 4.4,
                    "assists_per_game": 4.9,
                    "field_goal_percentage": 0.445,
                    "three_point_percentage": 0.420,
                    "free_throw_percentage": 0.920,
                    "steals_per_game": 1.0,
                    "blocks_per_game": 0.2,
                    "turnovers_per_game": 2.8,
                    "minutes_per_game": 32.1
                },
                "recent_form": "Struggling with shooting",
                "injury_status": "Healthy",
                "salary": 51.9,
                "contract_years": 3
            },
            "anthony_davis": {
                "player_id": "anthony_davis_001",
                "name": "Anthony Davis",
                "team": "Los Angeles Lakers",
                "position": "Power Forward",
                "league": "NBA",
                "season": "2024-25",
                "age": 31,
                "height": "6'10\"",
                "weight": "253 lbs",
                "stats": {
                    "points_per_game": 24.8,
                    "rebounds_per_game": 12.1,
                    "assists_per_game": 3.4,
                    "field_goal_percentage": 0.512,
                    "three_point_percentage": 0.298,
                    "free_throw_percentage": 0.812,
                    "steals_per_game": 1.3,
                    "blocks_per_game": 2.1,
                    "turnovers_per_game": 2.2,
                    "minutes_per_game": 36.2
                },
                "recent_form": "Dominant on defense",
                "injury_status": "Healthy",
                "salary": 40.6,
                "contract_years": 4
            }
        }
    
    @kernel_function(name="get_player_stats", description="Get detailed statistics for a specific player")
    def get_player_stats(self, player_name: str, season: str = "2024-25") -> Dict[str, Any]:
        """
        Get detailed statistics for a specific player.
        
        Args:
            player_name: Name of the player
            season: Season year (default: 2024-25)
        
        Returns:
            Dictionary containing player statistics
        """
        try:
            player_name_lower = player_name.lower().replace(" ", "_")
            
            # Find matching player
            for player_id, player_data in self.mock_players.items():
                if player_name_lower in player_id or player_name_lower in player_data["name"].lower():
                    return {
                        "api_source": "mock_sports_api",
                        "player_data": player_data,
                        "success": True
                    }
            
            return {
                "api_source": "mock_sports_api",
                "error": f"Player '{player_name}' not found",
                "success": False
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve player stats: {e}",
                "success": False
            }
    
    @kernel_function(name="get_team_roster", description="Get roster information for a specific team")
    def get_team_roster(self, team: str) -> Dict[str, Any]:
        """
        Get roster information for a specific team.
        
        Args:
            team: Team name
        
        Returns:
            Dictionary containing team roster
        """
        try:
            team_lower = team.lower()
            roster = []
            
            for player_id, player_data in self.mock_players.items():
                if team_lower in player_data["team"].lower():
                    roster.append({
                        "name": player_data["name"],
                        "position": player_data["position"],
                        "age": player_data["age"],
                        "height": player_data["height"],
                        "weight": player_data["weight"],
                        "injury_status": player_data["injury_status"]
                    })
            
            return {
                "api_source": "mock_sports_api",
                "team": team,
                "roster": roster,
                "total_players": len(roster),
                "success": True
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve team roster: {e}",
                "success": False
            }
    
    @kernel_function(name="get_league_leaders", description="Get league leaders in various statistical categories")
    def get_league_leaders(self, category: str = "points", limit: int = 10) -> Dict[str, Any]:
        """
        Get league leaders in various statistical categories.
        
        Args:
            category: Statistical category (points, rebounds, assists, etc.)
            limit: Number of players to return (default: 10)
        
        Returns:
            Dictionary containing league leaders
        """
        try:
            # Mock league leaders data
            leaders = {
                "points": [
                    {"player": "Luka Doncic", "team": "Dallas Mavericks", "value": 32.4},
                    {"player": "Stephen Curry", "team": "Golden State Warriors", "value": 28.1},
                    {"player": "LeBron James", "team": "Los Angeles Lakers", "value": 25.2},
                    {"player": "Anthony Davis", "team": "Los Angeles Lakers", "value": 24.8}
                ],
                "rebounds": [
                    {"player": "Rudy Gobert", "team": "Minnesota Timberwolves", "value": 12.8},
                    {"player": "Anthony Davis", "team": "Los Angeles Lakers", "value": 12.1},
                    {"player": "Nikola Jokic", "team": "Denver Nuggets", "value": 11.2},
                    {"player": "Domantas Sabonis", "team": "Sacramento Kings", "value": 10.9}
                ],
                "assists": [
                    {"player": "Tyrese Haliburton", "team": "Indiana Pacers", "value": 12.1},
                    {"player": "LeBron James", "team": "Los Angeles Lakers", "value": 6.8},
                    {"player": "Stephen Curry", "team": "Golden State Warriors", "value": 4.9},
                    {"player": "Anthony Davis", "team": "Los Angeles Lakers", "value": 3.4}
                ]
            }
            
            category_lower = category.lower()
            if category_lower in leaders:
                category_leaders = leaders[category_lower][:limit]
            else:
                category_leaders = leaders["points"][:limit]  # Default to points
            
            return {
                "api_source": "mock_sports_api",
                "category": category,
                "leaders": category_leaders,
                "total_players": len(category_leaders),
                "success": True
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve league leaders: {e}",
                "success": False
            }
    
    @kernel_function(name="get_injury_report", description="Get injury information for players")
    def get_injury_report(self, team: str = "", player: str = "") -> Dict[str, Any]:
        """
        Get injury information for players.
        
        Args:
            team: Team name (optional)
            player: Player name (optional)
        
        Returns:
            Dictionary containing injury information
        """
        try:
            # Mock injury report
            injuries = [
                {
                    "player": "Kawhi Leonard",
                    "team": "Los Angeles Clippers",
                    "injury": "Knee soreness",
                    "status": "Questionable",
                    "expected_return": "1-2 weeks"
                },
                {
                    "player": "Zion Williamson",
                    "team": "New Orleans Pelicans",
                    "injury": "Hamstring strain",
                    "status": "Out",
                    "expected_return": "2-3 weeks"
                },
                {
                    "player": "Ben Simmons",
                    "team": "Brooklyn Nets",
                    "injury": "Back spasms",
                    "status": "Day-to-day",
                    "expected_return": "1-2 days"
                }
            ]
            
            filtered_injuries = injuries
            if team:
                team_lower = team.lower()
                filtered_injuries = [inj for inj in injuries if team_lower in inj["team"].lower()]
            
            if player:
                player_lower = player.lower()
                filtered_injuries = [inj for inj in filtered_injuries if player_lower in inj["player"].lower()]
            
            return {
                "api_source": "mock_sports_api",
                "injuries": filtered_injuries,
                "total_injuries": len(filtered_injuries),
                "success": True
            }
            
        except Exception as e:
            return {
                "api_source": "mock_sports_api",
                "error": f"Failed to retrieve injury report: {e}",
                "success": False
            }
