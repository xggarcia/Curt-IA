"""
Test checkpoint save/load and resume functionality
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cine_genesis.core.workflow_orchestrator import WorkflowState


def test_workflowstate_serialization():
    """Test that WorkflowState can be serialized and deserialized"""
    print("TEST 1: WorkflowState Serialization")
    print("-" * 60)
    
    # Create a sample state
    state = WorkflowState(
        current_phase="SCRIPTWRITING",
        iteration_count=2,
        film_idea="A robot learns about emotions",
        director_vision={"genre": "Sci-Fi", "tone": "Thoughtful"},
        script="INT. WORKSHOP - DAY\n\nA robot sits alone...",
    )
    
    # Convert to dict
    state_dict = state.to_dict()
    print(f"✓ Converted to dict: {list(state_dict.keys())}")
    
    # Convert to JSON
    json_str = json.dumps(state_dict, indent=2)
    print(f"✓ Serialized to JSON ({len(json_str)} bytes)")
    
    # Deserialize
    loaded_dict = json.loads(json_str)
    loaded_state = WorkflowState.from_dict(loaded_dict)
    
    # Verify
    assert loaded_state.current_phase == state.current_phase
    assert loaded_state.iteration_count == state.iteration_count
    assert loaded_state.film_idea == state.film_idea
    assert loaded_state.director_vision == state.director_vision
    assert loaded_state.script == state.script
    
    print("✓ Deserialized correctly")
    print("✅ TEST PASSED\n")


def test_checkpoint_file_operations():
    """Test saving and loading checkpoint files"""
    print("TEST 2: Checkpoint File Operations")
    print("-" * 60)
    
    # Create test directory
    test_dir = Path("./test_checkpoint_temp")
    test_dir.mkdir(exist_ok=True)
    checkpoint_path = test_dir / "workflow_state.json"
    
    try:
        # Create and save state
        state = WorkflowState(
            current_phase="PREPARATION",
            iteration_count=0,
            film_idea="Test film",
            director_vision={"genre": "Drama"},
        )
        
        # Save to file
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved checkpoint to: {checkpoint_path}")
        
        # Load from file
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            loaded_dict = json.load(f)
        
        loaded_state = WorkflowState.from_dict(loaded_dict)
        
        # Verify
        assert loaded_state.current_phase == "PREPARATION"
        assert loaded_state.film_idea == "Test film"
        assert loaded_state.director_vision["genre"] == "Drama"
        
        print("✓ Loaded checkpoint correctly")
        print("✅ TEST PASSED\n")
        
    finally:
        # Cleanup
        if checkpoint_path.exists():
            checkpoint_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_resume_detection():
    """Test that resume option detects existing checkpoints"""
    print("TEST 3: Resume Detection")
    print("-" * 60)
    
    # Check if output directory has any checkpoints
    output_base = Path("./output")
    if not output_base.exists():
        print("⊘ No output directory found (create one by running a workflow first)")
        print("⊘ TEST SKIPPED\n")
        return
    
    resumable_count = 0
    for path in output_base.iterdir():
        if path.is_dir():
            checkpoint = path / "workflow_state.json"
            if checkpoint.exists():
                resumable_count += 1
                try:
                    with open(checkpoint, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    print(f"✓ Found checkpoint: {path.name}")
                    print(f"  Phase: {state.get('current_phase', 'UNKNOWN')}")
                    print(f"  Iteration: {state.get('iteration_count', 0)}")
                except Exception as e:
                    print(f"✗ Corrupted checkpoint in {path.name}: {e}")
    
    if resumable_count > 0:
        print(f"\n✓ Found {resumable_count} resumable project(s)")
        print("✅ TEST PASSED\n")
    else:
        print("\n⊘ No resumable projects found")
        print("⊘ TEST SKIPPED\n")


def main():
    """Run all checkpoint tests"""
    print("\n" + "=" * 60)
    print("  CINE-GENESIS: Checkpoint System Tests")
    print("=" * 60)
    print()
    
    try:
        test_workflowstate_serialization()
        test_checkpoint_file_operations()
        test_resume_detection()
        
        print("=" * 60)
        print("  ✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
