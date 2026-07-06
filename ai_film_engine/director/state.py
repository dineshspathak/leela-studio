from typing import Any

from pydantic import BaseModel, Field


class CharacterState(BaseModel):
    name: str
    emotion: str = "neutral"
    location: str = "unspecified"
    costume: str = "default"
    injuries: str = "none"
    state_condition: str = "dry"  # dry, wet, dusty, muddy
    holding_objects: list[str] = Field(default_factory=list)
    pose: str = "standing"
    facial_expression: str = "calm"


class EnvironmentState(BaseModel):
    location: str = "unspecified"
    storm_intensity: str = "none"  # none, mild, severe
    rain: str = "none"  # none, drizzle, heavy
    fog: str = "none"  # none, light, dense
    fire: str = "none"  # none, torches, raging
    torch_brightness: str = "normal"
    time_of_day: str = "day"  # morning, day, golden_hour, night
    moon_position: str = "unspecified"
    river_level: str = "normal"  # low, normal, overflowing


class StateEngine:
    def __init__(self):
        self.character_states: dict[str, CharacterState] = {}
        self.environment_state: EnvironmentState = EnvironmentState()
        self.warnings: list[str] = []

    def register_character(self, name: str, costume: str = "default"):
        if name not in self.character_states:
            self.character_states[name] = CharacterState(name=name, costume=costume)

    def transition_state(self, shot_info: dict[str, Any]) -> list[str]:
        """Update states and return list of continuity violation warnings."""
        warnings: list[str] = []
        shot_id = shot_info.get("shot_id", "")

        # 1. Update Environment State
        env_updates = shot_info.get("environment_updates", {})
        for k, v in env_updates.items():
            if hasattr(self.environment_state, k):
                old_v = getattr(self.environment_state, k)
                if old_v != v:
                    # Validate logical jumps
                    if k == "storm_intensity" and old_v == "none" and v == "severe":
                        warnings.append(
                            f"Environment jump warning in Shot {shot_id}: Storm jumped from 'none' to 'severe' without transition."
                        )
                    setattr(self.environment_state, k, v)

        # 2. Update Character States
        shot_chars = shot_info.get("characters", [])
        char_updates = shot_info.get("character_updates", {})

        for char_name in shot_chars:
            if char_name not in self.character_states:
                # Lazy register
                self.register_character(char_name)

            state = self.character_states[char_name]

            # Apply shot updates if any
            updates = char_updates.get(char_name, {})
            for k, v in updates.items():
                if hasattr(state, k):
                    old_val = getattr(state, k)
                    if old_val != v:
                        # Costume change checks
                        if k == "costume":
                            warnings.append(
                                f"Character continuity warning in Shot {shot_id}: Costume for '{char_name}' changed from '{old_val}' to '{v}'."
                            )
                        # State conditions change checks
                        if (
                            k == "state_condition"
                            and old_val == "dry"
                            and v == "wet"
                            and self.environment_state.rain == "none"
                        ):
                            warnings.append(
                                f"Character wetness mismatch in Shot {shot_id}: '{char_name}' became wet but environment rain is none."
                            )
                        setattr(state, k, v)

        return warnings
