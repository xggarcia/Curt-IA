"""
Simple test to verify AI image integration with animator
"""
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, '.')

print("Testing animator with AI images...")
print()

try:
    from cine_genesis import config
    from cine_genesis.agents.creative.animator_agent import AnimatorAgent
    from pathlib import Path
    
    # Check configuration
    print(f"✓ USE_AI_IMAGES: {config.visual_animation.use_ai_images}")
    print(f"✓ Model: {config.visual_animation.imagen_model}")
    print()
    
    # Initialize animator
    print("📥 Initializing AnimatorAgent...")
    animator = AnimatorAgent()
    print(f"✓ Animator initialized")
    print(f"✓ Imagen client: {animator.imagen_client is not None}")
    print()
    
    # Load storyboard
    storyboard_path = Path("output/Dog_that_learns_to_speak/storyboard.txt")
    print(f"📄 Loading storyboard: {storyboard_path}")
    
    with open(storyboard_path, 'r', encoding='utf-8') as f:
        storyboard_text = f.read()
    
    print(f"✓ Storyboard loaded ({len(storyboard_text)} chars)")
    print()
    
    # Parse scenes
    scenes = animator.parser.parse(storyboard_text)
    print(f"✓ Parsed {len(scenes)} scenes")
    print()
    
    # Try to create video
    output_path = Path("output/Dog_that_learns_to_speak/film_ai.mp4")
    print(f"🎬 Creating video with AI images: {output_path}")
    print("   This will take ~15-30 minutes for 24 images...")
    print()
    
    result = animator.create_video(
        storyboard=storyboard_text,
        output_path=output_path
    )
    
    print()
    print("=" * 60)
    print(f"✅ SUCCESS! AI video created: {result}")
    print("=" * 60)
    
except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
