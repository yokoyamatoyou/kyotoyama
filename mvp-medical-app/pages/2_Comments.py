import os
import streamlit as st
from modules.comments import add_comment, list_comments

DB_PATH = os.environ.get("COMMENT_DB_PATH", "comments.db")

st.set_page_config(page_title="Comments")

st.title("Image Comments")

image_name = st.text_input("Image identifier")
comment_text = st.text_area("Comment")

if st.button("Save Comment"):
    if not image_name or not comment_text:
        st.error("Provide image identifier and comment text")
    else:
        add_comment(DB_PATH, image_name, comment_text)
        st.success("Comment saved")

st.subheader("Stored Comments")
comments = list_comments(DB_PATH, image_name if image_name else None)
for c in comments:
    st.markdown(f"**{c['image_name']}**: {c['text']}")
