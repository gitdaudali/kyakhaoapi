"""
Template rendering utilities for email templates.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


@dataclass
class EmailData:
    """Data class for email content and metadata."""

    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """
    Render email template using Jinja2.

    Args:
        template_name: Name of the template file
        context: Context variables for template rendering

    Returns:
        Rendered HTML content
    """
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    template = env.get_template(template_name)
    html_content = template.render(context)
    return html_content
