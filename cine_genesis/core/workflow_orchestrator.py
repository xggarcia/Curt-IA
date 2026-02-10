"""
Workflow Orchestrator - Manages the end-to-end film production pipeline
"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from cine_genesis.config import config
from cine_genesis.utils.api_clients import GeminiClient
from cine_genesis.agents.governance.director_agent import DirectorAgent
from cine_genesis.agents.governance.coherence_manager_agent import CoherenceManagerAgent
from cine_genesis.agents.creative.scriptwriter_agent import ScriptwriterAgent
from cine_genesis.agents.critics.technical_critic import TechnicalCriticAgent
from cine_genesis.agents.critics.narrative_critic import NarrativeCriticAgent
from cine_genesis.agents.critics.audience_critic import AudienceCriticAgent
from cine_genesis.core.voting_system import VotingSystem, Feedback

logger = logging.getLogger(__name__)


@dataclass
class WorkflowState:
    """Track workflow state across phases"""
    current_phase: str = "INIT"
    iteration_count: int = 0
    script: Optional[str] = None
    visual_bible: Optional[Dict] = None
    storyboard: Optional[Dict] = None
    assets: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.assets is None:
            self.assets = {}


class WorkflowOrchestrator:
    """
    Orchestrates the complete CINE-GENESIS workflow
    Manages agents, voting, and iterative refinement
    """
    
    def __init__(
        self,
        film_idea: str,
        output_dir: Optional[Path] = None,
        gemini_client: Optional[GeminiClient] = None,
        base_script_path: Optional[Path] = None
    ):
        self.film_idea = film_idea
        self.base_script_path = base_script_path
        self.output_dir = output_dir or config.workflow.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load base script if provided
        if self.base_script_path:
            logger.info(f"Loading base script from: {self.base_script_path}")
            self.base_script = self.base_script_path.read_text(encoding='utf-8')
            logger.info(f"Base script loaded ({len(self.base_script)} characters)")
        else:
            self.base_script = None
        
        # API client with key rotation support
        api_keys = config.api.get_all_gemini_keys()
        self.gemini_client = gemini_client or GeminiClient(
            api_key=api_keys,  # Pass list of keys
            model=config.api.gemini_model,
            requests_per_minute=config.api.gemini_requests_per_minute
        )
        
        # Initialize agents
        logger.info("Initializing agents...")
        self.director = DirectorAgent(self.gemini_client)
        self.coherence_manager = CoherenceManagerAgent(self.gemini_client)
        self.scriptwriter = ScriptwriterAgent(self.gemini_client)
        
        # Critics
        self.technical_critic = TechnicalCriticAgent(self.gemini_client)
        self.narrative_critic = NarrativeCriticAgent(self.gemini_client)
        self.audience_critic = AudienceCriticAgent(self.gemini_client)
        
        # Voting system
        self.voting_system = VotingSystem()
        
        # State
        self.state = WorkflowState()
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete workflow
        
        Returns:
            Dictionary with final assets and metadata
        """
        logger.info(f"Starting CINE-GENESIS workflow for: {self.film_idea}")
        
        try:
            # Phase A: Preparation
            self._phase_preparation()
            
            # Phase B: Scriptwriting
            self._phase_scriptwriting()
            
            # Phase C: Visualization (TODO)
            # self._phase_visualization()
            
            # Phase D: Finalization (TODO)
            # self._phase_finalization()
            
            logger.info("=" * 60)
            logger.info("✅ Production complete!")
            logger.info(f"Output saved to: {self.output_dir}")
            logger.info("=" * 60)
            
            return {
                "output_dir": self.output_dir,
                "script": self.state.script,
                "visual_bible": self.state.visual_bible,
                "status": "complete"
            }
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            raise
    
    def _phase_preparation(self):
        """Phase A: Director vision and Visual Bible"""
        logger.info("=== PHASE A: PREPARATION ===")
        self.state.current_phase = "PREPARATION"
        
        # Director defines vision
        logger.info("Director defining creative vision...")
        vision = self.director.define_vision(self.film_idea)
        
        # Coherence Manager creates Visual Bible (for visual phases)
        # For now, we'll skip this for pure script generation
        # self.state.visual_bible = self.coherence_manager.create_visual_bible(
        #     self.film_idea, vision
        # )
        
        logger.info("Preparation phase complete.\n")
    
    def _phase_scriptwriting(self):
        """Phase B: Scriptwriting with iterative refinement"""
        logger.info("=== PHASE B: SCRIPTWRITING ===")
        self.state.current_phase = "SCRIPTWRITING"
        self.state.iteration_count = 0
        
        # Check if we're starting from a base script
        is_revision = self.base_script is not None
        
        while self.state.iteration_count < config.quality.max_iterations_per_phase:
            self.state.iteration_count += 1
            logger.info(f"\n--- Iteration {self.state.iteration_count} ---")
            
            # Generate or refine script
            logger.info("Scriptwriter working on screenplay...")
            if is_revision and self.state.iteration_count == 1:
                # First iteration with base script - start with loaded script
                script = self.scriptwriter.execute(
                    input_data=self.base_script,
                    context={
                        "vision": {},
                        "is_revision": True,
                        "target_duration": config.workflow.target_duration_seconds
                    }
                )
            else:
                # Normal generation or subsequent revisions
                if self.state.iteration_count > 1:
                    # Revision with feedback
                    script = self.scriptwriter.execute(
                        input_data=self.state.script or self.film_idea,
                        context={
                            "vision": {},
                            "is_revision": True,
                            "target_duration": config.workflow.target_duration_seconds
                        }
                    )
                else:
                    # Initial generation
                    script = self.scriptwriter.execute(
                        input_data=self.film_idea,
                        context={
                            "vision": {},
                            "is_revision": False,
                            "target_duration": config.workflow.target_duration_seconds
                        }
                    )
            
            # Save draft
            draft_path = self.output_dir / f"script_draft_{self.state.iteration_count}.txt"
            draft_path.write_text(script, encoding='utf-8')
            logger.info(f"Saved draft to: {draft_path}")
            
            # Director review
            logger.info("Director reviewing script...")
            director_approved, director_feedback = self.director.review_creative_work(
                work=script,
                work_type="script"
            )
            
            if not director_approved:
                logger.warning(f"Director rejected: {director_feedback}")
                logger.warning("Continuing to critics for detailed feedback...")
            else:
                logger.info("Director approved. Sending to Tribunal...")
            
            # Tribunal evaluation
            feedbacks = []
            
            logger.info("  Technical Critic evaluating...")
            tech_feedback = self.technical_critic.evaluate(script, {"type": "script"})
            logger.info(f"    Score: {tech_feedback.score}/10")
            feedbacks.append(tech_feedback)
            
            logger.info("  Narrative Critic evaluating...")
            narr_feedback = self.narrative_critic.evaluate(script, {"type": "script"})
            logger.info(f"    Score: {narr_feedback.score}/10")
            feedbacks.append(narr_feedback)
            
            logger.info("  Audience Critic evaluating...")
            aud_feedback = self.audience_critic.evaluate(script, {"type": "script"})
            logger.info(f"    Score: {aud_feedback.score}/10")
            feedbacks.append(aud_feedback)
            
            # Voting
            logger.info("-" * 60)
            result = self.voting_system.collect_votes(feedbacks)
            
            # Save feedback - format the result manually
            feedback_report = f"""ITERATION {self.state.iteration_count} - TRIBUNAL VERDICT
============================================================

RESULT: {'APPROVED ✅' if result.passed else 'REJECTED ❌'}
AVERAGE SCORE: {result.average_score:.1f}/10
THRESHOLD: {self.voting_system.quality_threshold}/10

INDIVIDUAL SCORES:
{chr(10).join([f'  - {name}: {score:.1f}/10' for name, score in result.individual_scores.items()])}

FAILING CRITICS: {', '.join(result.failing_critics) if result.failing_critics else 'None'}

AGGREGATED FEEDBACK:
{result.aggregated_feedback}
"""
            
            feedback_path = self.output_dir / f"feedback_iteration_{self.state.iteration_count}.txt"
            feedback_path.write_text(feedback_report, encoding='utf-8')
            
            if result.passed:
                # SUCCESS!
                logger.info(f"✅ SCRIPT APPROVED (Score: {result.average_score:.1f}/10)")
                self.state.script = script
                
                # Save final script
                final_path = self.output_dir / "final_script.txt"
                final_path.write_text(script, encoding='utf-8')
                logger.info(f"Final script saved to: {final_path}\n")
                return
            
            # FAILED - give feedback and iterate
            logger.info(f"Script needs revision. Failing critics: {result.failing_critics}")
            logger.info("")
        
        # Max iterations reached - DEADLOCK
        logger.warning("⚠️  Maximum iterations reached!")
        logger.info("Executing deadlock breaking protocol...")
        
        action, data = self.director.execute_deadlock_protocol(
            script,
            "script", 
            feedbacks,
            self.state.iteration_count
        )
        
        if action == "rewrite":
            logger.info("Director decided: COMPLETE REWRITE")
            self.state.script = data
        else:
            logger.info(f"Director decided: LOWER THRESHOLD to {data}")
            self.state.script = script
        
        # Save final version regardless
        final_path = self.output_dir / "final_script.txt"
        final_path.write_text(self.state.script, encoding='utf-8')
        logger.info(f"Final script (emergency approved) saved to: {final_path}\n")
    
    def _get_latest_feedback(self) -> str:
        """Get formatted feedback from last iteration"""
        feedback_path = self.output_dir / f"feedback_iteration_{self.state.iteration_count - 1}.txt"
        if feedback_path.exists():
            return feedback_path.read_text(encoding='utf-8')
        return ""
