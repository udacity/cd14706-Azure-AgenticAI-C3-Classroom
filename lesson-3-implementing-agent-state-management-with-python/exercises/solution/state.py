from enum import Enum, auto
from typing import Optional, List, Dict, Any
from datetime import datetime

class Phase(Enum):
    """Agent state machine phases for customer service processing"""
    Init = "Init"                           # Create session/state; capture initial user goal
    ClarifyRequirements = "ClarifyRequirements"  # Ask targeted questions until required fields are present
    PlanTools = "PlanTools"                 # Decide which tools to call and with what args
    ExecuteTools = "ExecuteTools"           # Call order/product tools (and any others); collect results
    AnalyzeResults = "AnalyzeResults"       # Process tool outputs and validate data completeness
    ResolveIssues = "ResolveIssues"         # Handle any problems or edge cases
    ProduceStructuredOutput = "ProduceStructuredOutput"  # Emit Pydantic-validated JSON (and natural language summary)
    Done = "Done"                           # Process complete

class AgentState:
    """Agent state management with comprehensive tracking"""

    def __init__(self):
        # Core state
        self.phase: Phase = Phase.Init
        self.session_id: str = self._generate_session_id()
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

        # State transition history (for debugging and visualization)
        self.phase_history: List[Dict[str, Any]] = [{
            "phase": Phase.Init.value,
            "timestamp": datetime.now(),
            "trigger": "session_created"
        }]

        # User requirements (for customer service)
        self.order_id: Optional[str] = None
        self.product_id: Optional[str] = None
        self.customer_id: Optional[str] = None

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

    def advance(self, trigger: str = "auto_advance") -> bool:
        """Advance to the next phase in the state machine"""
        phase_order = list(Phase)
        try:
            current_index = phase_order.index(self.phase)
            if current_index < len(phase_order) - 1:
                old_phase = self.phase
                self.phase = phase_order[current_index + 1]
                self.updated_at = datetime.now()

                # Record state transition
                self.phase_history.append({
                    "from_phase": old_phase.value,
                    "to_phase": self.phase.value,
                    "timestamp": datetime.now(),
                    "trigger": trigger
                })
                return True
            else:
                old_phase = self.phase
                self.phase = Phase.Done
                self.updated_at = datetime.now()

                # Record final transition
                self.phase_history.append({
                    "from_phase": old_phase.value,
                    "to_phase": Phase.Done.value,
                    "timestamp": datetime.now(),
                    "trigger": trigger
                })
                return False
        except (ValueError, IndexError):
            old_phase = self.phase
            self.phase = Phase.Done
            self.updated_at = datetime.now()

            # Record error transition
            self.phase_history.append({
                "from_phase": old_phase.value if old_phase else "Unknown",
                "to_phase": Phase.Done.value,
                "timestamp": datetime.now(),
                "trigger": f"error_recovery: {trigger}"
            })
            return False

    def can_advance(self) -> bool:
        """Check if the agent can advance to the next phase"""
        return self.phase != Phase.Done

    def transition_to(self, new_phase: Phase, trigger: str = "manual_transition") -> bool:
        """
        Explicitly transition to a specific phase (with validation).
        This allows non-linear state transitions (e.g., jumping to ResolveIssues).
        """
        if new_phase == self.phase:
            return False  # Already in this phase

        old_phase = self.phase
        self.phase = new_phase
        self.updated_at = datetime.now()

        # Record the transition
        self.phase_history.append({
            "from_phase": old_phase.value,
            "to_phase": new_phase.value,
            "timestamp": datetime.now(),
            "trigger": trigger,
            "transition_type": "explicit"
        })
        return True

    def get_phase_duration(self, phase: Phase) -> Optional[float]:
        """Calculate how long the agent spent in a specific phase (in seconds)"""
        entries = [h for h in self.phase_history if h.get("to_phase") == phase.value or h.get("phase") == phase.value]
        if not entries:
            return None

        enter_time = None
        exit_time = None

        for i, entry in enumerate(self.phase_history):
            if entry.get("to_phase") == phase.value or entry.get("phase") == phase.value:
                enter_time = entry["timestamp"]
            if enter_time and i + 1 < len(self.phase_history):
                next_entry = self.phase_history[i + 1]
                if next_entry.get("from_phase") == phase.value:
                    exit_time = next_entry["timestamp"]
                    break

        if enter_time and exit_time:
            return (exit_time - enter_time).total_seconds()
        elif enter_time and self.phase == phase:
            return (datetime.now() - enter_time).total_seconds()
        return None

    def get_transition_summary(self) -> str:
        """Get a human-readable summary of all state transitions"""
        if not self.phase_history:
            return "No transitions recorded"

        summary_lines = ["State Transition Timeline:", "=" * 60]
        for i, entry in enumerate(self.phase_history, 1):
            if "from_phase" in entry:
                summary_lines.append(
                    f"{i}. {entry['from_phase']:25} → {entry['to_phase']:25} "
                    f"({entry['trigger']}) at {entry['timestamp'].strftime('%H:%M:%S')}"
                )
            else:
                summary_lines.append(
                    f"{i}. {entry['phase']:25} (initialized) at {entry['timestamp'].strftime('%H:%M:%S')}"
                )

        summary_lines.append("=" * 60)
        summary_lines.append(f"Total transitions: {len(self.phase_history)}")
        summary_lines.append(f"Session duration: {(datetime.now() - self.created_at).total_seconds():.1f}s")

        return "\n".join(summary_lines)

    def set_requirements(self, requirements: Dict[str, Any]) -> None:
        """Set user requirements and validate completeness"""
        self.requirements.update(requirements)
        self.data_completeness = self._calculate_completeness()
        self.updated_at = datetime.now()

    def set_required_fields_for_query_type(self, query_type: str) -> None:
        """Set required fields based on query type"""
        if query_type == "order_status":
            self.required_fields = ["order_id"]
        elif query_type == "product_info":
            self.required_fields = ["product_id"]
        elif query_type == "customer_service":
            self.required_fields = ["customer_id"]
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

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a complete snapshot of current state for debugging/logging.
        This is useful for in-session state inspection and debugging.
        """
        return {
            "session_id": self.session_id,
            "current_phase": self.phase.value,
            "phase_description": self.get_phase_description(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "session_duration_seconds": (datetime.now() - self.created_at).total_seconds(),

            # Requirements tracking
            "requirements": self.requirements.copy(),
            "required_fields": self.required_fields.copy(),
            "data_completeness": self.data_completeness,

            # Tool tracking
            "tools_called": self.tools_called.copy(),
            "tool_results_count": len(self.tool_results),
            "tool_errors_count": len(self.tool_errors),

            # Issues tracking
            "active_issues": self.issues.copy(),
            "resolved_issues": self.resolved_issues.copy(),
            "resolution_attempts": len(self.resolution_attempts),

            # Output tracking
            "has_structured_output": self.structured_output is not None,
            "has_summary": self.natural_language_summary is not None,
            "citations_count": len(self.citations),

            # State history
            "total_transitions": len(self.phase_history),
            "transition_history": [
                {
                    "from": h.get("from_phase", h.get("phase")),
                    "to": h.get("to_phase", "N/A"),
                    "trigger": h.get("trigger"),
                    "timestamp": h["timestamp"].isoformat()
                }
                for h in self.phase_history
            ]
        }

    def print_snapshot(self) -> None:
        """Print a formatted state snapshot for debugging"""
        snapshot = self.snapshot()
        print("\n" + "="*80)
        print(f"STATE SNAPSHOT: {snapshot['session_id']}")
        print("="*80)
        print(f"Current Phase: {snapshot['current_phase']} - {snapshot['phase_description']}")
        print(f"Session Duration: {snapshot['session_duration_seconds']:.1f}s")
        print(f"Data Completeness: {snapshot['data_completeness']:.1%}")
        print(f"\nTools Called: {len(snapshot['tools_called'])} ({', '.join(snapshot['tools_called']) if snapshot['tools_called'] else 'None'})")
        print(f"Active Issues: {len(snapshot['active_issues'])}")
        print(f"Resolved Issues: {len(snapshot['resolved_issues'])}")
        print(f"State Transitions: {snapshot['total_transitions']}")
        print(f"Has Output: {snapshot['has_structured_output']}")
        print("="*80 + "\n")
