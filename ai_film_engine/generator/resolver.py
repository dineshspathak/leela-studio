import hashlib
from typing import Any

from pydantic import BaseModel


class MatchResult(BaseModel):
    matched: bool
    confidence: float  # 0.0 to 1.0
    match_level: (
        str  # exact_hash, metadata_match, reference_match, semantic_match, none
    )
    asset_path: str | None = None


class AssetResolver:
    def __init__(self, registry_db: Any = None):
        self.registry_db = registry_db

    def calculate_prompt_hash(self, prompt: str, neg_prompt: str = "") -> str:
        sha = hashlib.sha256()
        sha.update(prompt.encode("utf-8"))
        sha.update(neg_prompt.encode("utf-8"))
        return sha.hexdigest()

    def resolve_asset_matching(
        self,
        prompt: str,
        neg_prompt: str,
        references: list[str],
        metadata: dict[str, Any],
        registry_assets: list[dict[str, Any]],
    ) -> MatchResult:
        """Intelligent Asset Matching levels (Level 1: Exact Hash, Level 2: Metadata, Level 3: Reference, Level 4: Semantic)."""
        target_hash = self.calculate_prompt_hash(prompt, neg_prompt)

        # Level 1: Exact Hash Match
        for asset in registry_assets:
            if asset.get("prompt_hash") == target_hash:
                return MatchResult(
                    matched=True,
                    confidence=1.0,
                    match_level="exact_hash",
                    asset_path=asset.get("path"),
                )

        # Level 2: Metadata Match (similarity based on dimensions/durations)
        for asset in registry_assets:
            if (
                asset.get("resolution") == metadata.get("resolution")
                and abs(asset.get("duration", 0) - metadata.get("duration", 0)) < 0.1
                and asset.get("provider") == metadata.get("provider")
            ):
                return MatchResult(
                    matched=True,
                    confidence=0.8,
                    match_level="metadata_match",
                    asset_path=asset.get("path"),
                )

        # Level 3: Reference Image Match
        for asset in registry_assets:
            asset_refs = asset.get("references", [])
            if len(asset_refs) > 0 and any(r in references for r in asset_refs):
                return MatchResult(
                    matched=True,
                    confidence=0.6,
                    match_level="reference_match",
                    asset_path=asset.get("path"),
                )

        # Level 4: Semantic Similarity Match (mock fallback)
        for asset in registry_assets:
            if any(
                word in asset.get("prompt", "").lower()
                for word in prompt.lower().split()[:3]
            ):
                return MatchResult(
                    matched=True,
                    confidence=0.4,
                    match_level="semantic_match",
                    asset_path=asset.get("path"),
                )

        return MatchResult(matched=False, confidence=0.0, match_level="none")
