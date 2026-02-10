"""
Coherence Manager - Maintains visual consistency across the film
Creates and enforces the "Visual Bible"
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import random
import json
from ..agent_base import Agent, AgentRole
from ...utils.api_clients import GeminiClient
from ...config import config


@dataclass
class CharacterAppearance:
    """Visual specification for a character"""
    name: str
    description: str
    seed: int
    age_range: str
    clothing: str
    distinctive_features: List[str] = field(default_factory=list)
    
    def to_prompt_fragment(self) -> str:
        """Convert to prompt fragment for image/video generation"""
        features_str = ", ".join(self.distinctive_features)
        return f"{self.description}, {self.age_range}, wearing {self.clothing}, {features_str}"


@dataclass
class ColorPalette:
    """Color palette for the film"""
    primary: str  # HEX code
    secondary: str  # HEX code
    accent: str  # HEX code
    background: str  # HEX code
    mood_keywords: List[str] = field(default_factory=list)
    
    def to_prompt_fragment(self) -> str:
        """Convert to prompt fragment"""
        mood_str = ", ".join(self.mood_keywords)
        return f"color palette: {', '.join([self.primary, self.secondary, self.accent])}, {mood_str} color scheme"


@dataclass
class LightingTemplate:
    """Lighting setup for scenes"""
    name: str
    time_of_day: str
    mood: str
    key_light_intensity: str  # e.g., "strong", "soft", "dramatic"
    fill_ratio: str  # e.g., "1:2", "1:4"
    color_temperature: str  # e.g., "warm", "cool", "neutral"
    
    def to_prompt_fragment(self) -> str:
        """Convert to prompt fragment"""
        return f"{self.time_of_day} lighting, {self.mood} atmosphere, {self.key_light_intensity} key light, {self. color_temperature} tones"


@dataclass
class VisualBible:
    """
    The Visual Bible - Complete visual specification for the film
    Ensures consistency across all generated content
    """
    characters: Dict[str, CharacterAppearance] = field(default_factory=dict)
    color_palette: Optional[ColorPalette] = None
    lighting_templates: Dict[str, LightingTemplate] = field(default_factory=dict)
    style_keywords: List[str] = field(default_factory=list)
    
    def add_character(self, character: CharacterAppearance):
        """Add a character to the bible"""
        self.characters[character.name] = character
    
    def get_character_prompt(self, character_name: str) -> str:
        """Get prompt fragment for a character"""
        if character_name not in self.characters:
            raise ValueError(f"Character '{character_name}' not in Visual Bible")
        return self.characters[character_name].to_prompt_fragment()
    
    def inject_into_prompt(
        self,
        base_prompt: str,
        characters: Optional[List[str]] = None,
        lighting: Optional[str] = None,
        include_color_palette: bool = True
    ) -> str:
        """
        Inject Visual Bible parameters into a prompt
        
        Args:
            base_prompt: Original prompt
            characters: List of character names to include
            lighting: Lighting template name
            include_color_palette: Whether to include color palette
            
        Returns:
            Enhanced prompt with Visual Bible parameters
        """
        enhanced = base_prompt
        
        # Add character specifications
        if characters:
            char_specs = []
            for char_name in characters:
                if char_name in self.characters:
                    char = self.characters[char_name]
                    char_specs.append(f"{char_name}: {char.to_prompt_fragment()}, seed:{char.seed}")
            if char_specs:
                enhanced += f"\nCharacters: {'; '.join(char_specs)}"
        
        # Add lighting
        if lighting and lighting in self.lighting_templates:
            enhanced += f"\nLighting: {self.lighting_templates[lighting].to_prompt_fragment()}"
        
        # Add color palette
        if include_color_palette and self.color_palette:
            enhanced += f"\n{self.color_palette.to_prompt_fragment()}"
        
        # Add style keywords
        if self.style_keywords:
            enhanced += f"\nStyle: {', '.join(self.style_keywords)}"
        
        return enhanced
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "characters": {
                name: {
                    "name": char.name,
                    "description": char.description,
                    "seed": char.seed,
                    "age_range": char.age_range,
                    "clothing": char.clothing,
                    "distinctive_features": char.distinctive_features
                }
                for name, char in self.characters.items()
            },
            "color_palette": {
                "primary": self.color_palette.primary,
                "secondary": self.color_palette.secondary,
                "accent": self.color_palette.accent,
                "background": self.color_palette.background,
                "mood_keywords": self.color_palette.mood_keywords
            } if self.color_palette else None,
            "lighting_templates": {
                name: {
                    "name": lt.name,
                    "time_of_day": lt.time_of_day,
                    "mood": lt.mood,
                    "key_light_intensity": lt.key_light_intensity,
                    "fill_ratio": lt.fill_ratio,
                    "color_temperature": lt.color_temperature
                }
                for name, lt in self.lighting_templates.items()
            },
            "style_keywords": self.style_keywords
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualBible":
        """Deserialize from dictionary"""
        bible = cls()
        
        # Load characters
        for name, char_data in data.get("characters", {}).items():
            bible.add_character(CharacterAppearance(**char_data))
        
        # Load color palette
        if data.get("color_palette"):
            bible.color_palette = ColorPalette(**data["color_palette"])
        
        # Load lighting templates
        for name, lt_data in data.get("lighting_templates", {}).items():
            bible.lighting_templates[name] = LightingTemplate(**lt_data)
        
        # Load style keywords
        bible.style_keywords = data.get("style_keywords", [])
        
        return bible


class CoherenceManagerAgent(Agent):
    """
    Coherence Manager - Creates and enforces the Visual Bible
    """
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        super().__init__("CoherenceManager", AgentRole.COHERENCE_MANAGER)
        self.gemini_client = gemini_client or GeminiClient(
            api_key=config.api.gemini_api_key,
            model=config.api.gemini_model
        )
        self.visual_bible: Optional[VisualBible] = None
    
    def create_visual_bible(
        self,
        script_or_concept: str,
        vision: Dict[str, str]
    ) -> VisualBible:
        """
        Create the Visual Bible based on script and director's vision
        
        Args:
            script_or_concept: The script or film concept
            vision: Director's vision dictionary
            
        Returns:
            Complete Visual Bible
        """
        system_instruction = f"""You are a cinematographer and production designer creating a Visual Bible for a short film.

The director's vision is:
- Genre: {vision.get('genre', 'N/A')}
- Tone: {vision.get('tone', 'N/A')}
- Pacing: {vision.get('pacing', 'N/A')}
- Message: {vision.get('message', 'N/A')}

Based on the script/concept, define:
1. All characters with detailed visual descriptions
2. A cohesive color palette (provide HEX codes)
3. Lighting templates for different moods/times
4. Style keywords for overall aesthetic

Be specific and detailed. This will ensure visual consistency."""

        prompt = f"""Script/Concept:
{script_or_concept}

Create a complete Visual Bible. Format your response as JSON:

{{
  "characters": [
    {{
      "name": "character name",
      "description": "detailed physical description",
      "age_range": "age range",
      "clothing": "clothing description",
      "distinctive_features": ["feature 1", "feature 2"]
    }}
  ],
  "color_palette": {{
    "primary": "#HEXCODE",
    "secondary": "#HEXCODE",
    "accent": "#HEXCODE",
    "background": "#HEXCODE",
    "mood_keywords": ["keyword1", "keyword2"]
  }},
  "lighting_templates": [
    {{
      "name": "template name",
      "time_of_day": "time",
      "mood": "mood",
      "key_light_intensity": "intensity",
      "fill_ratio": "ratio",
      "color_temperature": "temperature"
    }}
  ],
  "style_keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

        response = self.gemini_client.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.7
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (may have extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Create Visual Bible
            bible = VisualBible()
            
            # Add characters with random seeds
            for char_data in data.get("characters", []):
                char = CharacterAppearance(
                    name=char_data["name"],
                    description=char_data["description"],
                    seed=random.randint(1000, 9999),
                    age_range=char_data.get("age_range", "adult"),
                    clothing=char_data.get("clothing", "casual clothing"),
                    distinctive_features=char_data.get("distinctive_features", [])
                )
                bible.add_character(char)
            
            # Add color palette
            if "color_palette" in data:
                bible.color_palette = ColorPalette(**data["color_palette"])
            
            # Add lighting templates
            for lt_data in data.get("lighting_templates", []):
                lt = LightingTemplate(**lt_data)
                bible.lighting_templates[lt.name] = lt
            
            # Add style keywords
            bible.style_keywords = data.get("style_keywords", [])
            
            self.visual_bible = bible
            return bible
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RuntimeError(f"Failed to parse Visual Bible from LLM response: {str(e)}\n\nResponse: {response}")
    
    def execute(self, input_data: Any, context: Dict[str, Any]) -> VisualBible:
        """
        Execute coherence management task
        
        Args:
            input_data: Script or concept
            context: Must contain 'vision' dictionary
            
        Returns:
            Visual Bible
        """
        vision = context.get('vision', {})
        return self.create_visual_bible(input_data, vision)
