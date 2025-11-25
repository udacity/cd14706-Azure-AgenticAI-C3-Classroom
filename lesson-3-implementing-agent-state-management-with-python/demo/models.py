# models.py - Pydantic models for sports analysis structured outputs
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class GameStatus(str, Enum):
    """Enum for game status values"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"

class LeagueType(str, Enum):
    """Enum for league types"""
    NBA = "NBA"
    NFL = "NFL"
    MLB = "MLB"
    NHL = "NHL"
    PREMIER_LEAGUE = "Premier League"
    CHAMPIONS_LEAGUE = "Champions League"
    MLS = "MLS"

class PlayerPosition(str, Enum):
    """Enum for player positions"""
    # Basketball
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    SMALL_FORWARD = "Small Forward"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"
    # Football
    QUARTERBACK = "Quarterback"
    RUNNING_BACK = "Running Back"
    WIDE_RECEIVER = "Wide Receiver"
    TIGHT_END = "Tight End"
    # Baseball
    PITCHER = "Pitcher"
    CATCHER = "Catcher"
    FIRST_BASE = "First Base"
    SECOND_BASE = "Second Base"
    THIRD_BASE = "Third Base"
    SHORTSTOP = "Shortstop"
    LEFT_FIELD = "Left Field"
    CENTER_FIELD = "Center Field"
    RIGHT_FIELD = "Right Field"
    # Hockey
    # CENTER = "Center" # earlier definition in basketball will work for this too
    LEFT_WING = "Left Wing"
    RIGHT_WING = "Right Wing"
    DEFENSEMAN = "Defenseman"
    GOALTENDER = "Goaltender"

class GameResult(BaseModel):
    """Response model for game results and scores"""
    game_id: str = Field(description="Unique identifier for the game")
    league: LeagueType = Field(description="Sports league")
    date: str = Field(description="Game date")
    home_team: str = Field(description="Home team name")
    away_team: str = Field(description="Away team name")
    home_score: int = Field(description="Home team score")
    away_score: int = Field(description="Away team score")
    status: GameStatus = Field(description="Current game status")
    quarter_period: Optional[str] = Field(None, description="Current quarter/period if in progress")
    time_remaining: Optional[str] = Field(None, description="Time remaining if in progress")
    venue: Optional[str] = Field(None, description="Stadium or venue name")
    attendance: Optional[int] = Field(None, description="Game attendance")
    message: Optional[str] = Field(None, description="Additional game information")

class PlayerPerformance(BaseModel):
    """Response model for player performance statistics"""
    player_id: str = Field(description="Unique identifier for the player")
    name: str = Field(description="Player name")
    team: str = Field(description="Current team")
    position: PlayerPosition = Field(description="Player position")
    league: LeagueType = Field(description="Sports league")
    season: str = Field(description="Season year")
    age: int = Field(description="Player age")
    height: str = Field(description="Player height")
    weight: str = Field(description="Player weight")
    stats: Dict[str, Any] = Field(description="Player statistics dictionary")
    recent_form: str = Field(description="Recent performance assessment")
    injury_status: str = Field(description="Current injury status")
    salary: Optional[float] = Field(None, description="Annual salary in millions")
    contract_years: Optional[int] = Field(None, description="Years remaining on contract")
    message: Optional[str] = Field(None, description="Additional player information")

class TeamAnalysis(BaseModel):
    """Response model for team analysis and standings"""
    team_id: str = Field(description="Unique identifier for the team")
    name: str = Field(description="Team name")
    city: str = Field(description="Team city")
    league: LeagueType = Field(description="Sports league")
    season: str = Field(description="Season year")
    wins: int = Field(description="Number of wins")
    losses: int = Field(description="Number of losses")
    ties: Optional[int] = Field(None, description="Number of ties (if applicable)")
    win_percentage: float = Field(description="Win percentage")
    conference_rank: int = Field(description="Conference ranking")
    division_rank: int = Field(description="Division ranking")
    points_for: int = Field(description="Points scored")
    points_against: int = Field(description="Points allowed")
    home_record: str = Field(description="Home win-loss record")
    away_record: str = Field(description="Away win-loss record")
    streak: str = Field(description="Current win/loss streak")
    message: Optional[str] = Field(None, description="Additional team information")

class SportsAnalysisResponse(BaseModel):
    """Main response model for sports analysis queries"""
    query_type: str = Field(description="Type of query (game_scores, player_stats, team_analysis, general)")
    human_readable_response: str = Field(description="Human-readable analysis for sports fans")
    structured_data: Optional[Dict] = Field(None, description="Structured sports data if applicable")
    tools_used: List[str] = Field(default_factory=list, description="List of tools that were used to answer the query")
    confidence_score: float = Field(default=0.0, description="Confidence score (0-1) for the analysis")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions or actions")
    predictions: List[Dict] = Field(default_factory=list, description="Predictions or forecasts if applicable")
    comparable_players: List[Dict] = Field(default_factory=list, description="Similar players for comparison")
    historical_context: Optional[str] = Field(None, description="Historical context or records")
