"""
Test script for CINE-GENESIS scriptwriting phase
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cine_genesis.core.workflow_orchestrator import WorkflowOrchestrator
from cine_genesis.config import config

def main():
    """Test the scriptwriting phase"""
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("\nPlease set it:")
        print("  export GEMINI_API_KEY='your_key_here'")
        print("\nOr create a .env file")
        sys.exit(1)
    
    print("=" * 60)
    print("  CINE-GENESIS TEST: Scriptwriting Phase")
    print("=" * 60)
    
    # Test with a simple concept
    film_idea = "A lonely robot discovers an abandoned music box and learns about human emotions through its melody."
    
    print(f"\nTest Concept: {film_idea}")
    print(f"\nConfiguration:")
    print(f"  - Target Duration: 60 seconds")
    print(f"  - Quality Threshold: 9.0/10")
    print(f"  - Max Iterations: 5")
    print("\n" + "=" * 60 + "\n")
    
    # Create test output directory
    test_output = Path("./test_output")
    test_output.mkdir(exist_ok=True)
    
    # Override config for testing
    config.workflow.output_dir = test_output
    config.workflow.target_duration_seconds = 60
    config.quality.default_quality_threshold = 9.0
    config.quality.max_iterations_per_phase = 5
    
    try:
        # Create and run orchestrator
        orchestrator = WorkflowOrchestrator(
            film_idea=film_idea,
            output_dir=test_output
        )
        
        print("Starting workflow...\n")
        result = orchestrator.run()
        
        print("\n" + "=" * 60)
        print("  ✓ TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nOutput saved to: {test_output}")
        print("\nGenerated files:")
        for file in sorted(test_output.glob("*")):
            print(f"  - {file.name}")
        
        # Display final script
        if orchestrator.state.script:
            print("\n" + "=" * 60)
            print("  FINAL APPROVED SCRIPT")
            print("=" * 60)
            print(orchestrator.state.script)
            print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
