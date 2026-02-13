"""
Minimal test to debug config issue
"""
from dotenv import load_dotenv
load_dotenv()

print("Step 1: Import config module directly")
import cine_genesis.config as cfg_module
print(f"  Config module: {cfg_module}")
print(f"  Has CineGenesisConfig: {has attr(cfg_module, 'CineGenesisConfig')}")
print(f"  Has VisualAnimationConfig: {hasattr(cfg_module, 'VisualAnimationConfig')}")
print(f"  Has config instance: {hasattr(cfg_module, 'config')}")
print()

print("Step 2: Check config instance")
config = cfg_module.config
print(f"  Config type: {type(config)}")
print(f"  Config fields: {[f for f in dir(config) if not f.startswith('_')]}")
print()

print("Step 3: Check for visual_animation attribute")
if hasattr(config, 'visual_animation'):
    print(f"  ✓ Has visual_animation")
    print(f"    Type: {type(config.visual_animation)}")
    print(f"    use_ai_images: {config.visual_animation.use_ai_images}")
else:
    print(f"  ❌ NO visual_animation attribute!")
    print(f"  Available: {[f for f in dir(config) if not f.startswith('_')]}")
print()

print("Step 4: Try to create VisualAnimationConfig manually")
try:
    visual_cfg = cfg_module.VisualAnimationConfig()
    print(f"  ✓ Created: {visual_cfg}")
    print(f"    use_ai_images: {visual_cfg.use_ai_images}")
except Exception as e:
    print(f"  ❌ Failed: {e}")
print()

print("Step 5: Try to access through regular import")
try:
    from cine_genesis.config import config as cfg
    print(f"  Config: {cfg}")
    print(f"  Has visual_animation: {hasattr(cfg, 'visual_animation')}")
    if hasattr(cfg, 'visual_animation'):
        print(f"  ✓ visual_animation.use_ai_images = {cfg.visual_animation.use_ai_images}")
    else:
        print(f"  ❌ Missing visual_animation")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
