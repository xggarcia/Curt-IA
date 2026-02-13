# Quick Test Mode - Storyboard & Animation

## Purpose

Test storyboard and animation generation **without** running the full validation loop. Perfect for:

- Testing new features quickly
- Saving API calls
- Generating storyboards/videos from existing scripts

## Usage

### Option 1: Interactive Mode

```bash
python test_storyboard_animation.py
```

You'll be prompted for:

1. Script file path
2. Output directory (optional)

### Option 2: Command Line

```bash
python test_storyboard_animation.py <script_path> [output_dir]
```

**Example:**

```bash
python test_storyboard_animation.py output/CURT/final_script.txt test_output
```

## What It Does

1. ✅ Loads your existing script
2. ✅ Generates storyboard (1 API call)
3. ✅ Creates MP4 animation (0 API calls)
4. ✅ Saves to output directory

**Total API calls: 1**

## Output Files

```
test_output/
├── storyboard.txt
└── test_film.mp4
```

## Example Usage

### Test with CURT script

```bash
python test_storyboard_animation.py output/CURT/script_draft_5.txt curt_test
```

### Test with any script

```bash
python test_storyboard_animation.py my_script.txt my_test
```

## Requirements

Make sure dependencies are installed:

```bash
pip install -r requirements.txt
```

Specifically needed:

- `moviepy` - For video creation
- `pillow` - For image generation
- `numpy` - For array operations

## Troubleshooting

**"Script file not found"**

- Check the path is correct
- Use absolute path if needed

**"Animation failed"**

- Run: `pip install moviepy pillow numpy`
- MoviePy will auto-install ffmpeg

**"API quota exceeded"**

- Wait 24 hours for quota reset
- Or add more API keys to `.env`

## API Usage

- Storyboard generation: **1 call**
- Animation: **0 calls** (local processing)

Much more efficient than full validation loop!
