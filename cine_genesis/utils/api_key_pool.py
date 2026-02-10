"""
API Key Pool Manager - Rotates between multiple API keys
"""
import logging
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ApiKeyStatus:
    """Track status of an individual API key"""
    key: str
    exhausted: bool = False
    exhausted_at: Optional[datetime] = None
    request_count: int = 0
    
    def mark_exhausted(self):
        """Mark this key as exhausted"""
        self.exhausted = True
        self.exhausted_at = datetime.now()
        logger.warning(f"🔴 API key ...{self.key[-8:]} marked as exhausted")
    
    def reset_if_needed(self):
        """Reset key if 24 hours have passed since exhaustion"""
        if self.exhausted and self.exhausted_at:
            hours_since_exhaustion = (datetime.now() - self.exhausted_at).total_seconds() / 3600
            if hours_since_exhaustion >= 24:
                self.exhausted = False
                self.exhausted_at = None
                self.request_count = 0
                logger.info(f"✅ API key ...{self.key[-8:]} quota reset (24h passed)")
                return True
        return False


class ApiKeyPool:
    """
    Manages multiple API keys and rotates between them
    Automatically switches when quota is exceeded
    """
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize the key pool
        
        Args:
            api_keys: List of API keys to rotate through
        """
        if not api_keys:
            raise ValueError("At least one API key must be provided")
        
        self.keys = [ApiKeyStatus(key=key) for key in api_keys]
        self.current_index = 0
        
        logger.info(f"🔑 API Key Pool initialized with {len(self.keys)} key(s)")
    
    def get_current_key(self) -> str:
        """
        Get the current active API key
        
        Returns:
            Active API key string
        """
        # Reset any keys that have passed 24h cooldown
        for key_status in self.keys:
            key_status.reset_if_needed()
        
        # Find first non-exhausted key
        for i in range(len(self.keys)):
            idx = (self.current_index + i) % len(self.keys)
            if not self.keys[idx].exhausted:
                self.current_index = idx
                return self.keys[idx].key
        
        # All keys exhausted
        raise RuntimeError(
            "❌ All API keys exhausted! Please wait 24 hours or add more keys.\n"
            f"Keys exhausted: {len([k for k in self.keys if k.exhausted])}/{len(self.keys)}"
        )
    
    def mark_current_exhausted(self):
        """Mark the current key as exhausted and rotate to next"""
        self.keys[self.current_index].mark_exhausted()
        self._rotate_to_next_available()
    
    def _rotate_to_next_available(self):
        """Find and switch to the next available key"""
        starting_index = self.current_index
        
        for i in range(1, len(self.keys) + 1):
            next_idx = (starting_index + i) % len(self.keys)
            if not self.keys[next_idx].exhausted:
                old_key = self.keys[self.current_index].key[-8:]
                new_key = self.keys[next_idx].key[-8:]
                self.current_index = next_idx
                logger.info(f"🔄 Rotated API key: ...{old_key} → ...{new_key}")
                return
        
        raise RuntimeError(
            "❌ No available API keys remaining!\n"
            f"All {len(self.keys)} keys are exhausted. Wait 24h or add more keys."
        )
    
    def get_status(self) -> dict:
        """Get status of all keys"""
        return {
            "total_keys": len(self.keys),
            "active_keys": len([k for k in self.keys if not k.exhausted]),
            "exhausted_keys": len([k for k in self.keys if k.exhausted]),
            "current_key_suffix": self.keys[self.current_index].key[-8:]
        }
