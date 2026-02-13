"""
Video Animator Utility - Creates simple programmatic videos from storyboards
"""
import re
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class StoryboardParser:
    """Parse storyboard text into structured scene data"""
    
    @staticmethod
    def parse(storyboard_text: str) -> List[Dict[str, Any]]:
        """
        Parse storyboard text into scene dictionaries
        
        Returns:
            List of dicts with: scene_num, heading, shot_type, camera_movement,
                               camera_angle, composition, lighting, color_palette,
                               action, visual_focus, duration
        """
        scenes = []
        
        # Split by scene markers
        scene_blocks = re.split(r'---+', storyboard_text)
        
        for block in scene_blocks:
            block = block.strip()
            if not block:
                continue
            
            scene = {}
            
            # Extract scene heading
            heading_match = re.search(r'SCENE\s+(\d+):\s*(.+)', block)
            if heading_match:
                scene['scene_num'] = int(heading_match.group(1))
                scene['heading'] = heading_match.group(2).strip()
            
            # Extract fields
            scene['shot_type'] = StoryboardParser._extract_field(block, 'Shot Type')
            scene['camera_movement'] = StoryboardParser._extract_field(block, 'Camera Movement')
            scene['camera_angle'] = StoryboardParser._extract_field(block, 'Camera Angle')
            scene['composition'] = StoryboardParser._extract_field(block, 'Composition')
            scene['lighting'] = StoryboardParser._extract_field(block, 'Lighting')
            scene['color_palette'] = StoryboardParser._extract_field(block, 'Color Palette')
            scene['action'] = StoryboardParser._extract_field(block, 'Action')
            scene['visual_focus'] = StoryboardParser._extract_field(block, 'Visual Focus')
            
            # Extract duration
            duration_match = re.search(r'Duration:\s*~?(\d+\.?\d*)\s*seconds?', block, re.IGNORECASE)
            if duration_match:
                scene['duration'] = float(duration_match.group(1))
            else:
                scene['duration'] = 5.0  # Default
            
            if 'scene_num' in scene:
                scenes.append(scene)
        
        return scenes
    
    @staticmethod
    def _extract_field(text: str, field_name: str) -> str:
        """Extract field value from storyboard text"""
        pattern = rf'{field_name}:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else 'N/A'


class SimpleVideoAnimator:
    """Create simple programmatic videos from scene data"""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        
    def create_scene_frame(self, scene: Dict[str, Any], frame_type: str = 'main') -> np.ndarray:
        """
        Create a single frame for a scene
        
        Args:
            scene: Scene dictionary from parser
            frame_type: 'title', 'main', or 'details'
        """
        # Create PIL Image
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Determine background color from color palette
        bg_color = self._get_background_color(scene.get('color_palette', ''), 
                                               scene.get('lighting', ''))
        draw.rectangle([(0, 0), (self.width, self.height)], fill=bg_color)
        
        # Load or create font
        try:
            title_font = ImageFont.truetype("arial.ttf", 80)
            text_font = ImageFont.truetype("arial.ttf", 40)
            small_font = ImageFont.truetype("arial.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        if frame_type == 'title':
            # Scene title frame
            scene_num = scene.get('scene_num', '?')
            heading = scene.get('heading', 'Scene')
            
            title = f"SCENE {scene_num}"
            self._draw_centered_text(draw, title, self.height // 3, title_font, fill='white')
            self._draw_centered_text(draw, heading, self.height // 2, text_font, fill='white')
            
        elif frame_type == 'main':
            # Main action frame
            action = scene.get('action', 'N/A')
            shot_type = scene.get('shot_type', 'N/A')
            
            y_pos = self.height // 3
            self._draw_centered_text(draw, action, y_pos, text_font, fill='white', max_width=self.width - 200)
            self._draw_centered_text(draw, f"[{shot_type}]", y_pos + 100, small_font, fill='lightgray')
            
        elif frame_type == 'details':
            # Technical details frame
            details = [
                f"Camera: {scene.get('camera_movement', 'N/A')}",
                f"Angle: {scene.get('camera_angle', 'N/A')}",
                f"Lighting: {scene.get('lighting', 'N/A')}",
                f"Focus: {scene.get('visual_focus', 'N/A')}"
            ]
            
            y_pos = self.height // 4
            for detail in details:
                self._draw_centered_text(draw, detail, y_pos, small_font, fill='white')
                y_pos += 80
        
        # Convert to numpy array
        return np.array(img)
    
    def _get_background_color(self, color_palette: str, lighting: str) -> tuple:
        """Determine background color from palette and lighting"""
        color_palette = color_palette.lower()
        lighting = lighting.lower()
        
        # Map colors
        if 'blue' in color_palette or 'cool' in color_palette:
            return (30, 50, 80)
        elif 'red' in color_palette or 'warm' in color_palette:
            return (80, 40, 30)
        elif 'green' in color_palette or 'nature' in color_palette:
            return (30, 60, 30)
        elif 'dark' in lighting or 'low-key' in lighting:
            return (20, 20, 20)
        elif 'bright' in lighting or 'high-key' in lighting:
            return (200, 200, 200)
        else:
            return (50, 50, 50)  # Default dark gray
    
    def _draw_centered_text(self, draw, text, y_pos, font, fill='white', max_width=None):
        """Draw centered text with word wrapping"""
        if max_width:
            # Simple word wrapping
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > max_width and current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    current_line.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw each line
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                width = bbox[2] - bbox[0]
                x = (self.width - width) // 2
                draw.text((x, y_pos + i * 50), line, font=font, fill=fill)
        else:
            # Single line
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            x = (self.width - width) // 2
            draw.text((x, y_pos), text, font=font, fill=fill)
