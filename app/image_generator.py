"""
Image generation module.
Handles color replacement, logo placement, and template processing.
"""

from pathlib import Path

from PIL import Image
import numpy as np

from app.utils import normalize_color, normalize_logo_filename, hex_to_rgb

# Template grayscale colors to replace
TEMPLATE_PRIMARY = "#4A4A4A"
TEMPLATE_SECONDARY = "#BDBDBD"

# Logo placement (relative to image dimensions)
LOGO_X_PCT = 0.005
LOGO_Y_PCT = 0.005
LOGO_W_PCT = 0.08
LOGO_H_PCT = 0.08

# Paths (relative to project root)
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates" / "Football_v1"
LOGO_DIR = BASE_DIR / "logos"
OUTPUT_DIR = BASE_DIR / "outputs"

TEMPLATE_FILES = [
    "01_gps_session_report.png",
    "02_drills.png",
    "03_qb_gps_report.png",
    "04_rb_gps_report.png",
    "05_wr_gps_report.png",
    "06_te_gps_report.png",
    "07_ol_gps_report.png",
    "08_dl_gps_report.png",
    "09_lb_gps_report.png",
]


def replace_colors(image, old_hex: str, new_hex: str, tolerance: int = 0):
    """Replace exact-match pixels of old_hex color with new_hex in an RGBA image."""
    old_rgb = hex_to_rgb(old_hex)
    new_rgb = hex_to_rgb(new_hex)

    data = np.array(image)

    r_match = np.abs(data[:, :, 0].astype(int) - old_rgb[0]) <= tolerance
    g_match = np.abs(data[:, :, 1].astype(int) - old_rgb[1]) <= tolerance
    b_match = np.abs(data[:, :, 2].astype(int) - old_rgb[2]) <= tolerance
    mask = r_match & g_match & b_match

    data[mask, 0] = new_rgb[0]
    data[mask, 1] = new_rgb[1]
    data[mask, 2] = new_rgb[2]

    return Image.fromarray(data)


def place_logo(base_image, logo_image):
    """Place logo in the top-left corner, sized relative to the base image."""
    base_w, base_h = base_image.size

    box_w = int(base_w * LOGO_W_PCT)
    box_h = int(base_h * LOGO_H_PCT)

    logo_w, logo_h = logo_image.size
    scale = min(box_w / logo_w, box_h / logo_h)
    new_w = int(logo_w * scale)
    new_h = int(logo_h * scale)

    resized_logo = logo_image.resize((new_w, new_h), Image.LANCZOS)

    x = int(base_w * LOGO_X_PCT)
    y = int(base_h * LOGO_Y_PCT)

    base_image.paste(resized_logo, (x, y), resized_logo)
    return base_image


def generate_output_folder(team_name: str) -> Path:
    """Create and return the output folder path."""
    folder = OUTPUT_DIR / f"{team_name}_pitch_deck"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def process_template(template_path: Path, logo_image, primary_hex: str, secondary_hex: str):
    """Load a template, replace colors, place logo, return final image."""
    image = Image.open(template_path).convert("RGBA")

    image = replace_colors(image, TEMPLATE_PRIMARY, primary_hex)
    image = replace_colors(image, TEMPLATE_SECONDARY, secondary_hex)

    image = place_logo(image, logo_image.copy())
    return image


def generate_reports(
    team_name: str,
    logo_filename: str,
    primary_color: str,
    secondary_color: str,
) -> dict:
    """Generate all 9 branded report PNGs. Returns result dict."""
    primary_color = normalize_color(primary_color)
    secondary_color = normalize_color(secondary_color)
    logo_filename = normalize_logo_filename(logo_filename)

    # Load logo
    logo_path = LOGO_DIR / logo_filename
    if not logo_path.exists():
        return {"success": False, "error": f"Logo not found: {logo_path}"}

    logo = Image.open(logo_path).convert("RGBA")

    # Create output folder
    output_folder = generate_output_folder(team_name)

    # Process templates
    generated_files = []
    for filename in TEMPLATE_FILES:
        template_path = TEMPLATE_DIR / filename

        if not template_path.exists():
            return {"success": False, "error": f"Template not found: {template_path}"}

        result = process_template(template_path, logo, primary_color, secondary_color)
        result.save(output_folder / filename, "PNG")
        generated_files.append(filename)

    return {
        "success": True,
        "output_folder": str(output_folder.relative_to(BASE_DIR)),
        "generated_files": generated_files,
    }
