# CINE-GENESIS: Autonomous Short Film Production System

An AI-powered multi-agent system that autonomously produces short films from concept to final edit, with quality control through iterative evaluation and feedback loops.

## 🎬 Overview

CINE-GENESIS orchestrates a team of specialized AI agents to create short films:

- **Director**: Defines creative vision and breaks deadlocks
- **Coherence Manager**: Maintains visual consistency via "Visual Bible"
- **Scriptwriter**: Creates screenplay with feedback integration
- **Tribunal**: 3 critics evaluate quality (Technical, Narrative, Audience)
- **Storyboard/Animator/Audio/Editor**: (Framework ready for implementation)

## 🚀 Quick Start

### 1. Installation

```bash
cd Curt-IA
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run

```bash
python -m cine_genesis.main --idea "A robot learning to feel emotions" --duration 60
```

## 📋 Requirements

- **Required**: Google Gemini API key (for LLM and vision)
- **Optional**: Image/Video/Audio generation APIs (see `.env.example`)

## 🎯 Current Status

**Phase 1 Complete**: Script Generation with Quality Control

- ✅ Director vision definition
- ✅ Scriptwriter with iterative refinement
- ✅ 3-critic tribunal (Technical, Narrative, Audience)
- ✅ Voting system with 9/10 threshold
- ✅ Deadlock breaking protocol
- ✅ Visual Bible creation

**Upcoming Phases**:

- ⏳ Storyboard generation
- ⏳ Video animation (requires video API integration)
- ⏳ Audio generation and sync
- ⏳ Final editing and assembly

## 💡 Usage Examples

### Basic usage (create from idea)

```bash
python -m cine_genesis.main --idea "Mystery in a coffee shop"
```

### Start with existing script (refine and improve)

```bash
python -m cine_genesis.main --script ./examples/robot_music_box.txt --duration 60
```

### Custom settings

```bash
python -m cine_genesis.main \
  --idea "Space adventure with talking cats" \
  --duration 30 \
  --output ./my_films/space_cats \
  --quality-threshold 8.5 \
  --max-iterations 3
```

### Resume from checkpoint (after API quota interruption)

```bash
# Resume from previous session
python -m cine_genesis.main --resume ./output

# Or use interactive mode and select "Resume previous creation"
python -m cine_genesis.main
```

## 📁 Project Structure

```
cine_genesis/
├── agents/
│   ├── agent_base.py           # Base classes for all agents
│   ├── governance/
│   │   ├── director_agent.py
│   │   └── coherence_manager_agent.py
│   ├── creative/
│   │   └── scriptwriter_agent.py
│   ├── critics/
│   │   ├── technical_critic.py
│   │   ├── narrative_critic.py
│   │   └── audience_critic.py
│   └── postprod/
├── core/
│   ├── workflow_orchestrator.py
│   └── voting_system.py
├── utils/
│   └── api_clients.py
├── config.py
└── main.py
```

## 🔧 Configuration

Edit `cine_genesis/config.py` or use environment variables:

- `GEMINI_API_KEY`: Google Gemini API
- `STABILITY_API_KEY`: Image generation (optional)
- `RUNWAY_API_KEY`: Video generation (optional)
- `ELEVENLABS_API_KEY`: Text-to-speech (optional)

## 📊 Workflow

1. **Preparation**
   - Director defines genre, tone, pacing, message
   - Visual Bible created (after script approval)

2. **Scriptwriting** (Iterative)
   - Scriptwriter creates screenplay from idea OR refines provided base script
   - Director pre-filters for vision alignment
   - Tribunal evaluates (all must score ≥9/10)
   - If failed: feedback → revise → repeat
   - If 5 failures: Director deadlock protocol
   - **Checkpoint saved** after each iteration ⭐

3. **Resume Support** ⭐ NEW
   - Automatically saves progress after each phase
   - Resume with `--resume` flag or interactive menu
   - Skips completed phases, continues from interruption
   - Perfect for handling API quota limits

4. **Visualization** (Framework ready)
   - Storyboard agent creates visual prompts
   - Animator generates video clips
   - Critics evaluate visual quality

5. **Finalization** (Framework ready)
   - Editor assembles clips
   - Audio agent adds sound
   - Final tribunal review

## 🎬 Example Output

After running, find in `./output/`:

- `script_final.txt` - Approved screenplay
- `visual_bible.json` - Character/visual specifications
- `feedback_iteration_*.txt` - Tribunal feedback per iteration
- `workflow_state.json` - State for resumption (if interrupted)

## 🤝 Contributing

This is a research/educational project. Feel free to:

- Implement missing phases (storyboard, animation, audio, editing)
- Add new API integrations
- Improve critic evaluation logic
- Enhance Visual Bible consistency

## 📝 License

MIT License - See project root for details

## 🙏 Acknowledgments

Built using:

- Google Gemini AI
- Multi-agent AI architecture principles
- Film production best practices
