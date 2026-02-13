"""
Storyboard Agent - Creates detailed visual scene descriptions from screenplay
"""
from typing import Dict, Any, Optional
from ..agent_base import CreativeAgent, AgentRole
from ...utils.api_clients import GeminiClient
from ...config import config


class StoryboardAgent(CreativeAgent):
    """
    Storyboard Agent creates detailed visual descriptions for each scene
    in the screenplay, serving as a blueprint for visualization
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("Storyboard Artist", AgentRole.STORYBOARD)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
    
    def execute(self, input_data: Any, context: Dict[str, Any]) -> str:
        """
        Create detailed storyboard from screenplay
        
        Args:
            input_data: The approved screenplay text
            context: Director's vision and other context
            
        Returns:
            Detailed storyboard with scene-by-scene visual descriptions
        """
        screenplay = input_data
        vision = context.get('vision', {})
        
        system_instruction = f"""You are an experienced storyboard artist and cinematographer.

Your task is to create a detailed visual storyboard from the provided screenplay.

For EACH scene in the script, provide:
1. **Scene Number & Heading** - Scene identifier and INT/EXT location
2. **Shot Type** - (e.g., Wide Shot, Medium Shot, Close-Up, Extreme Close-Up, Over-the-Shoulder)
3. **Camera Movement** - (e.g., Static, Pan, Tilt, Dolly, Tracking, Handheld)
4. **Camera Angle** - (e.g., Eye Level, High Angle, Low Angle, Bird's Eye, Dutch Angle)
5. **Composition** - Frame composition and visual elements placement
6. **Lighting** - Lighting setup and mood (e.g., Natural, Hard, Soft, Dramatic, High-key, Low-key)
7. **Color Palette** - Dominant colors and visual tone
8. **Action Description** - What's happening in the frame
9. **Visual Focus** - What should draw the viewer's attention
10. **Duration** - Approximate shot length in seconds

Director's Vision for reference:
- Genre: {vision.get('genre', 'N/A')}
- Tone: {vision.get('tone', 'N/A')}
- Pacing: {vision.get('pacing', 'N/A')}

Format your output as a structured storyboard document with clear scene breaks.
Be specific and detailed - these descriptions should be clear enough for an animator or filmmaker to visualize."""

        prompt = f"""SCREENPLAY:

{screenplay}

===

Create a detailed visual storyboard for this screenplay. Break it down scene by scene with complete cinematographic details.

Format each scene as:

---
SCENE [NUMBER]: [Scene Heading]

Shot Type: [type]
Camera Movement: [movement]
Camera Angle: [angle]
Composition: [detailed description]
Lighting: [setup and mood]
Color Palette: [colors and tone]
Action: [what's happening]
Visual Focus: [key element]
Duration: ~[X] seconds
---

Provide the complete storyboard below:"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.7,
            max_tokens=8000
        )
        
        self.current_output = response.strip()
        return self.current_output
