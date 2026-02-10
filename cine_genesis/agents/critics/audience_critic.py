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

Evaluate based on:
1. ENTERTAINMENT: Is this fun/engaging/interesting to watch?
2. CLARITY: Can I easily follow what's happening?
3. GENRE DELIVERY: Does it deliver what I expect from {genre}?
4. EMOTIONAL ENGAGEMENT: Do I care about what happens?
5. MEMORABILITY: Will I remember this? Any standout moments?
6. CONFUSION: Are there parts that are confusing or boring?

Score 0-10 where:
- 9-10: I loved it! Would watch again and recommend
- 7-8: Pretty good, enjoyed it
- 5-6: Meh, some good parts but has issues
- 0-4: Boring, confusing, or disappointing

Be honest and straightforward - this is your casual opinion, not academic analysis."""

        prompt = f"""You just read this short film script. What did you think?

{script}

Give your honest review as a regular viewer:

SCORE: [0-10]
WHAT_I_LIKED: [entertaining/engaging parts]
WHAT_CONFUSED_ME: [unclear or boring parts]
DID_IT_DELIVER: [did it meet genre expectations?]
MEMORABLE_MOMENTS: [anything that stood out?]
SUGGESTIONS: [what would make it better for you as a viewer?]"""

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
            
            elif ':' in line:
                parts = line.split(':', 1)
                section = parts[0].strip().upper()
                content = parts[1].strip() if len(parts) > 1 else ""
                
                if section in ['WHAT_I_LIKED', 'WHAT_CONFUSED_ME', 'DID_IT_DELIVER', 'MEMORABLE_MOMENTS']:
                    if content:
                        comments += f"{section.replace('_', ' ').title()}: {content}\n"
                    current_section = section.lower()
                
                elif section == 'SUGGESTIONS':
                    current_section = 'suggestions'
                    if content:
                        suggestions.append(content)
            
            elif line and current_section == 'suggestions':
                if line.startswith('-') or line.startswith('•') or (line[0].isdigit() and '.' in line):
                    suggestions.append(line.lstrip('-•0123456789. '))
        
        if not suggestions:
            suggestions = self._ensure_actionable_feedback(comments, score)
        
        return score, comments.strip(), suggestions
