"""
Base classes for all agents in CINE-GENESIS
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class AgentRole(Enum):
    """Agent role types"""
    DIRECTOR = "director"
    COHERENCE_MANAGER = "coherence_manager"
    SCRIPTWRITER = "scriptwriter"
    STORYBOARD = "storyboard"
    ANIMATOR = "animator"
    AUDIO = "audio"
    EDITOR = "editor"
    TECHNICAL_CRITIC = "technical_critic"
    NARRATIVE_CRITIC = "narrative_critic"
    AUDIENCE_CRITIC = "audience_critic"


@dataclass
class Message:
    """Message passed between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Feedback:
    """Feedback from critics or director"""
    critic_name: str
    score: float  # 0-10
    comments: str
    actionable_suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class Agent(ABC):
    """
    Abstract base class for all agents in CINE-GENESIS
    """
    
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.id = str(uuid.uuid4())
        self.message_history: List[Message] = []
        
    @abstractmethod
    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """
        Execute the agent's primary task
        
        Args:
            input_data: Input for the task
            context: Additional context (vision, biblia visual, etc.)
            
        Returns:
            Output of the agent's work
        """
        pass
    
    def receive_message(self, message: Message):
        """Receive and store a message"""
        self.message_history.append(message)
        
    def send_message(self, recipient: str, content: Any, metadata: Optional[Dict] = None) -> Message:
        """Send a message to another agent"""
        message = Message(
            sender=self.name,
            recipient=recipient,
            content=content,
            metadata=metadata or {}
        )
        return message
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', role={self.role.value})>"


class CreativeAgent(Agent):
    """
    Base class for creative agents (scriptwriter, storyboard, animator, audio)
    Adds iteration tracking and feedback integration
    """
    
    def __init__(self, name: str, role: AgentRole):
        super().__init__(name, role)
        self.iteration_count = 0
        self.feedback_history: List[Feedback] = []
        self.current_output: Optional[Any] = None
        
    @abstractmethod
    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute creative task"""
        pass
    
    def receive_feedback(self, feedback: Feedback):
        """
        Receive feedback from critics and update state
        
        Args:
            feedback: Feedback object with score and suggestions
        """
        self.feedback_history.append(feedback)
        self.iteration_count += 1
        
    def get_aggregated_feedback(self) -> str:
        """
        Aggregate all feedback into actionable instructions
        
        Returns:
            Formatted string with all feedback and suggestions
        """
        if not self.feedback_history:
            return "No feedback received yet."
        
        # Get most recent round of feedback
        recent_feedback = [f for f in self.feedback_history if f.timestamp == max(fb.timestamp for fb in self.feedback_history)]
        
        aggregated = "=== FEEDBACK SUMMARY ===\n\n"
        
        for fb in recent_feedback:
            aggregated += f"[{fb.critic_name}] Score: {fb.score}/10\n"
            aggregated += f"Comments: {fb.comments}\n"
            
            if fb.actionable_suggestions:
                aggregated += "Suggestions:\n"
                for i, suggestion in enumerate(fb.actionable_suggestions, 1):
                    aggregated += f"  {i}. {suggestion}\n"
            
            aggregated += "\n"
        
        return aggregated
    
    def reset_iteration(self):
        """Reset iteration counter (used after phase success)"""
        self.iteration_count = 0
        self.feedback_history = []


class CriticAgent(Agent):
    """
    Base class for critic agents (technical, narrative, audience)
    Evaluates work and provides scored feedback
    """
    
    def __init__(self, name: str, role: AgentRole):
        super().__init__(name, role)
        self.evaluation_history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def evaluate(self, work: Any, context: Dict[str, Any]) -> Feedback:
        """
        Evaluate a piece of work and return scored feedback
        
        Args:
            work: The work to evaluate (script, video, etc.)
            context: Context including vision, previous feedback, etc.
            
        Returns:
            Feedback object with score and actionable suggestions
        """
        pass
    
    def execute(self, input_data: Any, context: Dict[str, Any]) -> Feedback:
        """
        Execute evaluation (implements abstract execute from Agent)
        
        Args:
            input_data: Work to evaluate
            context: Additional context
            
        Returns:
            Feedback object
        """
        feedback = self.evaluate(input_data, context)
        
        # Store evaluation in history
        self.evaluation_history.append({
            "timestamp": datetime.now(),
            "work": input_data,
            "feedback": feedback
        })
        
        return feedback
    
    def _ensure_actionable_feedback(self, comments: str, score: float) -> List[str]:
        """
        Extract or generate actionable suggestions from comments
        
        Args:
            comments: Raw feedback comments
            score: Score given
            
        Returns:
            List of actionable suggestions
        """
        # If score is high, no suggestions needed
        if score >= 9.0:
            return ["Continue with current approach"]
        
        # Otherwise, parse suggestions from comments
        # This is a simple implementation; can be enhanced with LLM
        suggestions = []
        
        # Split by common suggestion markers
        for line in comments.split('\n'):
            line = line.strip()
            if any(marker in line.lower() for marker in ['should', 'must', 'need to', 'improve', 'fix', 'change', 'add', 'remove']):
                suggestions.append(line)
        
        # If no suggestions found, create generic one
        if not suggestions:
            suggestions.append(f"Improve quality to reach 9/10 threshold (current: {score}/10)")
        
        return suggestions
