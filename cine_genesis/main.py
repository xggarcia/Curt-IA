"""
CINE-GENESIS: Autonomous Short Film Production System
Main CLI entry point
"""
import sys
import argparse
from pathlib import Path
import logging

from cine_genesis.core.workflow_orchestrator import WorkflowOrchestrator
from cine_genesis.config import config


def interactive_menu():
    """Interactive menu for selecting options"""
    print("\n" + "=" * 60)
    print("  🎬 CINE-GENESIS Interactive Menu")
    print("=" * 60)
    
    # Check for resumable projects
    output_base = Path("./output")
    resumable_projects = []
    if output_base.exists():
        for path in output_base.iterdir():
            if path.is_dir():
                checkpoint = path / "workflow_state.json"
                if checkpoint.exists():
                    # Read checkpoint to get phase info
                    try:
                        import json
                        with open(checkpoint, 'r', encoding='utf-8') as f:
                            state = json.load(f)
                        resumable_projects.append((path, state))
                    except:
                        pass
    
    # Mode selection
    print("\n📝 How do you want to start?")
    print("  1. Create from idea (I have a concept)")
    print("  2. Refine existing script (I have a script file)")
    if resumable_projects:
        print("  3. Resume previous creation")
    
    mode = input("\nSelect mode (1, 2" + (", or 3" if resumable_projects else "") + "): ").strip()
    
    film_idea = None
    script_path = None
    resume_from = None
    output_dir = None
    story_name = None
    
    if mode == "1":
        print("\n" + "-" * 60)
        film_idea = input("💡 Enter your film idea: ").strip()
        if not film_idea:
            print("❌ Film idea cannot be empty!")
            sys.exit(1)
        
        # Ask for story name
        print("\n" + "-" * 60)
        print("📁 Story Name")
        print("  This will be used as the folder name for this project.")
        default_name = film_idea[:30].replace(" ", "_").replace("/", "_").replace("\\", "_")
        story_name_input = input(f"Enter story name (default: '{default_name}'): ").strip()
        story_name = story_name_input if story_name_input else default_name
        
        # Sanitize folder name
        story_name = "".join(c for c in story_name if c.isalnum() or c in ('_', '-', ' ')).rstrip()
        story_name = story_name.replace(" ", "_")
        
        output_dir = output_base / story_name
        
        # Check if folder exists
        if output_dir.exists():
            checkpoint = output_dir / "workflow_state.json"
            if checkpoint.exists():
                print(f"\n⚠️  Story folder '{story_name}' already exists!")
                print(f"   Found checkpoint at: {checkpoint}")
                
                # Load checkpoint info
                try:
                    import json
                    with open(checkpoint, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    phase = state.get('current_phase', 'UNKNOWN')
                    iteration = state.get('iteration_count', 0)
                    print(f"   Phase: {phase}, Iteration: {iteration}")
                except:
                    pass
                
                resume_choice = input("\n   Resume from this checkpoint? (Y/n): ").strip().lower()
                if resume_choice != 'n':
                    resume_from = checkpoint
                    print(f"✅ Will resume from existing checkpoint")
                else:
                    overwrite = input("   Overwrite existing folder? (y/N): ").strip().lower()
                    if overwrite == 'y':
                        import shutil
                        shutil.rmtree(output_dir)
                        print(f"✅ Deleted existing folder")
                    else:
                        print("❌ Cancelled. Please choose a different story name.")
                        sys.exit(0)
    
    elif mode == "2":
        print("\n" + "-" * 60)
        script_file = input("📄 Enter path to your script file: ").strip()
        script_path = Path(script_file)
        if not script_path.exists():
            print(f"❌ Script file not found: {script_path}")
            sys.exit(1)
        film_idea = "Script-based film"  # Placeholder
        
        # Ask for story name
        print("\n" + "-" * 60)
        print("📁 Story Name")
        print("  This will be used as the folder name for this project.")
        default_name = script_path.stem
        story_name_input = input(f"Enter story name (default: '{default_name}'): ").strip()
        story_name = story_name_input if story_name_input else default_name
        
        # Sanitize folder name
        story_name = "".join(c for c in story_name if c.isalnum() or c in ('_', '-', ' ')).rstrip()
        story_name = story_name.replace(" ", "_")
        
        output_dir = output_base / story_name
        
        # Check if folder exists (same logic as mode 1)
        if output_dir.exists():
            checkpoint = output_dir / "workflow_state.json"
            if checkpoint.exists():
                print(f"\n⚠️  Story folder '{story_name}' already exists!")
                resume_choice = input("   Resume from this checkpoint? (Y/n): ").strip().lower()
                if resume_choice != 'n':
                    resume_from = checkpoint
                    print(f"✅ Will resume from existing checkpoint")
                else:
                    overwrite = input("   Overwrite existing folder? (y/N): ").strip().lower()
                    if overwrite == 'y':
                        import shutil
                        shutil.rmtree(output_dir)
                        print(f"✅ Deleted existing folder")
                    else:
                        print("❌ Cancelled. Please choose a different story name.")
                        sys.exit(0)
    
    elif mode == "3" and resumable_projects:
        print("\n" + "-" * 60)
        print("📂 Resumable Projects:\n")
        for i, (path, state) in enumerate(resumable_projects, 1):
            phase = state.get('current_phase', 'UNKNOWN')
            iteration = state.get('iteration_count', 0)
            timestamp = state.get('timestamp', 'Unknown time')
            idea = state.get('film_idea', 'Unknown idea')
            # Truncate idea if too long
            if len(idea) > 50:
                idea = idea[:47] + "..."
            print(f"  {i}. {path.name}")
            print(f"     Phase: {phase}, Iteration: {iteration}")
            print(f"     Idea: {idea}")
            print(f"     Last updated: {timestamp[:19]}")
            print()
        
        project_idx = input(f"Select project (1-{len(resumable_projects)}): ").strip()
        try:
            idx = int(project_idx) - 1
            if 0 <= idx < len(resumable_projects):
                project_path, state = resumable_projects[idx]
                resume_from = project_path / "workflow_state.json"
                film_idea = state.get('film_idea', 'Resumed film')
                output_dir = project_path
                print(f"✅ Resuming from: {project_path}")
            else:
                print("❌ Invalid selection!")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid input!")
            sys.exit(1)
    
    else:
        print("❌ Invalid selection!")
        sys.exit(1)
    
    # Skip configuration prompts if resuming
    if resume_from:
        return {
            'idea': film_idea,
            'script': None,
            'duration': 60,
            'quality_threshold': 9.0,
            'max_iterations': 5,
            'output': output_dir,
            'verbose': False,
            'resume': resume_from
        }
    
    # Duration
    print("\n" + "-" * 60)
    print("⏱️  Target Duration")
    duration_input = input("Enter duration in seconds (default: 60): ").strip()
    duration = int(duration_input) if duration_input else 60
    
    # Quality threshold
    print("\n" + "-" * 60)
    print("⭐ Quality Threshold")
    print("  - 9.0 = Strict (default, may take longer)")
    print("  - 8.0 = Moderate (faster, good quality)")
    print("  - 7.0 = Lenient (quick results)")
    threshold_input = input("Enter threshold 0-10 (default: 9.0): ").strip()
    threshold = float(threshold_input) if threshold_input else 9.0
    
    # Max iterations
    print("\n" + "-" * 60)
    print("🔄 Maximum Iterations")
    print("  How many times should we try to improve the script?")
    iterations_input = input("Enter max iterations (default: 5): ").strip()
    max_iterations = int(iterations_input) if iterations_input else 5
    
    # Verbose mode
    print("\n" + "-" * 60)
    verbose_input = input("🔊 Enable verbose logging? (y/N): ").strip().lower()
    verbose = verbose_input == 'y'
    
    # Summary
    print("\n" + "=" * 60)
    print("  📋 Configuration Summary")
    print("=" * 60)
    if script_path:
        print(f"Mode: Refine existing script")
        print(f"Script: {script_path}")
    else:
        print(f"Mode: Create from idea")
        print(f"Idea: {film_idea}")
    print(f"Story Name: {story_name}")
    print(f"Duration: {duration}s")
    print(f"Quality Threshold: {threshold}/10")
    print(f"Max Iterations: {max_iterations}")
    print(f"Output: {output_dir}")
    print(f"Verbose: {verbose}")
    print("=" * 60)
    
    confirm = input("\n✅ Start production? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("❌ Cancelled.")
        sys.exit(0)
    
    return {
        'idea': film_idea,
        'script': script_path,
        'duration': duration,
        'quality_threshold': threshold,
        'max_iterations': max_iterations,
        'output': output_dir,
        'verbose': verbose,
        'resume': None
    }


def main():
    """Main CLI entry point"""
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        # Interactive mode
        options = interactive_menu()
        args = argparse.Namespace(**options)
    else:
        # Command-line argument mode
        parser = argparse.ArgumentParser(
        description="CINE-GENESIS: Autonomous Short Film Production System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog ="""
Examples:
  # Basic usage
  python main.py --idea "A robot learning to feel emotions"
  
  # With custom output directory and duration
  python main.py --idea "Space adventure" --output ./my_film --duration 30
  
  # Enable verbose logging
  python main.py --idea "Mystery thriller" --verbose
"""
    )
    
        parser.add_argument(
            '--idea',
            type=str,
            required=False,
            help='Film concept or idea (brief description). Required if --script not provided.'
        )
        
        parser.add_argument(
            '--script',
            type=Path,
            default=None,
            help='Path to existing script file to start with (skips initial writing, goes to refinement)'
        )
        
        parser.add_argument(
            '--output',
            type=Path,
            default=None,
            help='Output directory (default: ./output)'
        )
        
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='Target duration in seconds (default:60)'
        )
        
        parser.add_argument(
            '--quality-threshold',
            type=float,
            default=9.0,
            help='Quality threshold for approval (0-10, default: 9.0)'
        )
        
        parser.add_argument(
            '--max-iterations',
            type=int,
            default=5,
            help='Maximum iterations per phase (default: 5)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--resume',
            type=Path,
            default=None,
            help='Resume from checkpoint in specified output directory'
        )
        
        args = parser.parse_args()
        
        # Handle resume mode
        if args.resume:
            checkpoint_path = args.resume if args.resume.name == 'workflow_state.json' else args.resume / 'workflow_state.json'
            if not checkpoint_path.exists():
                parser.error(f"Checkpoint file not found: {checkpoint_path}")
            # Load checkpoint to get film idea and output dir
            import json
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            args.idea = state.get('film_idea', 'Resumed film')
            args.output = args.resume if args.resume.name != 'workflow_state.json' else args.resume.parent
            print(f"\n📂 Resuming from checkpoint: {checkpoint_path}")
            print(f"   Phase: {state.get('current_phase', 'UNKNOWN')}")
            print(f"   Iteration: {state.get('iteration_count', 0)}\n")
        else:
            # Validate that either idea or script is provided
            if not args.idea and not args.script:
                parser.error("Either --idea or --script must be provided")
        
        if args.script and not args.script.exists():
            parser.error(f"Script file not found: {args.script}")
    
    # Common validation and setup for both modes
    
    # Configure logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    logger = logging.getLogger(__name__)
    
    # Update config with CLI args
    if args.output:
        config.workflow.output_dir = args.output
    config.workflow.target_duration_seconds = args.duration
    config.quality.default_quality_threshold = args.quality_threshold
    config.quality.max_iterations_per_phase = args.max_iterations
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("\nPlease set the required API keys:")
        logger.error("  export GEMINI_API_KEY='your_key_here'")
        logger.error("\nOr create a .env file with:")
        logger.error("  GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Print banner
    print("=" * 60)
    print("  CINE-GENESIS: Autonomous Short Film Production")
    print("=" * 60)
    
    if args.script:
        print(f"\nStarting from Script: {args.script}")
        print("(Will refine and improve existing script)")
    else:
        print(f"\nFilm Idea: {args.idea}")
        print("(Will create script from scratch)")
    
    print(f"Target Duration: {args.duration}s")
    print(f"Quality Threshold: {args.quality_threshold}/10")
    print(f"Output Directory: {config.workflow.output_dir}")
    print("\n" + "=" * 60 + "\n")
    
    # Create orchestrator and run
    try:
        # Determine resume path
        resume_from = None
        if hasattr(args, 'resume') and args.resume:
            resume_from = args.resume if args.resume.name == 'workflow_state.json' else args.resume / 'workflow_state.json'
        
        orchestrator = WorkflowOrchestrator(
            film_idea=args.idea or "Script-based film",
            base_script_path=args.script,
            output_dir=config.workflow.output_dir,
            resume_from=resume_from
        )
        
        final_output = orchestrator.run()
        
        print("\n" + "=" * 60)
        print("  ✓ FILM PRODUCTION COMPLETE!")
        print("=" * 60)
        print(f"\nFinal output: {final_output}")
        print(f"All files saved to: {config.workflow.output_dir}")
        print()
        
    except KeyboardInterrupt:
        logger.warning("\nProduction interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nProduction failed: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
