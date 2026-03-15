"""
Utility helpers for input normalization and color conversion.
"""


def normalize_color(color: str) -> str:
    """Ensure color has a # prefix."""
    color = color.strip()
    if not color.startswith("#"):
        color = f"#{color}"
    return color


def normalize_logo_filename(filename: str) -> str:
    """Ensure logo filename ends with .png."""
    filename = filename.strip()
    if not filename.lower().endswith(".png"):
        filename = f"{filename}.png"
    return filename


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
