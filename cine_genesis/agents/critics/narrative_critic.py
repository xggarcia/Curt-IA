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

Evaluate the screenplay on:
1. STRUCTURE: Clear beginning, middle, end? Proper dramatic arc?
2. CHARACTER: Are characters compelling and well-motivated?
3. DIALOGUE: Natural, purposeful, reveals character?
4. EMOTIONAL IMPACT: Does it evoke intended emotions?
5. THEME: Is the central message clear and resonant?
6. PACING: Appropriate rhythm for a short film?

Score 0-10 where:
- 9-10: Exceptional storytelling, emotionally powerful
- 7-8: Solid narrative with minor weak points
- 5-6: Structural or character issues need addressing
- 0-4: Major narrative problems"""

        prompt = f"""Evaluate this short film screenplay for narrative quality:

{script}

Provide detailed evaluation:

SCORE: [0-10]
STRUCTURE: [analysis of dramatic structure]
CHARACTER: [character depth and development]
DIALOGUE: [quality and naturalness of dialogue]
EMOTIONAL_IMPACT: [does it move the audience?]
THEME: [clarity and power of message]
ISSUES: [specific narrative problems, if any]
SUGGESTIONS: [actionable improvements]"""

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
            
            elif ':' in line and line.split(':')[0].strip().upper() in [
                'STRUCTURE', 'CHARACTER', 'DIALOGUE', 'EMOTIONAL_IMPACT', 
                'THEME', 'ISSUES'
            ]:
                section = line.split(':', 1)[0].strip()
                content = line.split(':', 1)[1].strip()
                if content:
                    comments += f"{section}: {content}\n"
                current_section = section.lower()
            
            elif line.startswith('SUGGESTIONS:'):
                current_section = 'suggestions'
                content = line.split(':', 1)[1].strip()
                if content:
                    suggestions.append(content)
            
            elif line and current_section == 'suggestions':
                if line.startswith('-') or line.startswith('•') or line[0].isdigit():
                    suggestions.append(line.lstrip('-•0123456789. '))
        
        if not suggestions:
            suggestions = self._ensure_actionable_feedback(comments, score)
        
        return score, comments.strip(), suggestions
