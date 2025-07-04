import streamlit as st
from modules.image_analyzer import analyze_image, overlay_png_bytes
from modules.report_generator import generate_structured_report
from modules.ocr import extract_burned_in_text
from modules.comments import add_comment
import os

DB_PATH = os.environ.get("COMMENT_DB_PATH", "comments.db")


@st.cache_resource
def cached_analyze(data: bytes):
    return analyze_image(data)


@st.cache_resource
def cached_report(orig, prob, key):
    return generate_structured_report(orig, prob, key)


@st.cache_resource
def cached_ocr(image, key):
    return extract_burned_in_text(image, key)

st.set_page_config(page_title="Image Analysis")

st.title("Upload Medical Image")
st.info(
    "This tool is an experimental AI assistant for drafting radiology reports. "
    "Results may contain inaccuracies and should not be used for final diagnosis."
)

uploaded_file = st.file_uploader("Upload image", type=["nii", "nii.gz", "png", "jpg"])

if uploaded_file:
    with st.spinner("Analyzing image..."):
        results = cached_analyze(uploaded_file.getvalue())

    st.success("Analysis complete")

    col1, col2 = st.columns(2)
    col1.image(results["original_image"].numpy(), caption="Original")
    col2.image(results["segmentation_mask"].numpy(), caption="Mask")

    overlay_bytes = overlay_png_bytes(
        results["original_image"],
        results["segmentation_mask"],
    )
    st.download_button(
        "Download Overlay PNG",
        overlay_bytes,
        file_name=f"{uploaded_file.name}_overlay.png",
        mime="image/png",
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        with st.spinner("Generating report..."):
            report = cached_report(
                results["original_image"],
                results["probability_mask"],
                api_key,
            )
        if report:
            st.json(report.model_dump())

        with st.spinner("Extracting burned-in text..."):
            text = cached_ocr(results["original_image"], api_key)
        if text:
            st.subheader("Burned-in Text")
            st.text(text)
    else:
        st.warning("GEMINI_API_KEY not set")

    st.subheader("Add Comment")
    comment = st.text_area("Comment")
    if st.button("Save Comment"):
        add_comment(DB_PATH, uploaded_file.name, comment)
        st.success("Comment saved")
