"""
Manual Image Generator for CINE-GENESIS
This script uses Antigravity's generate_image tool to create scene images
"""
from pathlib import Path
import re

def parse_storyboard(storyboard_path: Path):
    """Parse storyboard into scenes"""
    with open(storyboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scenes = []
    scene_blocks = re.split(r'---+', content)
    
    for block in scene_blocks:
        block = block.strip()
        if not block or 'SCENE' not in block:
            continue
        
        scene = {}
        
        # Extract scene info
        heading_match = re.search(r'SCENE\s+(\d+):\s*(.+)', block)
        if heading_match:
            scene['scene_num'] = int(heading_match.group(1))
            scene['heading'] = heading_match.group(2).strip()
        
        # Extract fields
        for field in ['Shot Type', 'Lighting', 'Color Palette', 'Action', 'Visual Focus']:
            pattern = rf'{field}:\s*(.+?)(?:\n|$)'
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                scene[field.lower().replace(' ', '_')] = match.group(1).strip()
        
        if 'scene_num' in scene:
            scenes.append(scene)
    
    return scenes


def create_prompt(scene, frame_type='main'):
    """Create image generation prompt from scene data"""
    if frame_type == 'title':
        prompt = f"Title card for a film scene: '{scene.get('heading', 'Scene')}'. Elegant, minimalist typography on a dark background. Cinematic, professional."
    elif frame_type == 'main':
        prompt_parts = [
            "A cinematic film scene.",
            f"Camera: {scene.get('shot_type', 'Medium Shot')}.",
            f"Scene: {scene.get('action', 'Scene action')}",
            f"Lighting: {scene.get('lighting', 'Warm lighting')}.",
            f"Colors: {scene.get('color_palette', 'Neutral tones')}.",
            "Professional cinematography, film grain, 16:9 aspect ratio, high quality, masterpiece."
        ]
        prompt = " ".join(prompt_parts)
    else:  # details
        prompt = f"Close-up detail shot: {scene.get('visual_focus', 'Scene details')}. Cinematic lighting, shallow depth of field, film grain."
    
    return prompt


def main():
    print("=" * 60)
    print("  CINE-GENESIS Manual Image Generator")
    print("=" * 60)
    print()
    
    storyboard_path = Path("output/Dog_that_learns_to_speak/storyboard.txt")
    output_dir = Path("output/Dog_that_learns_to_speak/generated_images")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Reading storyboard: {storyboard_path}")
    scenes = parse_storyboard(storyboard_path)
    print(f"Found {len(scenes)} scenes")
    print()
    
    for scene in scenes:
        scene_num = scene.get('scene_num')
        print(f"Scene {scene_num}: {scene.get('heading', 'Unknown')}")
        
        for frame_type in ['title', 'main', 'details']:
            prompt = create_prompt(scene, frame_type)
            image_name = f"scene{scene_num}_{frame_type}"
            
            print(f"  - {frame_type.capitalize()}: {prompt[:80]}...")
            print(f"    → {image_name}.webp")
            # Note: You would use generate_image tool here
            # For now, just print what would be generated
        
        print()
    
    print("=" * 60)
    print("To generate images, Antigravity agent needs to call")
    print("generate_image tool for each prompt above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
