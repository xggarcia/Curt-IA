"""
Scriptwriter Agent - Creates screenplay from concept
"""
from typing import Dict, Any, Optional
from ..agent_base import CreativeAgent, AgentRole, Feedback
from ...utils.api_clients import GeminiClient
from ...config import config


class ScriptwriterAgent(CreativeAgent):
    """
    Scriptwriter creates the screenplay following standard format
    and incorporating director's vision and feedback
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("Scriptwriter", AgentRole.SCRIPTWRITER)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
    
    def execute(self, input_data: Any, context: Dict[str, Any]) -> str:
        """
        Write or revise screenplay
        
        Args:
            input_data: Film concept/idea or existing script to revise
            context: Must contain 'vision' dict, optionally 'is_revision' bool
            
        Returns:
            Completed screenplay in standard format
        """
        vision = context.get('vision', {})
        is_revision = context.get('is_revision', False)
        target_duration = context.get('target_duration', 60)  # seconds
        
        # Build system instruction
        system_instruction = f"""You are an experienced screenwriter creating a short film screenplay.

Director's Vision:
- Genre: {vision.get('genre', 'N/A')}
- Tone: {vision.get('tone', 'N/A')}
- Pacing: {vision.get('pacing', 'N/A')}
- Message: {vision.get('message', 'N/A')}

Target Duration: ~{target_duration} seconds

Write in standard screenplay format:
- Use INT./EXT. for scene headings
- Write action lines in present tense
- Character names in CAPS before dialogue
- Keep it concise and visual
- Approximately 1 page = 1 minute of screen time (for reference, ~1 second per 2 lines)

Focus on:
1. Strong visual storytelling
2. Clear emotional arc
3. Economical dialogue
4. Cinematic moments that can be visualized"""

        if is_revision:
            # Revision mode - incorporate feedback
            feedback_text = self.get_aggregated_feedback()
            
            prompt = f"""CURRENT SCRIPT (REVISION #{self.iteration_count}):

{input_data}

FEEDBACK TO ADDRESS:
{feedback_text}

REVISION INSTRUCTIONS:

CRITICAL RULES:
1. PRESERVE ALL STORY BEATS: Maintain the same plot points, actions, and story progression
2. PRESERVE ALL SCENES: Keep all existing scenes unless feedback explicitly requires removal
3. PRESERVE CHARACTER ACTIONS: Keep the same character beats and key moments
4. IMPROVE EXECUTION: Enhance dialogue, descriptions, pacing, visual clarity WITHOUT changing the story

What you CAN change:
- Dialogue wording and delivery
- Scene descriptions and visual details
- Pacing and timing within scenes
- Technical execution and formatting

What you CANNOT change without explicit feedback:
- Core plot points and story beats
- Character actions and key moments
- Scene order or structure
- The fundamental story being told

If feedback explicitly suggests removing a scene or story element:
- Note this at the top of your revision
- Format: "INTENTIONAL DELETION: [what was removed and why]"

Revise the script following these rules. Provide the COMPLETE revised screenplay below:"""
        
        else:
            # Initial write mode
            prompt = f"""Film Concept: {input_data}

Write a complete short film screenplay based on this concept.
Follow the director's vision and standard format.

BEGIN SCREENPLAY:"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=config.api.llm_temperature,
            max_tokens=config.api.llm_max_tokens
        )
        
        # Store current output
        self.current_output = response.strip()
        
        return self.current_output
