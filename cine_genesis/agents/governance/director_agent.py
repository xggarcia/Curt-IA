"""
Director Agent - Supreme authority in CINE-GENESIS
Defines vision, filters creative work, and breaks deadlocks
"""
from typing import Dict, Any, Optional
from ..agent_base import Agent, AgentRole, Feedback
from ...utils.api_clients import GeminiClient
from ...config import config


class DirectorAgent(Agent):
    """
    The Director is the supreme authority that:
    - Defines initial vision (genre, tone, pacing, message)
    - Pre-filters creative work before tribunal review
    - Breaks deadlocks when phases fail too many times
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("Director", AgentRole.DIRECTOR)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
        self.vision: Optional[Dict[str, str]] = None
        
    def define_vision(self, film_idea: str) -> Dict[str, str]:
        """
        Define the creative vision for the film based on initial idea
        
        Args:
            film_idea: Brief description of the film concept
            
        Returns:
            Vision dictionary with genre, tone, pacing, and message
        """
        system_instruction = """You are an experienced film director defining the creative vision for a short film.
Given a film idea, you must define:
1. GENRE: The film genre (drama, comedy, sci-fi, horror, etc.)
2. TONE/MOOD: The emotional atmosphere (dark, lighthearted, mysterious, romantic, etc.)
3. PACING: The rhythm and tempo (fast-paced action, slow contemplative, varied)
4. CENTRAL MESSAGE: The core theme or message the film conveys

Be specific and clear. These parameters will guide all creative decisions."""

        prompt = f"""Film Idea: {film_idea}

Define the creative vision for this short film. Provide your response in this exact format:

GENRE: [genre]
TONE: [tone/mood]
PACING: [pacing description]
MESSAGE: [central message]"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=config.api.llm_temperature
        )
        
        # Parse response into dictionary
        vision = {}
        for line in response.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                vision[key] = value
        
        self.vision = vision
        return vision
    
    def review_creative_work(
        self,
        work: Any,
        work_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, str]:
        """
        Pre-filter creative work before sending to tribunal
        
        Args:
            work: The creative work (script, storyboard, etc.)
            work_type: Type of work ("script", "storyboard", "video", etc.)
            context: Additional context
            
        Returns:
            Tuple of (approved: bool, feedback: str)
        """
        if not self.vision:
            raise ValueError("Vision must be defined before reviewing work")
        
        system_instruction = f"""You are a film director reviewing {work_type} for your short film.

Your vision for this film is:
- Genre: {self.vision.get('genre', 'N/A')}
- Tone: {self.vision.get('tone', 'N/A')}
- Pacing: {self.vision.get('pacing', 'N/A')}
- Message: {self.vision.get('message', 'N/A')}

Review the submitted work and determine if it aligns with this vision.
If it does NOT align, provide specific, actionable feedback for improvement.
If it DOES align, approve it to proceed to the tribunal."""

        prompt = f"""Review this {work_type}:

{work}

Does this align with the creative vision? 

Provide your response in this format:
APPROVED: [YES/NO]
FEEDBACK: [detailed feedback with specific suggestions if not approved, or brief approval note if approved]"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.5  # Lower temperature for more consistent reviews
        )
        
        # Parse response
        approved = False
        feedback = ""
        
        for line in response.strip().split('\n'):
            if line.startswith('APPROVED:'):
                approved = 'YES' in line.upper()
            elif line.startswith('FEEDBACK:'):
                feedback = line.split(':', 1)[1].strip()
        
        return approved, feedback
    
    def execute_deadlock_protocol(
        self,
        work: Any,
        work_type: str,
        feedback_history: list[Feedback],
        iteration_count: int
    ) -> tuple[str, float]:
        """
        Break deadlock when a phase fails too many times
        
        Options:
        1. Rewrite the problematic part directly
        2. Lower quality threshold to 8.0
        
        Args:
            work: Current version of the work
            work_type: Type of work
            feedback_history: All feedback received
            iteration_count: Number of failed iterations
            
        Returns:
            Tuple of (action: "rewrite" or "lower_threshold", new_work_or_threshold)
        """
        # Aggregate all feedback
        all_feedback = "\n".join([
            f"[{f.critic_name}] Score: {f.score}/10 - {f.comments}"
            for f in feedback_history
        ])
        
        system_instruction = f"""You are a film director intervening to break a deadlock.

The {work_type} has failed approval {iteration_count} times. Here's all the feedback received:

{all_feedback}

You have two options:
1. REWRITE the work yourself to address the core issues
2. LOWER the quality threshold from 9.0 to 8.0 to allow it to pass

Decide which approach is best and execute it."""

        prompt = f"""Current {work_type}:

{work}

DEADLOCK INTERVENTION NEEDED ({iteration_count} failed iterations)

Choose your action:
ACTION: [REWRITE or LOWER_THRESHOLD]

If REWRITE: Provide the complete rewritten version below.
If LOWER_THRESHOLD: Explain why lowering the threshold is the best choice."""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.7
        )
        
        # Parse action
        if "REWRITE" in response[:200].upper():
            # Extract rewritten content (everything after "ACTION:" line)
            content_start = response.find('\n', response.find('ACTION:'))
            rewritten = response[content_start:].strip()
            return "rewrite", rewritten
        else:
            return "lower_threshold", config.quality.emergency_quality_threshold
    
    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """
        Execute director tasks based on context
        
        Args:
            input_data: Input data
            context: Must contain 'action' key specifying what to do
            
        Returns:
            Result based on action
        """
        action = context.get('action', 'review')
        
        if action == 'define_vision':
            return self.define_vision(input_data)
        elif action == 'review':
            work_type = context.get('work_type', 'work')
            return self.review_creative_work(input_data, work_type, context)
        elif action == 'deadlock':
            return self.execute_deadlock_protocol(
                input_data,
                context.get('work_type', 'work'),
                context.get('feedback_history', []),
                context.get('iteration_count', 0)
            )
        else:
            raise ValueError(f"Unknown director action: {action}")
