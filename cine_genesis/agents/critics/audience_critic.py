"""
Audience Critic Agent - Evaluates entertainment and accessibility
"""
from typing import Dict, Any, Optional
from ..agent_base import CriticAgent, AgentRole, Feedback
from ...utils.api_clients import GeminiClient
from ...config import config


class AudienceCriticAgent(CriticAgent):
    """
    Audience Critic evaluates from average viewer perspective:
    - Entertainment factor
    - Clarity and understandability
    - Genre expectations
    - Rewatchability
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("AudienceCritic", AgentRole.AUDIENCE_CRITIC)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
    
    def evaluate(self, work: Any, context: Dict[str, Any]) -> Feedback:
        """
        Evaluate from audience perspective
        
        Args:
            work: Script or final video
            context: Contains work_type, vision, etc.
            
        Returns:
            Feedback with audience-focused score
        """
        work_type = context.get('work_type', 'script')
        vision = context.get('vision', {})
        
        if work_type == 'script':
            return self._evaluate_script(work, vision)
        else:
            # For now, default pass for non-script work
            # Could be extended to evaluate final video
            return Feedback(
                critic_name=self.name,
                score=9.0,
                comments="Audience evaluation primarily for scripts and final films",
                actionable_suggestions=["Continue with current approach"]
            )
    
    def _evaluate_script(self, script: str, vision: Dict[str, str]) -> Feedback:
        """Evaluate screenplay from audience perspective"""
        genre = vision.get('genre', 'unspecified genre')
        
        system_instruction = f"""You are an average moviegoer evaluating a {genre} short film script.

You're NOT a film expert - you're a regular viewer who wants to be entertained.

You MUST provide specific, detailed feedback in three categories:
1. GOOD - What audiences will enjoy and find engaging
2. BAD - What will confuse, bore, or disappoint audiences
3. IMPROVEMENTS - How to make it more engaging for viewers

Be specific: reference actual scenes, moments, or dialogue that you liked or didn't like.

IMPORTANT: Focus on how to make scenes MORE engaging, not removing them.
Only suggest cutting something if it truly ruins the viewing experience.
If you DO suggest removal, explicitly state: "SUGGEST REMOVAL: [element] because [reason]"

Score 0-10 where:
- 9-10: I loved it! Would watch again and recommend
- 7-8: Pretty good, enjoyed it
- 5-6: Meh, some good parts but has issues
- 0-4: Boring, confusing, or disappointing

Be honest and straightforward - this is your casual opinion, not academic analysis."""

        prompt = f"""You just read this short film script. What did you think?

{script}

Evaluate from a viewer's perspective:
- Entertainment and engagement factor
- Clarity and understandability
- Genre expectations delivery
- Emotional connection
- Memorable moments

Give your honest review in this EXACT format:

SCORE: [0-10]

GOOD:
- [Specific thing you enjoyed 1]
- [Specific thing you enjoyed 2]
- [Specific thing you enjoyed 3]

BAD:
- [Specific confusing/boring element 1]
- [Specific confusing/boring element 2]
- [Specific confusing/boring element 3]

IMPROVEMENTS:
- [How to make it better for viewers 1]
- [How to make it better for viewers 2]
- [How to make it better for viewers 3]"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.5  # Moderate temperature for "human" opinion
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
