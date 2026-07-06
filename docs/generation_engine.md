# Generation Engine Specification

## 1. Overview
The Generation Engine automates the execution of story generation schedules. It coordinates:
- Resolving prompts, templates, and variable overrides.
- Scanning local asset registries for matching cached files.
- Formulating topological execution sequences.
- Triggering dynamic worker jobs and saving progress.

## 2. Quality Profiles
The engine supports multiple quality modes, scaling the output quality, duration, and target provider:
- **Draft**: Fastest execution, lowest resolution, target model PixVerse v1.
- **Standard**: Balance of cost and performance.
- **Cinematic**: Full HD resolution, target model PixVerse v2.
- **Premium**: Highest fidelity 4K generation, target model Google Veo.

## 3. CLI Commands
- `python main.py generate Episode001.json`: Start generation.
- `python main.py generate Episode001.json --resume`: Resume unfinished runs.
- `python main.py generate Episode001.json --dry-run`: Preview details.
- `python main.py analyze Episode001.json`: Perform dry run resource estimations.
