
import streamlit as st
import sys
import os
import tempfile
import json
import io
import zipfile
import time
import requests

# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

TEXT_MODULE = os.path.join(BASE_DIR, "text_module")
IMAGE_MODULE = os.path.join(BASE_DIR, "image_module")
FUSION_MODULE = os.path.join(BASE_DIR, "fusion_module")
GENERATION_MODULE = os.path.join(BASE_DIR, "generation_module")

for folder in [
    TEXT_MODULE,
    IMAGE_MODULE,
    FUSION_MODULE,
    GENERATION_MODULE,
]:
    sys.path.insert(0, folder)

# =========================================================
# IMPORT PROJECT MODULES
# =========================================================

from scene_understanding import understand_scene
from image_processor import process_image
from new_data_fusion import perform_new_data_fusion
from fused_prompt_builder import create_fused_prompt

# =========================================================
# FLUX ASYNC API
# =========================================================
FLUX_HOST = "https://reply-seven-remind-stuff.trycloudflare.com"

FLUX_START_URL = FLUX_HOST + "/start"

# =========================================================
# STREAMLIT CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Crime Scene Reconstruction",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(124, 58, 237, 0.18),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(14, 165, 233, 0.16),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f8f7ff 0%,
                #eef4ff 50%,
                #f0fdfa 100%
            );
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -1.5px;
        margin-bottom: 0.2rem;
        background: linear-gradient(
            90deg,
            #312e81,
            #4f46e5,
            #7c3aed,
            #0891b2
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-size: 1.08rem;
        color: #64748b;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    h1 {
        color: #1e1b4b !important;
        font-weight: 800 !important;
    }

    h2 {
        color: #312e81 !important;
        font-weight: 800 !important;
    }

    h3 {
        color: #4338ca !important;
        font-weight: 750 !important;
    }

    textarea {
        border-radius: 16px !important;
        border: 2px solid #c7d2fe !important;
        background: #ffffff !important;
        color: #1e293b !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.08) !important;
    }

    [data-testid="stFileUploader"] {
        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.95),
            rgba(238,242,255,0.95)
        );
        border: 2px dashed #818cf8;
        border-radius: 18px;
        padding: 0.8rem;
        box-shadow: 0 8px 25px rgba(79,70,229,0.08);
    }

    .stButton > button {
        width: 100%;
        min-height: 3.4rem;
        border: none !important;
        border-radius: 16px !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        color: white !important;
        background: linear-gradient(
            90deg,
            #4338ca,
            #6366f1,
            #7c3aed,
            #0891b2
        ) !important;
        box-shadow: 0 10px 25px rgba(79,70,229,0.28) !important;
    }

    .stDownloadButton > button {
        width: 100%;
        border-radius: 14px !important;
        font-weight: 700 !important;
        color: #4338ca !important;
        background: #eef2ff !important;
        border: 2px solid #c7d2fe !important;
    }

    [data-testid="stImage"] img {
        border-radius: 18px;
        border: 3px solid rgba(99,102,241,0.18);
        box-shadow: 0 12px 35px rgba(15,23,42,0.16);
    }

    .tag {
        display: inline-block;
        padding: 7px 13px;
        margin: 4px;
        border-radius: 999px;
        background: linear-gradient(135deg, #ede9fe, #dbeafe);
        color: #4338ca;
        border: 1px solid #c4b5fd;
        font-size: 0.84rem;
        font-weight: 700;
    }

    .info-label {
        font-weight: 800;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        color: #6366f1;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }

    .info-value {
        font-size: 0.98rem;
        color: #1e293b;
        margin-bottom: 0.8rem;
        line-height: 1.55;
    }

    [data-testid="stExpander"] {
        border-radius: 16px !important;
        border: 1px solid #c7d2fe !important;
        background: rgba(255,255,255,0.9) !important;
        box-shadow: 0 6px 20px rgba(79,70,229,0.07);
    }

    .disclaimer {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #fdba74;
        background: linear-gradient(135deg, #fff7ed, #fffbeb);
        color: #9a3412;
        font-size: 0.9rem;
        line-height: 1.6;
        box-shadow: 0 6px 18px rgba(234,88,12,0.08);
    }

    .pipeline-box {
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        font-size: 0.95rem;
        line-height: 2;
        color: white;
        background: linear-gradient(
            135deg,
            #1e1b4b,
            #312e81,
            #4f46e5,
            #0891b2
        );
        border: 1px solid rgba(255,255,255,0.25);
        box-shadow: 0 15px 35px rgba(49,46,129,0.25);
    }

    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(
            90deg,
            transparent,
            #c7d2fe,
            #818cf8,
            #c7d2fe,
            transparent
        ) !important;
        margin: 2rem 0 !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_items(items):
    if not items:
        return "None"

    if isinstance(items, list):
        return ", ".join(str(item) for item in items)

    return str(items)


def display_information(title, items):
    st.markdown(
        f'<div class="info-label">{title}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="info-value">{format_items(items)}</div>',
        unsafe_allow_html=True,
    )


def display_tags(items):
    if not items:
        st.write("None")
        return

    tags = "".join(
        f'<span class="tag">{item}</span>'
        for item in items
    )

    st.markdown(tags, unsafe_allow_html=True)


def display_relationships(relationships):
    if not relationships:
        st.write("None")
        return

    for relationship in relationships:
        action = relationship.get("action", "")
        subject = relationship.get("subject")
        object_name = relationship.get("object")

        if subject and object_name:
            st.write(f"• {subject} → {action} → {object_name}")
        elif subject:
            st.write(f"• {subject} → {action}")
        elif object_name:
            st.write(f"• {action} → {object_name}")
        else:
            st.write(f"• {action}")


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🔍 Crime Scene Reconstruction</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Generate a plausible reconstruction of a crime scene '
    'using text and image information.'
    '</div>',
    unsafe_allow_html=True,
)

# =========================================================
# CRIME SCENE INPUT
# =========================================================

st.header("Crime Scene Input")

crime_description = st.text_area(
    "Enter Crime Scene Description",
    placeholder=(
        "Example: A car collided with a motorcycle on a city road "
        "at night. The motorcycle was damaged and broken glass "
        "was scattered near the vehicles."
    ),
    height=150,
)

uploaded_image = st.file_uploader(
    "Upload Crime Scene Image",
    type=["jpg", "jpeg", "png"],
)

if uploaded_image is not None:
    st.subheader("Uploaded Crime Scene Image")

    image_col1, image_col2, image_col3 = st.columns([1, 2, 1])

    with image_col2:
        st.image(
            uploaded_image,
            caption="Uploaded Crime Scene Image",
            use_container_width=True,
        )

# =========================================================
# RECONSTRUCT BUTTON
# =========================================================

st.write("")

reconstruct_clicked = st.button(
    "🔍 RECONSTRUCT SCENE",
    type="primary",
    use_container_width=True,
)

# =========================================================
# RECONSTRUCTION PIPELINE — PART 2
# =========================================================

if reconstruct_clicked:

    # -----------------------------------------------------
    # 1. INPUT VALIDATION
    # -----------------------------------------------------

    if not crime_description.strip():
        st.error("Please enter a crime scene description.")
        st.stop()

    if uploaded_image is None:
        st.error("Please upload a crime scene image.")
        st.stop()

    st.success("Crime scene processing started.")

    image_path = None

    try:
        # -------------------------------------------------
        # 1. TEXT SCENE UNDERSTANDING
        # -------------------------------------------------

        st.header("1. Text Scene Understanding")

        with st.spinner("Analyzing crime scene description..."):
            scene = understand_scene(crime_description)

        text_output_file = os.path.join(
            TEXT_MODULE,
            "scene_understanding_output.json",
        )

        with open(text_output_file, "w", encoding="utf-8") as file:
            json.dump(scene, file, indent=4, ensure_ascii=False)

        text_col1, text_col2 = st.columns(2)

        with text_col1:
            display_information("Event", scene.get("event", []))
            display_information("Time", scene.get("time", []))
            display_information("People", scene.get("people", []))
            display_information("Locations", scene.get("locations", []))
            display_information("Objects", scene.get("objects", []))

        with text_col2:
            display_information("Actions", scene.get("actions", []))
            display_information("Conditions", scene.get("conditions", []))
            display_information("Evidence", scene.get("evidence", []))

            st.markdown(
                '<div class="info-label">Relationships</div>',
                unsafe_allow_html=True,
            )
            display_relationships(scene.get("relationships", []))

        # -------------------------------------------------
        # 2. IMAGE PROCESSING
        # -------------------------------------------------

        st.header("2. Image Processing")

        suffix = os.path.splitext(uploaded_image.name)[1] or ".jpg"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(uploaded_image.getbuffer())
            image_path = temp_file.name

        with st.spinner("Detecting objects in the uploaded image..."):
            detected_objects = process_image(image_path)

        st.markdown("**Detected Objects**")
        display_tags(detected_objects)

        # -------------------------------------------------
        # 3. DATA FUSION
        # -------------------------------------------------

        st.header("3. Text + Image Data Fusion")

        with st.spinner("Combining text and image information..."):
            perform_new_data_fusion()

        fused_scene_file = os.path.join(
            FUSION_MODULE,
            "fused_scene.json",
        )

        if not os.path.exists(fused_scene_file):
            st.error(
                "Fused scene file was not created. "
                "Check the data-fusion module."
            )
            st.stop()

        with open(fused_scene_file, "r", encoding="utf-8") as file:
            fused_scene = json.load(file)

        fusion_col1, fusion_col2 = st.columns(2)

        with fusion_col1:
            st.markdown("**Common Objects**")
            display_tags(fused_scene.get("common_objects", []))

            st.markdown("**Text-Only Objects**")
            display_tags(fused_scene.get("text_only_objects", []))

        with fusion_col2:
            st.markdown("**Image-Only Objects**")
            display_tags(fused_scene.get("image_only_objects", []))

            st.markdown("**Visual Context**")

            visual_context_objects = []

            for item in fused_scene.get("visual_context", []):
                if isinstance(item, dict):
                    object_name = item.get("object")
                    if object_name:
                        visual_context_objects.append(object_name)
                else:
                    visual_context_objects.append(str(item))

            display_tags(visual_context_objects)

        with st.expander("View Fused Scene Context"):
            st.json(fused_scene.get("scene_context", {}))

        st.success("Text and image information successfully fused.")

        # -------------------------------------------------
        # 4. FLUX PROMPT GENERATION
        # -------------------------------------------------

        st.header("4. FLUX Prompt Generation")

        with st.spinner("Building the final FLUX prompt..."):
            final_prompt = create_fused_prompt(fused_scene)

        prompt_file = os.path.join(
            GENERATION_MODULE,
            "final_fused_prompt.txt",
        )

        with open(prompt_file, "w", encoding="utf-8") as file:
            file.write(final_prompt)

        with st.expander("View Generated FLUX Prompt"):
            st.code(final_prompt, language="text")

        st.success("Final FLUX prompt created successfully.")

        # Part 3 will add asynchronous FLUX generation here.
        
        
        # -------------------------------------------------
        # 5. CRIME SCENE RECONSTRUCTION USING FLUX
        # -------------------------------------------------

        st.header("5. Crime Scene Reconstruction")
        st.info("Generating reconstruction views using FLUX.1-dev.")

        with st.spinner("Submitting the scene to FLUX..."):
            with open(image_path, "rb") as image_file:
                start_response = requests.post(
                    FLUX_START_URL,
                    data={"prompt": final_prompt},
                    files={
                        "image": (
                            uploaded_image.name,
                            image_file,
                            uploaded_image.type or "application/octet-stream",
                        )
                    },
                    timeout=120,
                )

            start_response.raise_for_status()
            start_data = start_response.json()
            job_id = start_data.get("job_id")

            if not job_id:
                raise RuntimeError(
                    f"FLUX server did not return a job ID: {start_data}"
                )

            status_box = st.empty()
            progress_bar = st.progress(0)
            completed = False
            elapsed = 0
            max_wait_seconds = 900
            poll_interval = 5

            while elapsed < max_wait_seconds:
                status_response = requests.get(
                    f"{FLUX_HOST}/status/{job_id}",
                    timeout=30,
                )
                status_response.raise_for_status()
                status_data = status_response.json()

                job_status = str(
                    status_data.get("status", "")
                ).lower()

                status_box.info(
                    status_data.get(
                        "message",
                        f"Generating images... {elapsed} seconds elapsed",
                    )
                )

                if status_data.get("error") or job_status in (
                    "failed", "error"
                ):
                    raise RuntimeError(
                        f"FLUX generation failed: {status_data}"
                    )

                if (
                    status_data.get("completed") is True
                    or job_status in (
                        "completed", "complete", "success", "succeeded"
                    )
                ):
                    completed = True
                    progress_bar.progress(100)
                    break

                progress_bar.progress(
                    min(95, int(elapsed / max_wait_seconds * 100))
                )
                time.sleep(poll_interval)
                elapsed += poll_interval

            if not completed:
                raise TimeoutError(
                    "FLUX generation exceeded 15 minutes."
                )

            result_response = requests.get(
                f"{FLUX_HOST}/result/{job_id}",
                timeout=120,
            )
            result_response.raise_for_status()
            zip_bytes = result_response.content

            if not zipfile.is_zipfile(io.BytesIO(zip_bytes)):
                raise RuntimeError(
                    "The FLUX result is not a valid ZIP archive."
                )

        st.success("Reconstruction generation completed!")
        st.subheader("Generated Reconstruction Views")

        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            image_names = sorted(
                name
                for name in archive.namelist()
                if name.lower().endswith((".png", ".jpg", ".jpeg"))
                and not name.startswith("__")
            )

            if not image_names:
                st.warning("No image files were found in the ZIP.")
            else:
                for start_index in range(0, len(image_names), 2):
                    row_names = image_names[start_index:start_index + 2]
                    columns = st.columns(len(row_names))

                    for column, image_name in zip(columns, row_names):
                        with column:
                            st.image(
                                archive.read(image_name),
                                caption=os.path.basename(image_name),
                                use_container_width=True,
                            )

                st.download_button(
                    "Download Reconstruction Views (ZIP)",
                    data=zip_bytes,
                    file_name="reconstruction_views.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

        st.markdown(
            """
            <div class="disclaimer">
            <b>Important:</b> These are AI-generated, plausible
            interpretations of the provided inputs. They are not verified
            evidence or proof of what actually happened.
            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error("An error occurred during reconstruction.")
        st.exception(e)

    finally:
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass


# =========================================================
# SYSTEM PIPELINE FOOTER
# =========================================================

st.divider()
st.subheader("System Pipeline")

st.markdown(
    """
    <div class="pipeline-box">
    <b>Text Input</b> → <b>Scene Understanding</b> →
    <b>YOLO Image Processing</b> → <b>Data Fusion</b> →
    <b>FLUX Prompt Generation</b> → <b>FLUX.1-dev</b> →
    <b>Reconstruction Views</b>
    </div>
    """,
    unsafe_allow_html=True,
)
