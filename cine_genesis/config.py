"""
Configuration management for CINE-GENESIS
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class APIConfig:
    """API configuration for external services"""
    
    # LLM Configuration (Gemini)
    # Support multiple API keys for rotation
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = "gemini-flash-lite-latest"
    gemini_requests_per_minute: int = 5  # Rate limit
    llm_temperature: float = 0.7
    llm_max_tokens: int = 8000
    
    def get_all_gemini_keys(self) -> list[str]:
        """Get all available Gemini API keys from environment"""
        keys = []
        
        # Primary key
        if self.gemini_api_key:
            keys.append(self.gemini_api_key)
        
        # Additional keys (GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
        i = 2
        while True:
            key = os.getenv(f"GEMINI_API_KEY_{i}", "")
            if not key:
                break
            keys.append(key)
            i += 1
        
        return keys
    
    # Image Generation
    image_api_key: str = field(default_factory=lambda: os.getenv("STABILITY_API_KEY", ""))
    image_api_provider: str = "stability"  # stability, replicate, etc.
    image_model: str = "stable-diffusion-xl-1024-v1-0"
    
    # Video Generation
    video_api_key: str = field(default_factory=lambda: os.getenv("RUNWAY_API_KEY", ""))
    video_api_provider: str = "runway"  # runway, luma, etc.
    video_model: str = "gen3a_turbo"
    
    # Audio Generation
    tts_api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    music_api_key: str = field(default_factory=lambda: os.getenv("SUNO_API_KEY", ""))
    audio_api_provider: str = "elevenlabs"


@dataclass
class QualityConfig:
    """Quality control and evaluation settings"""
    
    # Voting thresholds
    default_quality_threshold: float = 9.0
    emergency_quality_threshold: float = 8.0
    
    # Iteration limits
    max_iterations_per_phase: int = 5
    enable_deadlock_breaking: bool = True
    
    # Critic weights (if using weighted voting)
    technical_critic_weight: float = 1.0
    narrative_critic_weight: float = 1.0
    audience_critic_weight: float = 1.0


@dataclass
class WorkflowConfig:
    """Workflow and output settings"""
    
    # Output paths
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    cache_dir: Path = field(default_factory=lambda: Path("./cache"))
    
    # Film parameters
    target_duration_seconds: int = 60
    video_resolution: tuple = (1920, 1080)
    video_fps: int = 24
    video_format: str = "mp4"
    
    # Logging
    log_level: str = "INFO"
    enable_verbose_logging: bool = True
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class CineGenesisConfig:
    """Main configuration container"""
    
    api: APIConfig = field(default_factory=APIConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> "CineGenesisConfig":
        """Create config from dictionary"""
        return cls(
            api=APIConfig(**config_dict.get("api", {})),
            quality=QualityConfig(**config_dict.get("quality", {})),
            workflow=WorkflowConfig(**config_dict.get("workflow", {}))
        )
    
    def validate(self) -> bool:
        """Validate that required API keys are present"""
        required_keys = [
            (self.api.gemini_api_key, "GEMINI_API_KEY"),
        ]
        
        missing_keys = [name for key, name in required_keys if not key]
        
        if missing_keys:
            raise ValueError(
                f"Missing required API keys: {', '.join(missing_keys)}. "
                f"Please set them as environment variables or in config."
            )
        
        return True


# Global config instance
config = CineGenesisConfig()
