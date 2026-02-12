"""
Narrative Critic Agent - Evaluates story and dramatic structure
"""
from typing import Dict, Any, Optional
from ..agent_base import CriticAgent, AgentRole, Feedback
from ...utils.api_clients import GeminiClient
from ...config import config


class NarrativeCriticAgent(CriticAgent):
    """
    Narrative Critic evaluates:
    - Story structure (3-act, pacing)
    - Character development
    - Dialogue quality
    - Emotional impact
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("NarrativeCritic", AgentRole.NARRATIVE_CRITIC)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
    
    def evaluate(self, work: Any, context: Dict[str, Any]) -> Feedback:
        """
        Evaluate narrative quality
        
        Args:
            work: Script or video to evaluate
            context: Contains work_type, vision, etc.
            
        Returns:
            Feedback with narrative score and suggestions
        """
        work_type = context.get('work_type', 'script')
        vision = context.get('vision', {})
        
        if work_type == 'script':
            return self._evaluate_script(work, vision)
        else:
            # For images/videos, narrative evaluation is limited
            # Could evaluate if the visual tells the story, but primarily for scripts
            return Feedback(
                critic_name=self.name,
                score=9.0,  # Default pass for non-script work
                comments="Narrative evaluation primarily applies to scripts",
                actionable_suggestions=["Continue with current approach"]
            )
    
    def _evaluate_script(self, script: str, vision: Dict[str, str]) -> Feedback:
        """Evaluate screenplay narrative quality"""
        system_instruction = f"""You are a seasoned script consultant and story editor.

The film's intended vision:
- Genre: {vision.get('genre', 'N/A')}
- Tone: {vision.get('tone', 'N/A')}
- Message: {vision.get('message', 'N/A')}

You MUST provide specific, detailed feedback in three categories:
1. GOOD - Strong narrative elements that work well
2. BAD - Narrative weaknesses and problems
3. IMPROVEMENTS - Specific actionable fixes for story/character/dialogue

Be specific: reference actual scenes, character moments, or dialogue from the script.

IMPORTANT: Preserve the story! Focus on improving execution, not changing plot.
Only suggest removing scenes/beats if absolutely necessary for story coherence.
If you DO suggest removal, explicitly state: "SUGGEST REMOVAL: [element] because [reason]"

Score 0-10 where:
- 9-10: Exceptional storytelling, emotionally powerful
- 7-8: Solid narrative with minor weak points
- 5-6: Structural or character issues need addressing
- 0-4: Major narrative problems"""

        prompt = f"""Evaluate this short film screenplay for narrative quality:

{script}

Analyze these aspects:
- Story structure and dramatic arc
- Character development and motivation
- Dialogue quality and naturalness
- Emotional impact
- Theme clarity
- Pacing for a short film

Provide evaluation in this EXACT format:

SCORE: [0-10]

GOOD:
- [Specific strong narrative element 1]
- [Specific strong narrative element 2]
- [Specific strong narrative element 3]

BAD:
- [Specific narrative weakness 1]
- [Specific narrative weakness 2]
- [Specific narrative weakness 3]

IMPROVEMENTS:
- [Actionable narrative improvement 1]
- [Actionable narrative improvement 2]
- [Actionable narrative improvement 3]"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3
        )
        
        score, comments, suggestions = self._parse_evaluation(response)
        
        return Feedback(
            critic_name=self.name,
            score=score,
            comments=comments,
            actionable_suggestions=suggestions
        )
    
    def _parse_evaluation(self, response: str) -> tuple[float, str, list[str]]:
        """Parse evaluation response"""
        score = 5.0
        comments = ""
        suggestions = []
        good_points = []
        bad_points = []
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SCORE:'):
                try:
                    score_text = line.split(':', 1)[1].strip()
                    score_num = score_text.split('/')[0].strip()
                    score = float(score_num)
                except (ValueError, IndexError):
                    score = 5.0
            
            elif line.upper().startswith('GOOD:'):
                current_section = 'good'
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    good_points.append(content)
            
            elif line.upper().startswith('BAD:'):
                current_section = 'bad'
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    bad_points.append(content)
            
            elif line.upper().startswith('IMPROVEMENTS:'):
                current_section = 'improvements'
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    suggestions.append(content)
            
            elif line and current_section in ['good', 'bad', 'improvements']:
                # Multi-line items
                if line.startswith('-') or line.startswith('•') or (line[0].isdigit() and '.' in line[:3]):
                    cleaned = line.lstrip('-•0123456789. ')
                    if current_section == 'good':
                        good_points.append(cleaned)
                    elif current_section == 'bad':
                        bad_points.append(cleaned)
                    elif current_section == 'improvements':
                        suggestions.append(cleaned)
        
        # Build structured comments
        if good_points:
            comments += "✅ GOOD:\n" + "\n".join([f"  • {point}" for point in good_points]) + "\n\n"
        if bad_points:
            comments += "❌ BAD:\n" + "\n".join([f"  • {point}" for point in bad_points]) + "\n\n"
        
        if not suggestions:
            suggestions = self._ensure_actionable_feedback(comments, score)
        
        return score, comments.strip(), suggestions
