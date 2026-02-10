# CINE-GENESIS Interactive Mode Quick Guide

## 🎮 Two Ways to Use

### 1. Interactive Mode (New! Easiest)

Simply run without any arguments:

```bash
python main.py
```

The program will guide you through all options step-by-step!

### 2. Command-Line Mode (Advanced)

Provide all options at once:

```bash
python main.py --idea "Your film concept" --duration 60
```

---

## 📺 Interactive Menu Walkthrough

When you run `python main.py`, you'll see:

```
============================================================
  🎬 CINE-GENESIS Interactive Menu
============================================================

📝 How do you want to start?
  1. Create from idea (I have a concept)
  2. Refine existing script (I have a script file)

Select mode (1 or 2): _
```

### Step-by-Step:

1. **Choose Mode** (1 or 2)
   - Option 1: You have a film idea/concept
   - Option 2: You have an existing script file

2. **Enter Film Idea or Script Path**
   - Mode 1: Type your idea (e.g., "A robot learns emotions")
   - Mode 2: Enter file path (e.g., `./my_script.txt`)

3. **Set Duration** (default: 60)
   - Target length in seconds

4. **Set Quality Threshold** (default: 9.0)
   - 9.0 = Strict (best quality, may iterate more)
   - 8.0 = Moderate (good balance)
   - 7.0 = Lenient (fast results)

5. **Set Max Iterations** (default: 5)
   - How many revision attempts allowed

6. **Set Output Directory** (default: `./output`)
   - Where to save results

7. **Enable Verbose Logging?** (y/N)
   - Shows detailed AI processing logs

8. **Review Configuration Summary**
   - All your choices displayed

9. **Confirm to Start** (Y/n)
   - Type Y to begin production!

---

## 💡 Example Interactive Session

```
Select mode (1 or 2): 1

💡 Enter your film idea: A lonely robot finds a music box

⏱️  Target Duration
Enter duration in seconds (default: 60): 30

⭐ Quality Threshold
Enter threshold 0-10 (default: 9.0): 8.0

🔄 Maximum Iterations
Enter max iterations (default: 5): 3

📁 Output Directory
Enter output path (default: ./output):

🔊 Enable verbose logging? (y/N): n

============================================================
  📋 Configuration Summary
============================================================
Mode: Create from idea
Idea: A lonely robot finds a music box
Duration: 30s
Quality Threshold: 8.0/10
Max Iterations: 3
Output: output
Verbose: False
============================================================

✅ Start production? (Y/n):
```

---

## 🚀 Quick Start (Recommended First Run)

1. Open terminal in the `Curt-IA` directory
2. Run: `python main.py`
3. Follow the prompts:
   - Select **1** (Create from idea)
   - Enter: `"A cat discovers superpowers"`
   - Duration: `30`
   - Threshold: `8.0`
   - Iterations: `2`
   - Output: _press Enter for default_
   - Verbose: `n`
   - Start: `Y`

This will complete in 3-5 minutes!

---

## 📝 Tips

- **First time?** Use lower threshold (8.0) and fewer iterations (2-3) for faster testing
- **Have a script?** Choose option 2 and point to your `.txt` file
- **Want control?** Still use command-line: `python main.py --idea "..." --duration 30`
- **Empty input = default**: Just press Enter to use default values
