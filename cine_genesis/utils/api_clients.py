"""
API client wrappers for external services
"""
import time
import requests
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from cine_genesis.utils.rate_limiter import RateLimiter
from cine_genesis.utils.api_key_pool import ApiKeyPool
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API (LLM and Vision)"""
    
    def __init__(
        self, 
        api_key: Union[str, List[str], ApiKeyPool], 
        model: str = "gemini-flash-lite-latest", 
        requests_per_minute: int = 5
    ):
        # Handle different input types
        if isinstance(api_key, ApiKeyPool):
            self.key_pool = api_key
        elif isinstance(api_key, list):
            self.key_pool = ApiKeyPool(api_key)
        else:
            self.key_pool = ApiKeyPool([api_key])
        
        self.model_name = model
        
        # Configure with current key
        current_key = self.key_pool.get_current_key()
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel(model)
        
        # Rate limiter to prevent quota errors
        self.rate_limiter = RateLimiter(max_requests=requests_per_minute, time_window=60)
        
        logger.info(f"🤖 GeminiClient initialized with {self.key_pool.get_status()['total_keys']} key(s)")
        
    def generate_text(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8000
    ) -> str:
        """
        Generate text using Gemini with automatic key rotation
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        max_retries = self.key_pool.get_status()['total_keys']
        
        for attempt in range(max_retries):
            try:
                # Check rate limit before making request
                self.rate_limiter.wait_if_needed()
                
                # Combine system instruction with prompt if provided
                if system_instruction:
                    full_prompt = f"{system_instruction}\n\n{prompt}"
                else:
                    full_prompt = prompt
                
                # Generate content
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                
                return response.text
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a quota error
                if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                    logger.warning(f"⚠️  Quota exceeded on attempt {attempt + 1}/{max_retries}")
                    
                    # Mark current key as exhausted
                    self.key_pool.mark_current_exhausted()
                    
                    # Try to rotate to next key
                    try:
                        new_key = self.key_pool.get_current_key()
                        genai.configure(api_key=new_key)
                        self.model = genai.GenerativeModel(self.model_name)
                        logger.info(f"✅ Switched to next API key, retrying...")
                        continue  # Retry with new key
                    except RuntimeError as pool_error:
                        # All keys exhausted
                        raise RuntimeError(f"Gemini API error: {pool_error}")
                else:
                    # Not a quota error, raise immediately
                    raise RuntimeError(f"Gemini API error: {error_str}")
        
        raise RuntimeError(f"Failed after {max_retries} attempts with all available API keys")
    
    def analyze_image(
        self, 
        image_path: Path, 
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Analyze image using Gemini Vision
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            system_instruction: Optional system instruction
            
        Returns:
            Analysis result
        """
        try:
            # Check rate limit before making request
            self.rate_limiter.wait_if_needed()
            
            # Load image
            img = Image.open(image_path)
            
            # Combine system instruction with prompt if provided
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Generate analysis
            response = self.model.generate_content([full_prompt, img])
            
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Gemini Vision API error: {str(e)}")
    
    def analyze_video(
        self,
        video_path: Path,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Analyze video using Gemini
        
        Args:
            video_path: Path to video file
            prompt: Analysis prompt
            system_instruction: Optional system instruction
            
        Returns:
            Analysis result
        """
        try:
            # Upload video file
            video_file = genai.upload_file(path=str(video_path))
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise RuntimeError("Video processing failed")
            
            # Combine system instruction with prompt if provided
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Generate analysis
            response = self.model.generate_content([full_prompt, video_file])
            
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Gemini Video API error: {str(e)}")


class ImageGenClient:
    """Client for image generation APIs (Stability AI, Replicate, etc.)"""
    
    def __init__(self, api_key: str, provider: str = "stability"):
        self.api_key = api_key
        self.provider = provider
        
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
        **kwargs
    ) -> bytes:
        """
        Generate image from text prompt
        
        Args:
            prompt: Image generation prompt
            negative_prompt: What to avoid
            width: Image width
            height: Image height
            seed: Random seed for consistency
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Image bytes
        """
        if self.provider == "stability":
            return self._generate_stability(prompt, negative_prompt, width, height, seed, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_stability(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        seed: Optional[int],
        **kwargs
    ) -> bytes:
        """Generate using Stability AI API"""
        # Placeholder implementation - requires actual API integration
        # For now, this is a stub that would need proper Stability AI SDK
        raise NotImplementedError(
            "Stability AI integration requires API setup. "
            "Please implement using stability-sdk or REST API."
        )


class VideoGenClient:
    """Client for video generation APIs (Runway, Luma, etc.)"""
    
    def __init__(self, api_key: str, provider: str = "runway"):
        self.api_key = api_key
        self.provider = provider
        
    def generate_video(
        self,
        prompt: Optional[str] = None,
        image_path: Optional[Path] = None,
        duration: int = 5,
        **kwargs
    ) -> bytes:
        """
        Generate video from text or image
        
        Args:
            prompt: Text prompt for generation
            image_path: Optional starting image
            duration: Video duration in seconds
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Video bytes
        """
        if self.provider == "runway":
            return self._generate_runway(prompt, image_path, duration, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_runway(
        self,
        prompt: Optional[str],
        image_path: Optional[Path],
        duration: int,
        **kwargs
    ) -> bytes:
        """Generate using Runway API"""
        # Placeholder implementation - requires actual API integration
        raise NotImplementedError(
            "Runway Gen-3 integration requires API setup. "
            "Please implement using Runway API."
        )


class AudioGenClient:
    """Client for audio generation APIs (ElevenLabs, Suno, etc.)"""
    
    def __init__(
        self,
        tts_api_key: str = "",
        music_api_key: str = "",
        provider: str = "elevenlabs"
    ):
        self.tts_api_key = tts_api_key
        self.music_api_key = music_api_key
        self.provider = provider
        
    def generate_speech(
        self,
        text: str,
        voice_id: str = "default",
        **kwargs
    ) -> bytes:
        """
        Generate speech from text
        
        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes
        """
        if self.provider == "elevenlabs":
            return self._generate_elevenlabs_tts(text, voice_id, **kwargs)
        else:
            raise ValueError(f"Unsupported TTS provider: {self.provider}")
    
    def _generate_elevenlabs_tts(
        self,
        text: str,
        voice_id: str,
        **kwargs
    ) -> bytes:
        """Generate speech using ElevenLabs"""
        # Placeholder implementation
        raise NotImplementedError(
            "ElevenLabs integration requires API setup. "
            "Please implement using elevenlabs SDK."
        )
    
    def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        **kwargs
    ) -> bytes:
        """
        Generate background music
        
        Args:
            prompt: Music generation prompt (mood, genre, etc.)
            duration: Duration in seconds
            **kwargs: Additional parameters
            
        Returns:
            Audio bytes
        """
        # Placeholder implementation
        raise NotImplementedError(
            "Music generation requires API setup (Suno, MusicGen, etc.)."
        )
