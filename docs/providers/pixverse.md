# PixVerse Provider Architecture & Documentation

This document explains the integration of the PixVerse Provider within the LEELA Studio Provider architecture.

---

## 🏗️ Provider Architecture

```mermaid
graph TD
    Pipeline["Orchestrator / Pipeline"]
    BaseProvider["BaseProvider (Interface)"]
    PixVerseProvider["PixVerseProvider (Concrete)"]
    SDK["PixVerse SDK (jobs/downloads/client)"]

    Pipeline --> BaseProvider
    BaseProvider <|-- PixVerseProvider
    PixVerseProvider --> SDK
```

The LEELA Studio leverages an abstract provider architecture (`BaseProvider`) to support multiple media production backend integrations seamlessly.

### `BaseProvider` Interface
Defined in `providers/base.py`, it forces all providers (PixVerse, etc.) to expose the following async contracts:
- `authenticate() -> bool`
- `generate_image(prompt, aspect_ratio) -> VideoJob`
- `generate_image_to_video(request) -> VideoJob`
- `generate_text_to_video(request) -> VideoJob`
- `get_task_status(task_id) -> VideoJob`
- `download_asset(...) -> Path`
- `cancel_task(task_id) -> bool`
- `health_check() -> bool`

### `PixVerseProvider` Implementation
Implemented in `providers/pixverse.py`, it maps the abstract methods directly to the underlying PixVerse SDK.

---

## 🔒 Authentication Flow
The provider delegates authorization checks to the SDK's `authenticate()` method which verifies the existence of valid configuration variables (e.g. `api_key`).

---

## 🔄 Request, Polling & Download Lifecycle
- **Requests**: Handled by passing strongly-typed Pydantic request models (`TextToVideoRequest`, `ImageToVideoRequest`) to the underlying SDK.
- **Polling**: Handled by passing task IDs to the SDK status checker.
- **Downloads**: Structured outputs are saved under `downloads/Episode[XXX]/Scene[XXX]/Shot[XXX].mp4` with a matching `Shot[XXX]_asset.json` containing generation metadata.
