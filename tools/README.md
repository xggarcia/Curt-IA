# CINE-GENESIS Tools

This directory contains standalone tools for AI media generation.

## Scripts

### `generate_ai_video.py`

Generates a full AI-animated video from a storyboard using local Stable Diffusion.

- **Usage**: `python tools/generate_ai_video.py`
- **Output**: `output/Dog_that_learns_to_speak/film_ai.mp4`
- **Requires**: GPU (recommended) or CPU (slow), `diffusers`, `transformers`, `torch`

### `check_local_sd.py`

Verifies that local Stable Diffusion is set up correctly and can generate a single test image.

- **Usage**: `python tools/check_local_sd.py`
- **Output**: `test_local_sd.png`

## Setup

Ensure you have the dependencies installed:

```bash
pip install -r requirements.txt
```
