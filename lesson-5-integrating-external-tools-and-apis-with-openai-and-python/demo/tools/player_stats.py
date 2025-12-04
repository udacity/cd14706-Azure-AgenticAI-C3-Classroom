# tools/player_stats.py
from semantic_kernel.functions import kernel_function
import requests
import logging
import os

logger = logging.getLogger(__name__)

BALLDONTLIE_API = "https://api.balldontlie.io/v1"

class PlayerStatsTools:
    @kernel_function(name="get_player_stats", description="Get NBA player stats from the Ball Don't Lie API")
    def get_player_stats(self, player_name: str, league: str = "NBA", season: str = "2023-24"):
        """Fetch live player stats from the Ball Don't Lie API."""
        if league.upper() != "NBA":
            return {
                "error": f"League '{league}' not supported by Ball Don't Lie API",
                "supported": ["NBA"]
            }

        try:
            logger.info(f"Fetching real stats for player: {player_name}")

            # 1️⃣ Get player ID
            # Split player name into first and last name
            name_parts = player_name.strip().split(maxsplit=1)
            if len(name_parts) == 2:
                first_name, last_name = name_parts
            else:
                # If only one name provided, try as last name
                first_name, last_name = "", name_parts[0]

            search_params = {}
            if first_name:
                search_params["first_name"] = first_name
            if last_name:
                search_params["last_name"] = last_name

            BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
            headers = {"Authorization": BALLDONTLIE_API_KEY} if BALLDONTLIE_API_KEY else {}

            search_resp = requests.get(
                f"{BALLDONTLIE_API}/players",
                params=search_params,
                headers=headers
            )
            search_resp.raise_for_status()
            data = search_resp.json()
            if not data["data"]:
                return {"error": f"No player found for '{player_name}'"}

            player = data["data"][0]
            player_id = player["id"]

            # Return player info 
            return {
                "api_source": "Ball Don't Lie API (Free Tier - Player Info Only)",
                "player_name": f"{player['first_name']} {player['last_name']}",
                "player_id": str(player_id),
                "team": player["team"]["full_name"],
                "position": player["position"] or "N/A",
                "height": player.get("height", "N/A"),
                "weight": player.get("weight", "N/A"),
                "jersey_number": player.get("jersey_number", "N/A"),
                "college": player.get("college", "N/A"),
                "country": player.get("country", "N/A"),
                "draft_year": player.get("draft_year"),
                "draft_round": player.get("draft_round"),
                "draft_number": player.get("draft_number"),
                "message": "Note: Game stats require Ball Don't Lie API paid plan. Free tier provides player information only."
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning(f"Ball Don't Lie API unauthorized, using mock data")
                return self._get_mock_stats(player_name, league)
            elif e.response.status_code == 429:
                logger.warning(f"Ball Don't Lie API rate limit exceeded, using mock data")
                return self._get_mock_stats(player_name, league)
            else:
                logger.warning(f"Ball Don't Lie API error, using mock data: {e}")
                return self._get_mock_stats(player_name, league)
        except Exception as e:
            logger.warning(f"Ball Don't Lie API unavailable, using mock data: {e}")
            return self._get_mock_stats(player_name, league)

    def _get_mock_stats(self, player_name: str, league: str = "NBA"):
        """Return mock player stats as fallback"""
        mock_players = {
            "lebron james": {
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "position": "Forward",
                "height": "6-9",
                "weight": "250 lbs",
                "age": 39,
                "stats": {
                    "points_per_game": 25.7,
                    "rebounds_per_game": 7.3,
                    "assists_per_game": 8.3,
                    "field_goal_percentage": 0.540,
                    "three_point_percentage": 0.410,
                    "free_throw_percentage": 0.750
                },
                "message": "Mock data - Real API unavailable"
            },
            "stephen curry": {
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "position": "Guard",
                "height": "6-2",
                "weight": "185 lbs",
                "age": 35,
                "stats": {
                    "points_per_game": 26.4,
                    "rebounds_per_game": 4.5,
                    "assists_per_game": 5.0,
                    "field_goal_percentage": 0.453,
                    "three_point_percentage": 0.408,
                    "free_throw_percentage": 0.910
                },
                "message": "Mock data - Real API unavailable"
            },
            "giannis antetokounmpo": {
                "player_name": "Giannis Antetokounmpo",
                "team": "Milwaukee Bucks",
                "position": "Forward",
                "height": "6-11",
                "weight": "242 lbs",
                "age": 29,
                "stats": {
                    "points_per_game": 31.1,
                    "rebounds_per_game": 11.8,
                    "assists_per_game": 5.7,
                    "field_goal_percentage": 0.553,
                    "three_point_percentage": 0.279,
                    "free_throw_percentage": 0.651
                },
                "message": "Mock data - Real API unavailable"
            }
        }

        player_key = player_name.lower()
        if player_key in mock_players:
            return mock_players[player_key]
        else:
            # Generic fallback
            return {
                "player_name": player_name,
                "team": "Unknown Team",
                "position": "N/A",
                "message": f"Mock data for {player_name} - Real API unavailable"
            }
