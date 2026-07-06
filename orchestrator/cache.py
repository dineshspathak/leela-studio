import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


class AssetRegistry:
    def __init__(
        self,
        db_path: str = "cache/asset_registry.db",
        json_index_path: str = "assets/index.json",
    ):
        self.db_path = Path(db_path)
        self.json_index_path = Path(json_index_path)

        # Init DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                hash TEXT PRIMARY KEY,
                path TEXT,
                metadata TEXT
            )
            """)
        conn.commit()
        conn.close()

    def generate_prompt_hash(self, job: dict[str, Any]) -> str:
        """Create SHA256 hash including prompt, negative_prompt, references, etc."""
        # Clean inputs
        prompt = job.get("prompt", "")
        neg_prompt = job.get("negative_prompt", "")
        references = "".join(sorted(job.get("references", [])))
        duration = str(job.get("duration", 5))
        resolution = str(job.get("resolution", "720p"))
        provider = job.get("provider", "pixverse")
        model = job.get("model", "v6")
        aspect_ratio = job.get("aspect_ratio", "16:9")

        raw_str = f"{prompt}|{neg_prompt}|{references}|{duration}|{resolution}|{provider}|{model}|{aspect_ratio}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def get_cached_asset(self, prompt_hash: str) -> str | None:
        """Check SQLite database for existing asset path by prompt hash."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM assets WHERE hash = ?", (prompt_hash,))
        row = cursor.fetchone()
        conn.close()

        if row:
            path_str = row[0]
            # Ensure file actually exists locally
            if Path(path_str).exists():
                return path_str
        return None

    def register_asset(
        self,
        prompt_hash: str,
        path: Path,
        job_info: dict[str, Any],
        metadata: dict[str, Any],
    ):
        """Save asset mapping to SQLite and append metadata to assets/index.json."""
        path_str = str(path)

        # 1. Save to SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO assets (hash, path, metadata) VALUES (?, ?, ?)",
            (prompt_hash, path_str, json.dumps(metadata)),
        )
        conn.commit()
        conn.close()

        # 2. Save to assets/index.json
        self.json_index_path.parent.mkdir(parents=True, exist_ok=True)
        index_data: list[dict[str, Any]] = []

        if self.json_index_path.exists():
            try:
                with open(self.json_index_path, encoding="utf-8") as f:
                    index_data = json.load(f)
            except Exception:
                index_data = []

        # Find duplicate in JSON list and update or append
        existing_idx = next(
            (
                i
                for i, x in enumerate(index_data)
                if x.get("prompt_hash") == prompt_hash
            ),
            None,
        )

        record = {
            "asset_id": job_info.get("job_id", ""),
            "episode": job_info.get("episode_id", ""),
            "scene": job_info.get("scene_id", ""),
            "shot": job_info.get("shot_id", ""),
            "provider": metadata.get("provider", "pixverse"),
            "model": "v6",
            "prompt_hash": prompt_hash,
            "created_at": metadata.get("created_at", ""),
            "path": path_str,
            "resolution": metadata.get("resolution", "720p"),
            "duration": metadata.get("duration", 5),
            "references": metadata.get("references", []),
            "tags": job_info.get("tags", []),
        }

        if existing_idx is not None:
            index_data[existing_idx] = record
        else:
            index_data.append(record)

        with open(self.json_index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
