"""
Technical Critic Agent - Evaluates visual and technical quality
"""
from typing import Dict, Any, Optional
from pathlib import Path
from ..agent_base import CriticAgent, AgentRole, Feedback
from ...utils.api_clients import GeminiClient
from ...config import config


class TechnicalCriticAgent(CriticAgent):
    """
    Technical Critic evaluates:
    - Visual quality (resolution, artifacts, deformations)
    - Physical coherence (gravity, proportions, anatomy)
    - Temporal stability (flickering, morphing)
    - Consistency with Visual Bible
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("TechnicalCritic", AgentRole.TECHNICAL_CRITIC)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
    
    def evaluate(self, work: Any, context: Dict[str, Any]) -> Feedback:
        """
        Evaluate technical quality of work
        
        Args:
            work: The work to evaluate (can be script text, image path, or video path)
            context: Contains work_type, visual_bible, etc.
            
        Returns:
            Feedback with score and suggestions
        """
        work_type = context.get('work_type', 'script')
        visual_bible = context.get('visual_bible')
        
        if work_type == 'script':
            return self._evaluate_script(work, visual_bible)
        elif work_type == 'image':
            return self._evaluate_image(work, visual_bible, context)
        elif work_type == 'video':
            return self._evaluate_video(work, visual_bible, context)
        else:
            raise ValueError(f"Unknown work type: {work_type}")
    
    def _evaluate_script(self, script: str, visual_bible: Any) -> Feedback:
        """Evaluate script for technical feasibility"""
        system_instruction = """You are a technical director reviewing a screenplay for production feasibility.

You MUST provide specific, detailed feedback in three categories:
1. GOOD - What works well technically
2. BAD - What has significant technical problems
3. IMPROVEMENTS - Specific actionable steps to enhance quality

Be specific: reference actual scenes, effects, or descriptions from the script.

IMPORTANT: Preserve the story! Only suggest removing scenes/elements if absolutely necessary.
If you DO suggest removal, explicitly state: "SUGGEST REMOVAL: [element] because [reason]"

Score 0-10 where:
- 9-10: Excellent, highly producible
- 7-8: Good, minor technical concerns
- 5-6: Problematic areas need revision
- 0-4: Major technical issues"""

        prompt = f"""Review this screenplay for technical production quality:

{script}

Evaluate these aspects:
- Visual clarity and describability of scenes
- Technical feasibility with AI image/video generation
- Scene complexity and effects difficulty
- Continuity and transitions

Provide evaluation in this EXACT format:

SCORE: [0-10]

GOOD:
- [Specific positive technical aspect 1]
- [Specific positive technical aspect 2]
- [Specific positive technical aspect 3]

BAD:
- [Specific technical problem 1]
- [Specific technical problem 2]
- [Specific technical problem 3]

IMPROVEMENTS:
- [Actionable improvement 1]
- [Actionable improvement 2]
- [Actionable improvement 3]"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3  # Lower for more consistent evaluation
        )
        
        # Parse response
        score, comments, suggestions = self._parse_evaluation(response)
        
        return Feedback(
            critic_name=self.name,
            score=score,
            comments=comments,
            actionable_suggestions=suggestions
        )
    
    def _evaluate_image(self, image_path: Path, visual_bible: Any, context: Dict) -> Feedback:
        """Evaluate image quality and consistency"""
        system_instruction = """You are a cinematographer evaluating image quality for a film.

Evaluate:
1. Visual quality (clarity, artifacts, deformations)
2. Anatomical correctness (if people present)
3. Physical coherence (lighting, shadows, perspective)
4. Consistency with character/style specifications

Score 0-10 where:
- 9-10: Excellent quality, no issues
- 7-8: Good with minor flaws
- 5-6: Noticeable problems
- 0-4: Major quality issues"""

        # Build context about what should be in the image
        scene_description = context.get('scene_description', '')
        expected_elements = context.get('expected_elements', '')
        
        prompt = f"""Evaluate this image for a film production.

Expected scene: {scene_description}
Expected elements: {expected_elements}

Check for:
- Visual artifacts or deformations
- Anatomical issues (wrong proportions, extra fingers, distorted faces)
- Physical impossibilities
- Consistency with the scene requirements

SCORE: [0-10]
STRENGTHS: [what looks good]
ISSUES: [specific problems]
SUGGESTIONS: [how to fix issues]"""

        response = self.gemini_client.analyze_image(
            image_path=image_path,
            prompt=prompt,
            system_instruction=system_instruction
        )
        
        score, comments, suggestions = self._parse_evaluation(response)
        
        return Feedback(
            critic_name=self.name,
            score=score,
            comments=comments,
            actionable_suggestions=suggestions
        )
    
    def _evaluate_video(self, video_path: Path, visual_bible: Any, context: Dict) -> Feedback:
        """Evaluate video quality and temporal stability"""
        system_instruction = """You are a cinematographer evaluating video quality for a film.

Evaluate:
1. Visual quality throughout the clip
2. Temporal stability (no morphing, flickering, or sudden changes)
3. Motion coherence (smooth, believable movement)
4. Physical plausibility
5. Consistency across frames

Score 0-10 where:
- 9-10: Excellent, stable, high quality
- 7-8: Good with minor temporal issues
- 5-6: Noticeable instability or artifacts
- 0-4: Major quality or coherence problems"""

        scene_description = context.get('scene_description', '')
        
        prompt = f"""Evaluate this video clip for film production.

Expected scene: {scene_description}

Watch for:
- Temporal artifacts (morphing, flickering, discontinuities)
- Quality degradation across frames
- Unnatural motion or physics
- Character/object consistency throughout

SCORE: [0-10]
STRENGTHS: [what works well]
ISSUES: [specific problems and which frames]
SUGGESTIONS: [how to improve]"""

        response = self.gemini_client.analyze_video(
            video_path=video_path,
            prompt=prompt,
            system_instruction=system_instruction
        )
        
        score, comments, suggestions = self._parse_evaluation(response)
        
        return Feedback(
            critic_name=self.name,
            score=score,
            comments=comments,
            actionable_suggestions=suggestions
        )
    
    def _parse_evaluation(self, response: str) -> tuple[float, str, list[str]]:
        """Parse evaluation response into score, comments, and suggestions"""
        score = 5.0  # Default middle score
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
                    # Extract number (handle formats like "8/10" or just "8")
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
        
        # Ensure we have actionable suggestions
        if not suggestions:
            suggestions = self._ensure_actionable_feedback(comments, score)
        
        return score, comments.strip(), suggestions
