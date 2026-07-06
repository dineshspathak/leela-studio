import json
import re
from pathlib import Path

from episodes.schemas import Episode


def substitute_variables(json_str: str, variables: dict[str, str]) -> str:
    """Substitute ${var} and $var strings inside the JSON string."""

    def replacer(match):
        var_name = match.group(1) or match.group(2)
        # Strip to handle whitespace if any e.g. ${ krishna }
        clean_name = var_name.strip()
        return variables.get(clean_name, match.group(0))

    return re.sub(r"\$\{(\w+)\}|\$(\w+)", replacer, json_str)


def parse_episode(file_path: Path) -> Episode:
    """Parse, replace variables, and load an Episode object from JSON."""
    with open(file_path, encoding="utf-8") as f:
        raw_content = f.read()

    # Extract variables first
    temp_data = json.loads(raw_content)
    variables = temp_data.get("variables", {})

    # Substitute variables
    clean_content = substitute_variables(raw_content, variables)

    # Parse Pydantic schema
    final_data = json.loads(clean_content)
    return Episode(**final_data)
