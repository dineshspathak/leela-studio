from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ai_film_engine.core.episodes.schemas import GlobalDefaults, Shot


class PromptBuilder:
    def __init__(self, templates_dir: str = "ai_film_engine/director/prompt_templates"):
        self.templates_dir = Path(templates_dir)
        if not self.templates_dir.exists():
            self.templates_dir = Path("ai_film_engine/director/prompt_templates")
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))

    def build_prompt(
        self, shot: Shot, defaults: GlobalDefaults, lighting: str | None = None
    ) -> str:
        """Render the appropriate prompt template based on generation_type."""
        # Select Jinja template
        if shot.generation_type == "text_to_image":
            template_name = "text_to_image.jinja"
        elif shot.generation_type == "image_to_video":
            template_name = "image_to_video.jinja"
        elif shot.generation_type == "text_to_video":
            template_name = "text_to_video.jinja"
        else:
            # Fallback/default if unrecognized type
            return shot.prompt

        template = self.env.get_template(template_name)

        # Populate context variables, falling back to global defaults
        context = {
            "prompt": shot.prompt,
            "location": shot.location or "unspecified environment",
            "camera": shot.camera or defaults.camera_style,
            "lighting": lighting or defaults.cinematic_profile or "dramatic lighting",
            "visual_style": defaults.visual_style,
            "cinematic_profile": defaults.cinematic_profile,
            "motion": shot.motion or "subtle realistic motion",
        }

        return template.render(context).strip()

    def build_negative_prompt(self, shot: Shot, defaults: GlobalDefaults) -> str:
        """Return shot's negative prompt or fallback to the global defaults."""
        return shot.negative_prompt or defaults.negative_prompt
