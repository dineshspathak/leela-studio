# Vision Document: AI Film Operating System (V2)

## 1. Platform Philosophy
The platform is designed as a project-agnostic **AI Film Operating System**. It moves away from story-specific references (like Krishna or Devaki) and models filmmaking through generic structural concepts:
- **Episodes, Scenes, and Shots** as hierarchical layout representations.
- **Universal Asset Model**: All entities (Images, Videos, Audios, LoRAs, Prompts) inherit from a base `Asset` model.
- **Dynamic Job Engine**: Every execution step (image/video generation, upscaling, rendering, lip-sync, voiceovers) is a unified `Job` subclass.

## 2. Dynamic Plugin Architecture
Inspired by VS Code, the platform uses an extensible registry system. Developers can register custom:
- **AI Providers** (Google Veo, Runway, PixVerse, ComfyUI)
- **Transitions & Visual Effects**
- **Voice & Music Engines**
- **LLM/Image/Video models**

This ensures the core engine remains completely untouched when adding future models or providers.

## 3. Graph Workflows
Production pipelines are modeled as directed acyclic graphs (DAGs) of `Job` nodes. The Workflow Engine resolves dependencies topologically, enabling automated step-by-step filmmaking from story processing to final MP4 exports.
