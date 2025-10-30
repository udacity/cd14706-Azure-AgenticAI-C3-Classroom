from enum import Enum, auto
from typing import Optional, List, Dict, Any
from datetime import datetime

class Phase(Enum):
    """Agent state machine phases for sports analysis processing"""
    Init = "Init"                           # Create session/state; capture initial user goal
    ClarifyRequirements = "ClarifyRequirements"  # Ask targeted questions until required fields are present
    PlanTools = "PlanTools"                 # Decide which tools to call and with what args
    ExecuteTools = "ExecuteTools"           # Call sports tools (scores, player stats, etc.); collect results
    AnalyzeResults = "AnalyzeResults"       # Process tool outputs and validate data completeness
    ResolveIssues = "ResolveIssues"         # Handle any problems or edge cases
    ProduceStructuredOutput = "ProduceStructuredOutput"  # Emit Pydantic-validated JSON (and natural language summary)
    Done = "Done"                           # Process complete

class AgentState:
    """Enhanced agent state management for sports analysis with comprehensive tracking"""
    
    def __init__(self):
        # Core state
        self.phase: Phase = Phase.Init
        self.session_id: str = self._generate_session_id()
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        
        # Sports requirements
        self.league: Optional[str] = None
        self.team: Optional[str] = None
        self.player: Optional[str] = None
        self.query_type: Optional[str] = None  # game_scores, player_stats, team_analysis
        
        # General requirements (for any agent)
        self.requirements: Dict[str, Any] = {}
        self.required_fields: List[str] = []
        self.clarification_questions: List[str] = []
        
        # Tool execution tracking
        self.tools_called: List[str] = []
        self.tool_results: Dict[str, Any] = {}
        self.tool_errors: Dict[str, str] = {}
        
        # Analysis and validation
        self.analysis_results: Optional[Dict[str, Any]] = None
        self.data_completeness: float = 0.0
        self.validation_errors: List[str] = []
        
        # Issues and resolution
        self.issues: List[str] = []
        self.resolution_attempts: List[str] = []
        self.resolved_issues: List[str] = []
        
        # Output generation
        self.structured_output: Optional[Dict[str, Any]] = None
        self.natural_language_summary: Optional[str] = None
        self.citations: List[str] = []
        
        # Session metadata
        self.summary: Optional[str] = None
        self.context: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import uuid
        return f"session_{uuid.uuid4().hex[:8]}"

    def advance(self) -> bool:
        """Advance to the next phase in the state machine"""
        phase_order = list(Phase)
        try:
            current_index = phase_order.index(self.phase)
            if current_index < len(phase_order) - 1:
                self.phase = phase_order[current_index + 1]
                self.updated_at = datetime.now()
                return True
            else:
                self.phase = Phase.Done
                self.updated_at = datetime.now()
                return False
        except (ValueError, IndexError):
            self.phase = Phase.Done
            self.updated_at = datetime.now()
            return False

    def can_advance(self) -> bool:
        """Check if the agent can advance to the next phase"""
        return self.phase != Phase.Done

    def set_requirements(self, requirements: Dict[str, Any]) -> None:
        """Set user requirements and validate completeness"""
        self.requirements.update(requirements)
        self.data_completeness = self._calculate_completeness()
        self.updated_at = datetime.now()
    
    def set_required_fields_for_query_type(self, query_type: str) -> None:
        """Set required fields based on query type"""
        if query_type == "game_scores":
            self.required_fields = ["league"]
        elif query_type == "player_stats":
            self.required_fields = ["player", "league"]
        elif query_type == "team_analysis":
            self.required_fields = ["team", "league"]
        else:
            self.required_fields = []
        self.updated_at = datetime.now()

    def add_clarification_question(self, question: str) -> None:
        """Add a clarification question to be asked"""
        if question not in self.clarification_questions:
            self.clarification_questions.append(question)
            self.updated_at = datetime.now()

    def mark_requirement_clarified(self, field: str) -> None:
        """Mark a requirement field as clarified"""
        if field in self.required_fields:
            self.required_fields.remove(field)
        self.updated_at = datetime.now()

    def add_tool_call(self, tool_name: str, result: Any = None, error: str = None) -> None:
        """Record a tool call and its result"""
        self.tools_called.append(tool_name)
        if result is not None:
            self.tool_results[tool_name] = result
        if error is not None:
            self.tool_errors[tool_name] = error
        self.updated_at = datetime.now()

    def set_analysis_results(self, results: Dict[str, Any]) -> None:
        """Set analysis results and calculate data completeness"""
        self.analysis_results = results
        self.data_completeness = self._calculate_completeness()
        self.updated_at = datetime.now()

    def _calculate_completeness(self) -> float:
        """Calculate data completeness percentage"""
        if not self.required_fields:
            # If no required fields are set, check if we have basic requirements
            if self.requirements:
                return 0.8  # Assume we have enough info if requirements exist
            return 0.0
        
        completed_fields = len([f for f in self.required_fields if f in self.requirements])
        return completed_fields / len(self.required_fields)

    def add_issue(self, issue: str) -> None:
        """Add an issue that needs resolution"""
        if issue not in self.issues:
            self.issues.append(issue)
            self.updated_at = datetime.now()

    def add_resolution_attempt(self, attempt: str) -> None:
        """Record a resolution attempt"""
        self.resolution_attempts.append(attempt)
        self.updated_at = datetime.now()

    def resolve_issue(self, issue: str) -> None:
        """Mark an issue as resolved"""
        if issue in self.issues:
            self.issues.remove(issue)
            self.resolved_issues.append(issue)
            self.updated_at = datetime.now()

    def set_structured_output(self, output: Dict[str, Any], summary: str = None) -> None:
        """Set the final structured output and natural language summary"""
        self.structured_output = output
        if summary:
            self.natural_language_summary = summary
        self.updated_at = datetime.now()

    def add_citation(self, citation: str) -> None:
        """Add a citation to the output"""
        if citation not in self.citations:
            self.citations.append(citation)
            self.updated_at = datetime.now()

    def get_phase_description(self) -> str:
        """Get a human-readable description of the current phase"""
        descriptions = {
            Phase.Init: "Initialize session and capture user goal",
            Phase.ClarifyRequirements: "Ask targeted questions to gather required information",
            Phase.PlanTools: "Decide which tools to call and with what parameters",
            Phase.ExecuteTools: "Execute planned tools and collect results",
            Phase.AnalyzeResults: "Process tool outputs and validate data completeness",
            Phase.ResolveIssues: "Handle any problems or edge cases identified",
            Phase.ProduceStructuredOutput: "Generate Pydantic-validated JSON and natural language summary",
            Phase.Done: "Process complete"
        }
        return descriptions.get(self.phase, "Unknown phase")

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a comprehensive status summary of the agent state"""
        return {
            "session_id": self.session_id,
            "phase": self.phase.value,
            "phase_description": self.get_phase_description(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "requirements": self.requirements,
            "required_fields": self.required_fields,
            "clarification_questions": self.clarification_questions,
            "tools_called": self.tools_called,
            "tool_errors": list(self.tool_errors.keys()),
            "data_completeness": self.data_completeness,
            "issues": self.issues,
            "resolved_issues": self.resolved_issues,
            "has_structured_output": self.structured_output is not None,
            "citations_count": len(self.citations)
        }

    def reset(self) -> None:
        """Reset the agent state to initial state"""
        self.__init__()

    def is_complete(self) -> bool:
        """Check if the agent process is complete"""
        return self.phase == Phase.Done

    def has_issues(self) -> bool:
        """Check if there are unresolved issues"""
        return len(self.issues) > 0

    def is_data_complete(self, threshold: float = 0.8) -> bool:
        """Check if data completeness meets the threshold"""
        return self.data_completeness >= threshold

    def set_sports_context(self, league: str = None, team: str = None, player: str = None) -> None:
        """Set sports-specific context"""
        if league:
            self.league = league
        if team:
            self.team = team
        if player:
            self.player = player
        self.updated_at = datetime.now()

    def get_sports_context(self) -> Dict[str, Any]:
        """Get current sports context"""
        return {
            "league": self.league,
            "team": self.team,
            "player": self.player,
            "query_type": self.query_type
        }