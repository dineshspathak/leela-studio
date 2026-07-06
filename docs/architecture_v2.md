# V2 Architecture Specification

## 1. Directory Layout
```text
LEELA-STUDIOS/
├── main.py                    # Multi-command Typer CLI (compile, render, project, etc.)
├── ai_film_engine/            # Decoupled core engine module (zero story concepts)
│   ├── core/                  # Project, workspace, job, storage, database abstractions
│   ├── director/              # Storyboard, prompts compiler, and continuity quality validation
│   ├── orchestrator/          # Task queue execution, workers, and checkpoint managers
│   ├── renderer/              # Timelines, subtitle engines, audio duck mixers, FFmpeg render
│   ├── providers/             # Base provider layouts & PixVerse client wrapper
│   ├── plugins/               # Extensible effects/transitions plugins
│   ├── budget/                # Credit counters and limits
│   └── workflows/             # DAG based job schedulers
├── workspace/                 # Workspace folder isolation layer
│   ├── shared/                # Global actors, music, SFX and Loras
│   └── projects/              # Projects workspace folder
│       └── leela/             # Leela project isolation (project.yaml, assets, episodes)
└── tests/                     # Unit test suites
```

## 2. Abstractions
- **`ProjectManager`**: Dynamically creates, loads, lists, and deletes projects within the workspace.
- **`BaseStorage` / `LocalStorage`**: Abstract read/write layer isolating the filesystem.
- **`BaseDatabase` / `SQLiteDatabase`**: Abstract key-value metadata registry.
- **`PluginRegistry`**: Dynamically registers third-party providers/effects at runtime.

## 3. Configuration Layer Overrides
Configs are resolved hierarchically with children overriding parent values:
`Global Config` ➔ `Project Config` ➔ `Episode Config` ➔ `Scene Config` ➔ `Shot Config`
