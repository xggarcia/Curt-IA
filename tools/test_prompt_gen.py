import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from cine_genesis.core.prompt_generator import PromptGenerator

def test_generate_prompts():
    print("Testing PromptGenerator...")
    
    # Path to existing storyboard
    storyboard_path = project_root / "output" / "Person_in_futuristic_city" / "storyboard.txt"
    
    if not storyboard_path.exists():
        print(f"Error: Storyboard not found at {storyboard_path}")
        return
        
    print(f"Reading storyboard from: {storyboard_path}")
    storyboard_text = storyboard_path.read_text(encoding='utf-8')
    
    # Generate prompts
    generator = PromptGenerator()
    prompts = generator.generate(storyboard_text)
    
    # Output path
    output_path = storyboard_path.parent / "video_generation_prompts.txt"
    output_path.write_text(prompts, encoding='utf-8')
    
    print(f"Generated prompts saved to: {output_path}")
    print("\n--- Preview of generated prompts ---")
    print(prompts[:500] + "...\n(truncated)")

if __name__ == "__main__":
    test_generate_prompts()
