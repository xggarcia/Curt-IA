"""
Prompt Generator - Creates optimized prompts for external video generation models from storyboard scenes.
"""
import logging
from typing import List, Dict, Any
from ..utils.video_animator import StoryboardParser

logger = logging.getLogger(__name__)

class PromptGenerator:
    """
    Generates detailed prompts for video generation models (e.g., Runway, Pika, Sora)
    based on storyboard scenes.
    """
    
    def __init__(self):
        self.parser = StoryboardParser()
        
    def generate(self, storyboard_text: str) -> str:
        """
        Generate a prompt document from storyboard text.
        
        Args:
            storyboard_text: The full text of the storyboard.
            
        Returns:
            A formatted string containing prompts for each scene.
        """
        scenes = self.parser.parse(storyboard_text)
        
        if not scenes:
            logger.warning("No scenes found in storyboard text.")
            return "No scenes found in storyboard."
            
        output_lines = []
        output_lines.append("# VIDEO GENERATION PROMPTS")
        output_lines.append("==========================\n")
        output_lines.append("Use these prompts with external video generation tools (Runway Gen-2/Gen-3, Pika, Stable Video Diffusion, etc.).")
        output_lines.append("They are optimized to include subject, action, environment, lighting, and camera movement.\n")
        
        for scene in scenes:
            scene_num = scene.get('scene_num', '?')
            heading = scene.get('heading', 'Unknown Scene')
            
            # Construct the prompt
            prompt = self._construct_prompt(scene)
            
            output_lines.append(f"## SCENE {scene_num}: {heading}")
            output_lines.append(f"**Prompt:**\n{prompt}\n")
            output_lines.append("-" * 40 + "\n")
            
        return "\n".join(output_lines)
    
    def _construct_prompt(self, scene: Dict[str, Any]) -> str:
        """
        Construct a single optimized prompt from a scene dictionary.
        """
        # Extract components
        action = scene.get('action', '').strip()
        visual_focus = scene.get('visual_focus', '').strip()
        lighting = scene.get('lighting', '').strip()
        colors = scene.get('color_palette', '').strip()
        camera = scene.get('camera_movement', '').strip()
        angle = scene.get('camera_angle', '').strip()
        shot_type = scene.get('shot_type', '').strip()
        composition = scene.get('composition', '').strip()
        
        # Build the prompt parts
        # 1. Subject & Action (The core visual)
        # Combine action and visual focus if they are different, otherwise just action
        core_visual = f"{action}"
        if visual_focus and visual_focus.lower() not in action.lower():
             core_visual += f", focus on {visual_focus}"
             
        # 2. Environment & Atmosphere (Lighting, Colors)
        atmosphere = []
        if lighting and lighting != 'N/A':
            atmosphere.append(f"{lighting} lighting")
        if colors and colors != 'N/A':
            atmosphere.append(f"{colors} color palette")
            
        # 3. Cinematography (Camera, Shot type)
        cinematography = []
        if shot_type and shot_type != 'N/A':
            cinematography.append(shot_type)
        if angle and angle != 'N/A':
            cinematography.append(angle)
        if camera and camera != 'N/A':
            cinematography.append(camera)
            
        # Assemble
        prompt_parts = [
            core_visual,
            "cinematic style, photorealistic, high quality, 4k", # Base style keywords
            ", ".join(atmosphere),
            ", ".join(cinematography)
        ]
        
        # Clean up empty parts
        prompt_parts = [p for p in prompt_parts if p and p.strip()]
        
        return ", ".join(prompt_parts) + "."
