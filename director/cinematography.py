from typing import Any

from director.camera import CameraEngine
from director.composition import CompositionEngine
from director.emotions import EmotionsEngine
from director.language import CinematicLanguageEngine
from director.lighting import LightingEngine
from director.motion import MotionEngine


class CinematographyEngine:
    def __init__(self):
        self.camera = CameraEngine()
        self.lighting = LightingEngine()
        self.emotions = EmotionsEngine()
        self.composition = CompositionEngine()
        self.motion = MotionEngine()
        self.language = CinematicLanguageEngine()

    def design_shot(
        self,
        shot_prompt: str,
        importance: str,
        time_of_day: str = "day",
        environment: str = "outdoor",
        is_action: bool = False,
    ) -> dict[str, Any]:
        """Orchestrate all director sub-engines to design a complete shot."""
        # 1. Camera setups
        cam_setup = self.camera.recommend_setup(importance, is_action)
        framing = cam_setup["framing"]
        movement = cam_setup["movement"]

        # 2. Lighting setup
        light = self.lighting.recommend_lighting(time_of_day, environment)

        # 3. Emotion setup
        emotion = self.emotions.recommend_emotion(shot_prompt)

        # 4. Composition setup
        comp = self.composition.recommend_composition(framing)

        # 5. Motion setup
        is_storm = "storm" in environment.lower() or "rain" in shot_prompt.lower()
        mot = self.motion.recommend_motion(framing, is_storm)

        # 6. Format to professional cinematic language
        cinematic_prompt = self.language.format_shot_description(
            framing=framing,
            movement=movement,
            lighting=light,
            composition=comp,
            motion=mot,
            emotion=emotion,
        )

        # 7. Generate Negative Prompt
        negative_prompt = "ugly, deformed, blurry, low resolution, watermark"

        return {
            "framing": framing,
            "movement": movement,
            "lighting": light,
            "emotion": emotion,
            "composition": comp,
            "motion": mot,
            "cinematic_prompt": cinematic_prompt,
            "negative_prompt": negative_prompt,
        }
