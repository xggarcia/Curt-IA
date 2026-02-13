"""
Quick Test Script - Generate storyboard and animation from existing script
Bypasses the validation loop to test these features directly
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from cine_genesis.config import config
from cine_genesis.utils.api_clients import GeminiClient
from cine_genesis.agents.creative.storyboard_agent import StoryboardAgent
from cine_genesis.agents.creative.animator_agent import AnimatorAgent


def test_storyboard_and_animation(script_path: str, output_dir: str = "test_output"):
    """
    Test storyboard and animation generation from existing script
    
    Args:
        script_path: Path to existing script file
        output_dir: Directory for output files
    """
    script_file = Path(script_path)
    if not script_file.exists():
        logger.error(f"Script file not found: {script_path}")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load script
    logger.info(f"Loading script from: {script_path}")
    script = script_file.read_text(encoding='utf-8')
    
    # Initialize agents
    logger.info("Initializing agents...")
    api_keys = config.api.get_all_gemini_keys()
    gemini_client = GeminiClient(
        api_key=api_keys,
        model=config.api.gemini_model,
        requests_per_minute=config.api.gemini_requests_per_minute
    )
    
    storyboard_artist = StoryboardAgent(gemini_client)
    animator = AnimatorAgent()
    
    # Generate storyboard
    logger.info("\n" + "=" * 60)
    logger.info("GENERATING STORYBOARD")
    logger.info("=" * 60)
    
    try:
        storyboard = storyboard_artist.execute(
            input_data=script,
            context={"vision": {}}
        )
        
        # Save storyboard
        storyboard_path = output_path / "storyboard.txt"
        storyboard_path.write_text(storyboard, encoding='utf-8')
        logger.info(f"✅ Storyboard saved to: {storyboard_path}")
        
    except Exception as e:
        logger.error(f"❌ Storyboard generation failed: {e}")
        return
    
    # Generate animation
    logger.info("\n" + "=" * 60)
    logger.info("GENERATING ANIMATION")
    logger.info("=" * 60)
    logger.info("(This may take a few minutes)")
    
    try:
        video_path = output_path / "test_film.mp4"
        
        video_file = animator.execute(
            input_data=storyboard,
            context={"output_path": video_path}
        )
        
        logger.info(f"✅ Video created: {video_file}")
        
    except Exception as e:
        logger.error(f"❌ Animation failed: {e}")
        logger.error("\nMake sure you have installed:")
        logger.error("  pip install moviepy pillow numpy")
        return
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ TEST COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Output files in: {output_path}")
    logger.info(f"  - storyboard.txt")
    logger.info(f"  - test_film.mp4")


def main():
    """Main entry point"""
    print("=" * 60)
    print("  🎬 CINE-GENESIS - Quick Test Mode")
    print("=" * 60)
    print("\nThis mode lets you test storyboard and animation")
    print("generation from an existing script WITHOUT validation.\n")
    
    # Get script path
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
    else:
        script_path = input("Enter path to script file: ").strip()
    
    # Get output directory
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = input("Enter output directory (default: test_output): ").strip()
        if not output_dir:
            output_dir = "test_output"
    
    # Run test
    test_storyboard_and_animation(script_path, output_dir)


if __name__ == "__main__":
    main()
