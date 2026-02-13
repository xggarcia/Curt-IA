"""
Imagen Client - Local Stable Diffusion implementation
Uses locally running models for unlimited, free AI image generation
"""
import logging
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import torch
from PIL import Image

from cine_genesis.utils.api_key_pool import ApiKeyPool
from cine_genesis.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class ImagenClient:
    """Client for AI image generation using local Stable Diffusion"""
    
    def __init__(
        self,
        api_key: Union[str, List[str], ApiKeyPool] = None,  # Not used, kept for compatibility
        model: str = "runwayml/stable-diffusion-v1-5",
        requests_per_minute: int = 60  # Higher limit for local generation
    ):
        """
        Initialize local Stable Diffusion pipeline
        
        Args:
            api_key: Not used (kept for compatibility)
            model: Hugging Face model name to download
            requests_per_minute: Rate limit (not really needed for local, but kept for compatibility)
        """
        self.model_name = model
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Rate limiter (not strictly necessary for local, but kept for API compatibility)
        self.rate_limiter = RateLimiter(max_requests=requests_per_minute, time_window=60)
        
        logger.info(f"🎨 ImagenClient (Local Stable Diffusion) initializing...")
        logger.info(f"   Model: {model}")
        logger.info(f"   Device: {self.device}")
        
        if self.device == "cpu":
            logger.warning("⚠️  No CUDA GPU detected - using CPU (will be slow)")
        
        # Lazy load the pipeline on first use to avoid long startup times
        self._load_pipeline()
    
    def _load_pipeline(self):
        """Load the Stable Diffusion pipeline"""
        if self.pipe is not None:
            return  # Already loaded
        
        try:
            logger.info("📥 Loading Stable Diffusion model (this may take a few minutes on first run)...")
            
            from diffusers import StableDiffusionPipeline
            
            # Load pipeline with appropriate dtype
            if self.device == "cuda":
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    safety_checker=None,  # Disable safety checker for faster generation
                    requires_safety_checker=False
                )
                self.pipe = self.pipe.to("cuda")
                
                # Enable memory optimizations
                try:
                    self.pipe.enable_attention_slicing()
                    logger.info("✓ Enabled attention slicing for memory efficiency")
                except:
                    pass
                
            else:
                # CPU mode
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    safety_checker=None,
                    requires_safety_checker=False
                )
                self.pipe = self.pipe.to("cpu")
            
            logger.info("✅ Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {str(e)}")
            raise RuntimeError(f"Failed to load Stable Diffusion model: {str(e)}")
    
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        number_of_images: int = 1,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5
    ) -> List[Image.Image]:
        """
        Generate images using local Stable Diffusion
        
        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Image aspect ratio (we'll use 512x512 and resize)
            number_of_images: Number of images to generate
            num_inference_steps: Number of denoising steps (higher = better quality, slower)
            guidance_scale: How closely to follow the prompt (7-9 is good range)
            
        Returns:
            List of PIL Image objects
        """
        # Ensure pipeline is loaded
        if self.pipe is None:
            self._load_pipeline()
        
        # Check rate limit (mostly for compatibility)
        self.rate_limiter.wait_if_needed()
        
        logger.info(f"🎨 Generating image locally: {prompt[:100]}...")
        logger.info(f"   Steps: {num_inference_steps}, Guidance: {guidance_scale}")
        
        try:
            # Generate images
            images = []
            for i in range(number_of_images):
                result = self.pipe(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=512,
                    width=512
                )
                images.append(result.images[0])
                logger.info(f"✅ Generated image {i+1}/{number_of_images}")
            
            return images
            
        except Exception as e:
            logger.error(f"❌ Image generation failed: {str(e)}")
            raise RuntimeError(f"Local Stable Diffusion generation error: {str(e)}")
    
    def generate_cinematic_scene(
        self,
        scene_description: str,
        shot_type: str = "Medium Shot",
        lighting: str = "Warm, soft lighting",
        color_palette: str = "Warm tones",
        style: str = "cinematic",
        aspect_ratio: str = "16:9"
    ) -> Image.Image:
        """
        Generate a cinematic scene image optimized for film production
        
        Args:
            scene_description: Main description of the scene
            shot_type: Camera shot type
            lighting: Lighting description
            color_palette: Color palette description
            style: Visual style
            aspect_ratio: Image aspect ratio
            
        Returns:
            PIL Image object
        """
        # Construct detailed cinematic prompt
        # Stable Diffusion works better with concise, descriptive prompts
        prompt_parts = [
            f"{style} film scene,",
            f"{shot_type},",
            scene_description,
            f"{lighting},",
            f"{color_palette},",
            "professional cinematography, film grain, highly detailed, 8k, masterpiece"
        ]
        
        prompt = " ".join(prompt_parts)
        
        # Add negative prompt to improve quality
        negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy, cartoon, anime, text, watermark"
        
        logger.info(f"🎬 Generating cinematic scene...")
        
        # Generate with higher quality settings for cinematic look
        result = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=40,  # Higher steps for better quality
            guidance_scale=8.0,  # Stronger guidance for cinematic look
            height=512,
            width=512
        )
        
        return result.images[0]
