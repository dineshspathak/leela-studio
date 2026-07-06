from typing import ClassVar


class CinematicLanguageEngine:
    LENS_MAP: ClassVar[dict[str, str]] = {
        "close up": "85mm portrait lens, shallow depth of field",
        "medium": "50mm prime lens, natural depth of field",
        "wide": "35mm anamorphic wide lens, deep focus",
        "extreme wide": "24mm ultra-wide lens, cinematic landscape scale",
        "over shoulder": "85mm over-the-shoulder emotional framing, shallow depth of field",
        "bird eye": "high angle bird's-eye perspective, overhead wide dynamic view",
        "low angle": "24mm low-angle heroic composition, dramatic scale",
        "high angle": "50mm high-angle vulnerable perspective",
    }

    MOVEMENT_MAP: ClassVar[dict[str, str]] = {
        "push in": "slow cinematic push-in tracking shot",
        "push out": "slow cinematic pull-back reveal tracking shot",
        "pan left": "controlled camera pan left panning shot",
        "pan right": "controlled camera pan right panning shot",
        "crane": "crane down reveal crane camera shot",
        "handheld": "organic handheld camera shake motion, realistic shoulder mount",
        "locked": "static tripod lock-down shot, absolutely stable framing",
        "dolly": "smooth horizontal dolly tracking shot along tracks",
    }

    LIGHTING_MAP: ClassVar[dict[str, str]] = {
        "golden hour": "sunset golden hour light, warm side-lit volumetric glows",
        "moonlight": "soft volumetric moonlight, cool ambient cyan tones with deep shadows",
        "torch": "flickering torch light, high contrast chiaroscuro shadow play",
        "storm": "dark storm atmosphere with dramatic volumetric lightning rim flashes",
        "volumetric": "volumetric light shafts casting god-rays through atmospheric haze",
        "soft": "diffused soft light, low contrast beauty lighting",
        "hard": "harsh hard lighting casting sharp defined cinematic shadows",
    }

    def format_shot_description(
        self,
        framing: str,
        movement: str,
        lighting: str,
        composition: str,
        motion: str,
        emotion: str,
    ) -> str:
        """Combine raw inputs into professional cinematic director-speak."""
        lens = self.LENS_MAP.get(framing.lower(), "50mm lens")
        move_desc = self.MOVEMENT_MAP.get(movement.lower(), movement)
        light_desc = self.LIGHTING_MAP.get(lighting.lower(), lighting)

        return (
            f"Framing: {lens}. "
            f"Camera Movement: {move_desc}. "
            f"Lighting: {light_desc}. "
            f"Composition: {composition}. "
            f"Key Motion: {motion}. "
            f"Emotional Resonance: {emotion}."
        )
