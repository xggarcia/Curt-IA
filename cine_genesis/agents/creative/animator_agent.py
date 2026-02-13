"""
Animator Agent - Creates videos from storyboards using AI-generated visuals or programmatic animation
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import hashlib
import json

from ..agent_base import CreativeAgent, AgentRole
from ...utils.video_animator import StoryboardParser, SimpleVideoAnimator
from ...utils.imagen_client import ImagenClient
from ...config import config

logger = logging.getLogger(__name__)


class AnimatorAgent(CreativeAgent):
    """
    Animator Agent creates videos from storyboards using:
    - AI-generated images (Gemini Imagen 3) for visual scenes
    - Programmatic text overlays as fallback
    """
    
    def __init__(self, imagen_client: Optional[ImagenClient] = None):
        super().__init__("Animator", AgentRole.ANIMATOR)
        self.parser = StoryboardParser()
        self.animator = SimpleVideoAnimator(width=1920, height=1080, fps=30)
        
        # Initialize Imagen client if AI images are enabled
        if config.visual_animation.use_ai_images:
            if imagen_client:
                self.imagen_client = imagen_client
            else:
                # Create Imagen client with same key pool as Gemini
                api_keys = config.api.get_all_gemini_keys()
                self.imagen_client = ImagenClient(
                    api_key=api_keys,
                    model=config.visual_animation.imagen_model,
                    requests_per_minute=config.api.gemini_requests_per_minute
                )
            logger.info("🎨 AI image generation enabled")
        else:
            self.imagen_client = None
            logger.info("📝 Using text-based animation (AI images disabled)")
        
        #Cache directory for generated images
        self.cache_dir = config.workflow.cache_dir / "generated_images"
        if config.visual_animation.cache_generated_images:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, input_data: Any, context: Dict[str, Any]) -> str:
        """
        Create video from storyboard
        
        Args:
            input_data: Storyboard text
            context: Must contain 'output_path' for video file
            
        Returns:
            Path to created video file
        """
        storyboard_text = input_data
        output_path = Path(context.get('output_path', 'output.mp4'))
        
        logger.info("Parsing storyboard into scenes...")
        scenes = self.parser.parse(storyboard_text)
        logger.info(f"Found {len(scenes)} scenes")
        
        if not scenes:
            raise ValueError("No scenes found in storyboard")
        
        logger.info("Generating video frames...")
        video_path = self._create_video(scenes, output_path)
        
        self.current_output = str(video_path)
        return self.current_output
    
    def _create_video(self, scenes: list, output_path: Path) -> Path:
        """Create video from parsed scenes"""
        try:
            # MoviePy 2.x exports these directly from the main module
            from moviepy import ImageClip, concatenate_videoclips, vfx
        except ImportError as e:
            logger.error(f"Import error details: {e}")
            raise ImportError(
                "MoviePy is required for video animation. "
                "Install with: pip install moviepy\n"
                f"Error: {e}"
            )
        
        clips = []
        
        for scene in scenes:
            scene_duration = scene.get('duration', 5.0)
            
            # Create frames for this scene
            if self.imagen_client and config.visual_animation.use_ai_images:
                # Generate AI images for scene
                try:
                    # 1. Title frame (1 sec)
                    title_frame = self._generate_or_get_cached_image(scene, 'title')
                    title_clip = ImageClip(title_frame, duration=1.0)
                    title_clip = title_clip.with_effects([vfx.FadeIn(0.3)])
                    
                    # 2. Main action frame (duration - 2 sec)
                    main_frame = self._generate_or_get_cached_image(scene, 'main')
                    main_clip = ImageClip(main_frame, duration=max(scene_duration - 2, 1.0))
                    
                    # 3. Details frame (1 sec)
                    details_frame = self._generate_or_get_cached_image(scene, 'details')
                    details_clip = ImageClip(details_frame, duration=1.0)
                    details_clip = details_clip.with_effects([vfx.FadeOut(0.3)])
                    
                except Exception as e:
                    logger.warning(f"⚠️  AI image generation failed: {e}")
                    if config.visual_animation.fallback_to_text:
                        logger.info("📝 Falling back to text-based frames")
                        # Fallback to text frames
                        title_frame = self.animator.create_scene_frame(scene, 'title')
                        title_clip = ImageClip(title_frame, duration=1.0)
                        title_clip = title_clip.with_effects([vfx.FadeIn(0.3)])
                        
                        main_frame = self.animator.create_scene_frame(scene, 'main')
                        main_clip = ImageClip(main_frame, duration=max(scene_duration - 2, 1.0))
                        
                        details_frame = self.animator.create_scene_frame(scene, 'details')
                        details_clip = ImageClip(details_frame, duration=1.0)
                        details_clip = details_clip.with_effects([vfx.FadeOut(0.3)])
                    else:
                        raise
            else:
                # Use text-based frames (original behavior)
                # 1. Title frame (1 sec)
                title_frame = self.animator.create_scene_frame(scene, 'title')
                title_clip = ImageClip(title_frame, duration=1.0)
                title_clip = title_clip.with_effects([vfx.FadeIn(0.3)])
                
                # 2. Main action frame (duration - 2 sec)
                main_frame = self.animator.create_scene_frame(scene, 'main')
                main_clip = ImageClip(main_frame, duration=max(scene_duration - 2, 1.0))
                
                # 3. Details frame (1 sec)
                details_frame = self.animator.create_scene_frame(scene, 'details')
                details_clip = ImageClip(details_frame, duration=1.0)
                details_clip = details_clip.with_effects([vfx.FadeOut(0.3)])
            
            # Concatenate scene clips
            scene_clip = concatenate_videoclips([title_clip, main_clip, details_clip])
            clips.append(scene_clip)
        
        # Concatenate all scenes
        logger.info("Concatenating scenes...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Write video file
        logger.info(f"Writing video to: {output_path}")
        final_video.write_videofile(
            str(output_path),
            fps=self.animator.fps,
            codec='libx264',
            audio=False,
            logger=None  # Suppress moviepy's verbose logging
        )
        
        logger.info(f"✅ Video created: {output_path}")
        return output_path
    
    def _generate_or_get_cached_image(self, scene: Dict[str, Any], frame_type: str):
        """
        Generate AI image for scene or retrieve from cache
        
        Args:
            scene: Scene dictionary from parser
            frame_type: 'title', 'main', or 'details'
            
        Returns:
            NumPy array of image
        """
        # Create cache key from scene data
        cache_key_data = {
            'scene_num': scene.get('scene_num'),
            'heading': scene.get('heading'),
            'frame_type': frame_type,
            'shot_type': scene.get('shot_type'),
            'lighting': scene.get('lighting'),
            'color_palette': scene.get('color_palette'),
            'action': scene.get('action'),
            'resolution': config.visual_animation.image_resolution
        }
        cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.png"
        
        # Check cache
        if config.visual_animation.cache_generated_images and cache_file.exists():
            logger.info(f"📦 Using cached image for scene {scene.get('scene_num')} ({frame_type})")
            from PIL import Image
            import numpy as np
            img = Image.open(cache_file)
            return np.array(img)
        
        # Generate new image
        logger.info(f"🎨 Generating AI image for scene {scene.get('scene_num')} ({frame_type})...")
        
        # Create scene description based on frame type
        if frame_type == 'title':
            # Title card with scene heading
            description = f"Title card: {scene.get('heading', 'Scene')}, elegant typography, minimalist design"
        elif frame_type == 'main':
            # Main action scene
            description = scene.get('action', 'Scene action')
        else:  # details
            # Visual focus detail
            description = scene.get('visual_focus', 'Scene details')
        
        # Generate image
        pil_image = self.imagen_client.generate_cinematic_scene(
            scene_description=description,
            shot_type=scene.get('shot_type', 'Medium Shot'),
            lighting=scene.get('lighting', 'Warm lighting'),
            color_palette=scene.get('color_palette', 'Neutral tones'),
            style="cinematic",
            aspect_ratio=config.visual_animation.aspect_ratio
        )
        
        # Resize to target dimensions
        target_width, target_height = config.visual_animation.get_image_dimensions()
        pil_image = pil_image.resize((target_width, target_height))
        
        # Save to cache
        if config.visual_animation.cache_generated_images:
            pil_image.save(cache_file)
            logger.info(f"💾 Cached image to {cache_file}")
        
        # Convert to numpy array
        import numpy as np
        return np.array(pil_image)
