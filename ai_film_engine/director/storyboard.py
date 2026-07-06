import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class StoryboardBuilder:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_storyboard_files(self, episode_title: str, shots: list[dict[str, Any]]):
        """Export Storyboard.json, Storyboard.md, and Storyboard.pdf."""
        # 1. Save JSON
        json_path = self.output_dir / "Storyboard.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"episode_title": episode_title, "shots": shots}, f, indent=2)

        # 2. Save Markdown
        md_path = self.output_dir / "Storyboard.md"
        self._build_markdown(episode_title, shots, md_path)

        # 3. Save PDF
        pdf_path = self.output_dir / "Storyboard.pdf"
        self._build_pdf(episode_title, shots, pdf_path)

    def _build_markdown(self, title: str, shots: list[dict[str, Any]], dest: Path):
        lines = [
            f"# Storyboard - {title}",
            "",
            "| Shot ID | Thumbnail | Camera & Lens | Lighting | Motion | Emotion | Credits |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]

        for s in shots:
            job_id = s.get("job_id", "")
            cam = f"**{s.get('framing', '')}**<br>{s.get('movement', '')}"
            light = s.get("lighting", "")
            motion = s.get("motion", "")
            emotion = s.get("emotion", "")
            credits = s.get("credits", 1)

            lines.append(
                f"| {job_id} | [Thumbnail Placeholder] | {cam} | {light} | {motion} | {emotion} | {credits} |"
            )

        with open(dest, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _build_pdf(self, title: str, shots: list[dict[str, Any]], dest: Path):
        doc = SimpleDocTemplate(str(dest), pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=15,
        )

        shot_title_style = ParagraphStyle(
            "ShotTitle",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2B6CB0"),
            spaceAfter=10,
        )

        body_style = styles["Normal"]

        story = []

        # Cover/Title
        story.append(Paragraph("LEELA Studio Storyboard", title_style))
        story.append(Paragraph(f"Episode: {title}", styles["Heading3"]))
        story.append(Spacer(1, 20))

        for idx, s in enumerate(shots):
            job_id = s.get("job_id", f"Shot {idx+1}")
            story.append(Paragraph(f"Scene/Shot: {job_id}", shot_title_style))

            # Setup metadata table
            data = [
                [
                    Paragraph("<b>Camera & Lens</b>", body_style),
                    Paragraph(s.get("framing", ""), body_style),
                ],
                [
                    Paragraph("<b>Movement</b>", body_style),
                    Paragraph(s.get("movement", ""), body_style),
                ],
                [
                    Paragraph("<b>Lighting Preset</b>", body_style),
                    Paragraph(s.get("lighting", ""), body_style),
                ],
                [
                    Paragraph("<b>Composition Style</b>", body_style),
                    Paragraph(s.get("composition", ""), body_style),
                ],
                [
                    Paragraph("<b>Key Motion Focus</b>", body_style),
                    Paragraph(s.get("motion", ""), body_style),
                ],
                [
                    Paragraph("<b>Resonant Emotion</b>", body_style),
                    Paragraph(s.get("emotion", ""), body_style),
                ],
                [
                    Paragraph("<b>Estimated Credits</b>", body_style),
                    Paragraph(str(s.get("credits", 1)), body_style),
                ],
                [
                    Paragraph("<b>Director Prompt</b>", body_style),
                    Paragraph(s.get("cinematic_prompt", ""), body_style),
                ],
            ]

            t = Table(data, colWidths=[150, 300])
            t.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F7FAFC")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )

            story.append(t)
            story.append(Spacer(1, 15))
            story.append(PageBreak())

        doc.build(story)
