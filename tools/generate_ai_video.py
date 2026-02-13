"""
Standalone AI video generator - bypassing config issues
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

import re
from pathlib import Path
from PIL import Image
import numpy as np
from moviepy import ImageClip, concatenate_videoclips
import hashlib

# Setup
print("=" * 60)
print("  CINE-GENESIS AI Video Generator")
print("=" * 60)
print()

# Initialize Stable Diffusion
print("📥 Loading Stable Diffusion...")
from cine_genesis.utils.imagen_client import ImagenClient

client = ImagenClient(model="runwayml/stable-diffusion-v1-5")
print("✓ Model loaded")
print()

# Load storyboard
storyboard_file = Path("output/Dog_that_learns_to_speak/storyboard.txt")
print(f"📄 Loading storyboard: {storyboard_file}")
storyboard = storyboard_file.read_text(encoding='utf-8')

# Parse scenes
scenes = []
scene_blocks = re.split(r'---+', storyboard)

for block in scene_blocks:
    block = block.strip()
    if not block or 'SCENE' not in block:
        continue
    
    scene = {}
    
    # Extract scene number
    heading_match = re.search(r'SCENE\s+(\d+):\s*(.+)', block)
    if heading_match:
        scene['number'] = int(heading_match.group(1))
        scene['heading'] = heading_match.group(2).strip()
    
    # Extract fields
    for field in ['Shot Type', 'Lighting', 'Color Palette', 'Action', 'Visual Focus', 'Duration']:
        pattern = rf'{field}:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, block, re.IGNORECASE)
        if match:
            scene[field.lower().replace(' ', '_')] = match.group(1).strip()
    
    if 'number' in scene:
        scenes.append(scene)

print(f"✓ Parsed {len(scenes)} scenes")
print()

# Generate images  
cache_dir = Path("cache/generated_images")
cache_dir.mkdir(parents=True, exist_ok=True)

video_clips = []
total_images = len(scenes) * 3  # 3 images per scene

for idx, scene in enumerate(scenes):
    scene_num = scene['number']
    print(f"🎬 Scene {scene_num}: {scene.get('heading', 'Unknown')[:50]}...")
    
    # Generate 3 images per scene: title, main, details
    for frame_type in ['title', 'main', 'details']:
        # Create prompt
        if frame_type == 'title':
            prompt = f"Title card: '{scene.get('heading', 'Scene')}', elegant minimalist typography, dark background, cinematic"
        elif frame_type == 'main':
            prompt_parts = [
                "Cinematic film scene,",
                f"{scene.get('shot_type', 'Medium shot')},",
                scene.get('action', 'Scene'),
                f"{scene.get('lighting', 'Warm lighting')},",
                f"{scene.get('color_palette', 'Neutral tones')},",
                "professional cinematography, film grain, masterpiece, 8k"
            ]
            prompt = " ".join(prompt_parts)
        else:  # details
            prompt = f"Close-up detail shot: {scene.get('visual_focus', 'Scene details')}, cinematic lighting, shallow depth of field, film grain"
        
        # Check cache
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = cache_dir / f"{cache_key}.png"
        
        if cache_file.exists():
            print(f"  ✓ {frame_type}: cached")
            img = Image.open(cache_file)
        else:
            print(f"  🎨 {frame_type}: generating...")
            img = client.generate_cinematic_scene(
                scene_description=prompt
            )
            img.save(cache_file)
            print(f"  ✓ {frame_type}: saved to cache")
        
        # Create video clip from image (2 seconds each)
        img_array = np.array(img)
        clip = ImageClip(img_array).with_duration(2.0)
        video_clips.append(clip)
    
    print()

# Combine clips
print(f"🎞️  Combining {len(video_clips)} clips...")
final_video = concatenate_videoclips(video_clips, method="compose")

# Save video
output_file = Path("output/Dog_that_learns_to_speak/film_ai.mp4")
print(f"💾 Saving video: {output_file}")
final_video.write_videofile(
    str(output_file),
    fps=24,
    codec='libx264',
    audio=False
)

print()
print("=" * 60)
print(f"✅ SUCCESS! AI video created:")
print(f"   {output_file}")
print(f"   {len(scenes)} scenes, {len(video_clips)} image clips")
print("=" * 60)
