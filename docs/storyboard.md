# LEELA Studio Storyboard Documentation

The Storyboard compiles the designed shots list into visual formats to represent a professional film storyboard.

---

## 📋 Storyboard Formats
1. **`Storyboard.json`**: Structural JSON details containing metadata, prompts, and credit counts.
2. **`Storyboard.md`**: Markdown tables detailing framing, motion, and lens options.
3. **`Storyboard.pdf`**: Programmatically generated document using ReportLab compiling page-by-page shot logs, lens details, and placeholders.

---

## 💰 Dynamic Credit Optimizer
The Director Engine validates compiled shot lists against the Episode Budget limit:
1. **Cost Check**: Aggregates expected credits.
2. **First Pass Optimization**: Downgrades unimportant `IMPORTANT` or `HERO` shots to `BACKGROUND` static fallbacks.
3. **Second Pass Optimization**: Merges contiguous background shots containing identical prompts and locations into single compiled units to conserve resource credits.

---

## 🎨 Scene Rhythm Engine
Ensures sequential shot variations to prevent monotony:
- Alternates durations, camera distances (close, medium, wide), and camera motion dynamics.
- Diversifies emotional states matching narrative peaks.
