"""
Streamlit app for Whistle Report Generator.
Upload a logo, pick brand colors, and generate branded report templates.
"""

import io
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates" / "Football_v1"

# Template grayscale colors to replace
TEMPLATE_PRIMARY = "#4A4A4A"
TEMPLATE_SECONDARY = "#BDBDBD"

# Logo placement (relative to image dimensions)
LOGO_X_PCT = 0.005
LOGO_Y_PCT = 0.005
LOGO_W_PCT = 0.08
LOGO_H_PCT = 0.08

# Maximum templates allowed
MAX_TEMPLATES = 10


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def replace_colors(image: Image.Image, old_hex: str, new_hex: str, tolerance: int = 0) -> Image.Image:
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


def place_logo(base_image: Image.Image, logo_image: Image.Image) -> Image.Image:
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


def process_template(
    template_image: Image.Image,
    logo_image: Image.Image,
    primary_hex: str,
    secondary_hex: str
) -> Image.Image:
    """Apply color replacement and logo placement to a template."""
    image = template_image.convert("RGBA")
    image = replace_colors(image, TEMPLATE_PRIMARY, primary_hex)
    image = replace_colors(image, TEMPLATE_SECONDARY, secondary_hex)
    image = place_logo(image, logo_image.copy())
    return image


def get_available_templates() -> list[Path]:
    """Get list of template files from the templates directory."""
    if not TEMPLATE_DIR.exists():
        return []
    templates = sorted(TEMPLATE_DIR.glob("*.png"))
    return templates[:MAX_TEMPLATES]


def create_zip_download(images: dict[str, Image.Image]) -> bytes:
    """Create a ZIP file containing all generated images."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, image in images.items():
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            zip_file.writestr(filename, img_buffer.read())
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit App
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Whistle Report Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Whistle Report Generator")
st.markdown("Generate branded report templates with your logo and colors.")

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar - Configuration
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Brand Settings")

    # Logo upload
    st.subheader("1. Upload Logo")
    uploaded_logo = st.file_uploader(
        "Upload your logo (PNG with transparency recommended)",
        type=["png", "jpg", "jpeg"],
        help="For best results, use a PNG with transparent background"
    )

    if uploaded_logo:
        logo_image = Image.open(uploaded_logo).convert("RGBA")
        st.image(logo_image, caption="Your Logo", width=150)
    else:
        logo_image = None

    st.divider()

    # Color pickers
    st.subheader("2. Brand Colors")

    col1, col2 = st.columns(2)
    with col1:
        primary_color = st.color_picker(
            "Primary Color",
            value="#990000",
            help="Main brand color for headers and accents"
        )
    with col2:
        secondary_color = st.color_picker(
            "Secondary Color",
            value="#A9A9A9",
            help="Secondary color for backgrounds and details"
        )

    # Show color preview
    st.markdown(
        f"""
        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <div style="background-color: {primary_color}; width: 50%; height: 40px; border-radius: 5px;"></div>
            <div style="background-color: {secondary_color}; width: 50%; height: 40px; border-radius: 5px;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Template selection
    st.subheader("3. Select Templates")
    available_templates = get_available_templates()

    if available_templates:
        template_options = {t.stem: t for t in available_templates}
        selected_template_names = st.multiselect(
            f"Choose templates (max {MAX_TEMPLATES})",
            options=list(template_options.keys()),
            default=list(template_options.keys()),
            help="Select which templates to generate"
        )
        selected_templates = [template_options[name] for name in selected_template_names]
    else:
        st.warning("No templates found in templates/Football_v1/")
        selected_templates = []

# ─────────────────────────────────────────────────────────────────────────────
# Main Area - Preview & Generate
# ─────────────────────────────────────────────────────────────────────────────

# Validation
can_generate = logo_image is not None and len(selected_templates) > 0

if not uploaded_logo:
    st.info("👈 Upload a logo in the sidebar to get started.")

if uploaded_logo and not selected_templates:
    st.warning("Please select at least one template to generate.")

# Generate button
if can_generate:
    st.subheader("Preview & Generate")

    # Show preview of first template
    with st.expander("Preview (First Template)", expanded=True):
        preview_template = Image.open(selected_templates[0])
        preview_result = process_template(
            preview_template,
            logo_image,
            primary_color,
            secondary_color
        )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Template**")
            st.image(preview_template, use_container_width=True)
        with col2:
            st.markdown("**With Your Branding**")
            st.image(preview_result, use_container_width=True)

    st.divider()

    # Generate all reports
    if st.button("🚀 Generate All Reports", type="primary", use_container_width=True):
        generated_images = {}

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, template_path in enumerate(selected_templates):
            status_text.text(f"Processing: {template_path.name}")

            template_image = Image.open(template_path)
            result_image = process_template(
                template_image,
                logo_image,
                primary_color,
                secondary_color
            )
            generated_images[template_path.name] = result_image

            progress_bar.progress((i + 1) / len(selected_templates))

        status_text.text("Done!")

        # Store in session state
        st.session_state.generated_images = generated_images
        st.success(f"Generated {len(generated_images)} branded reports!")

# Download section
if "generated_images" in st.session_state and st.session_state.generated_images:
    st.divider()
    st.subheader("Download Reports")

    # Create ZIP download
    zip_data = create_zip_download(st.session_state.generated_images)

    st.download_button(
        label="📥 Download All Reports (ZIP)",
        data=zip_data,
        file_name="branded_reports.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True
    )

    # Show all generated images in a grid
    with st.expander("View All Generated Reports", expanded=False):
        cols = st.columns(3)
        for i, (filename, image) in enumerate(st.session_state.generated_images.items()):
            with cols[i % 3]:
                st.image(image, caption=filename, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.9em;">
        Whistle Report Generator • Upload logo, pick colors, generate branded templates
    </div>
    """,
    unsafe_allow_html=True
)
