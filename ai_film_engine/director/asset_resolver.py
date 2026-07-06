from pathlib import Path


class AssetResolver:
    def __init__(self, base_dir: str = "assets"):
        self.base_dir = Path(base_dir)

    def resolve_character_asset(self, name: str) -> Path:
        """Resolve a character's name to a master image path."""
        clean_name = name.lower().replace(" ", "_")
        return self.base_dir / "characters" / clean_name / "master.png"

    def resolve_location_asset(self, name: str) -> Path:
        """Resolve a location's name to a master image path."""
        clean_name = name.lower().replace(" ", "_")
        return self.base_dir / "locations" / clean_name / "master.png"

    def resolve_reference(self, ref_name: str) -> Path:
        """Helper to resolve any reference name to a target path."""
        # Try character path, otherwise default to location
        char_path = self.resolve_character_asset(ref_name)
        if char_path.parent.exists():
            return char_path
        return self.resolve_location_asset(ref_name)
