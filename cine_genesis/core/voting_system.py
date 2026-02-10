"""
Voting System - Aggregates critic feedback and determines pass/fail
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from ..agents.agent_base import Feedback
from ..config import config


@dataclass
class VotingResult:
    """Result of a voting round"""
    passed: bool
    average_score: float
    individual_scores: Dict[str, float]
    aggregated_feedback: str
    failing_critics: List[str]


class VotingSystem:
    """
    Manages the tribunal voting process
    Collects feedback from all critics and determines if work passes
    """
    
    def __init__(self, quality_threshold: float = None):
        self.quality_threshold = quality_threshold or config.quality.default_quality_threshold
    
    def collect_votes(self, feedbacks: List[Feedback]) -> VotingResult:
        """
        Collect and aggregate feedback from all critics
        
        Args:
            feedbacks: List of Feedback objects from critics
            
        Returns:
            VotingResult with pass/fail determination and aggregated feedback
        """
        if not feedbacks:
            raise ValueError("No feedback provided for voting")
        
        # Extract scores
        scores = {fb.critic_name: fb.score for fb in feedbacks}
        average_score = sum(scores.values()) / len(scores)
        
        # Determine if passed ALL critics meet threshold
        failing_critics = [
            name for name, score in scores.items() 
            if score < self.quality_threshold
        ]
        
        passed = len(failing_critics) == 0
        
        # Aggregate feedback
        aggregated = self._aggregate_feedback(feedbacks, passed)
        
        return VotingResult(
            passed=passed,
            average_score=average_score,
            individual_scores=scores,
            aggregated_feedback=aggregated,
            failing_critics=failing_critics
        )
    
    def _aggregate_feedback(self, feedbacks: List[Feedback], passed: bool) -> str:
        """
        Aggregate all feedback into a single formatted string
        
        Args:
            feedbacks: All feedback objects
            passed: Whether the vote passed
            
        Returns:
            Formatted feedback string
        """
        result = "=== TRIBUNAL VOTING RESULTS ===\n\n"
        result += f"STATUS: {'✓ APPROVED' if passed else '✗ REJECTED'}\n\n"
        
        # Individual critic feedback
        for fb in feedbacks:
            pass_fail = "✓" if fb.score >= self.quality_threshold else "✗"
            result += f"{pass_fail} [{fb.critic_name}] Score: {fb.score}/10\n"
            result += f"   Comments: {fb.comments}\n"
            
            if fb.actionable_suggestions and fb.score < self.quality_threshold:
                result += "   Suggestions:\n"
                for i, suggestion in enumerate(fb.actionable_suggestions, 1):
                    result += f"   {i}. {suggestion}\n"
            
            result += "\n"
        
        # Summary
        if passed:
            result += "VERDICT: All critics approve. Proceed to next phase.\n"
        else:
            avg = sum(f.score for f in feedbacks) / len(feedbacks)
            result += f"VERDICT: Revisions needed (avg score: {avg:.1f}/10)\n"
            result += "\nPRIORITY ACTIONS:\n"
            
            # Collect all suggestions from failing critics
            all_suggestions = []
            for fb in feedbacks:
                if fb.score < self.quality_threshold:
                    all_suggestions.extend(fb.actionable_suggestions)
            
            for i, suggestion in enumerate(all_suggestions, 1):
                result += f"{i}. {suggestion}\n"
        
        return result
    
    def set_threshold(self, new_threshold: float):
        """Update quality threshold (used for deadlock breaking)"""
        if not 0 <= new_threshold <= 10:
            raise ValueError("Threshold must be between 0 and 10")
        self.quality_threshold = new_threshold
    
    def get_worst_critic_feedback(self, feedbacks: List[Feedback]) -> Feedback:
        """
        Get feedback from the critic who gave the lowest score
        
        Args:
            feedbacks: All feedback objects
            
        Returns:
            Feedback object with lowest score
        """
        return min(feedbacks, key=lambda fb: fb.score)
