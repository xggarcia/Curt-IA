"""
Direct test of AI image video creation without workflow system
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

# Direct imports to bypass any caching issues
from cine_genesis.config import config, VisualAnimationConfig
from cine_genesis.agents.creative.animator_agent import AnimatorAgent

print("=" * 60)
print("  Direct AI Video Animation Test")
print("=" * 60)
print()

# Verify config
print(f"Config loaded: {config}")
print(f"Has visual_animation: {hasattr(config, 'visual_animation')}")
print(f"USE_AI_IMAGES: {config.visual_animation.use_ai_images}")
print(f"Model: {config.visual_animation.imagen_model}")
print()

# Create animator
print("📥 Creating AnimatorAgent with AI images...")
animator = AnimatorAgent()
print(f"✓ ImagenClient present: {animator.imagen_client is not None}")
print()

# Load storyboard
storyboard_file = Path("output/Dog_that_learns_to_speak/storyboard.txt")
print(f"📄 Loading: {storyboard_file}")
storyboard = storyboard_file.read_text(encoding='utf-8')
print(f"✓ {len(storyboard)} characters loaded")
print()

# Create video
output_file = Path("output/Dog_that_learns_to_speak/film_ai.mp4")
print(f"🎬 Generating AI video: {output_file}")
print("   NOTE: This will take ~20-30 minutes on CPU")
print("   Generating 24 AI images (3 per scene)")
print()

try:
    result = animator.create_video(
        storyboard=storyboard,
        output_path=output_file
    )
    
    print()
    print("=" * 60)
    print(f"✅ SUCCESS!")
    print(f"   Video: {result}")
    print("=" * 60)
    
except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ ERROR: {e}")
    print("=" * 60)
    
    import traceback
    traceback.print_exc()
