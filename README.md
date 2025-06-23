# Kyotoyama Medical Image Analyzer

This repository contains an MVP for a Streamlit-based medical image analysis application.
The project follows the plan outlined in `Kyotoyama_Medical_Image_Analyzer最新版MVP設計・進捗管理.md`.

The application allows users to upload medical images, perform segmentation with ANTsPyNet,
generate a structured report using the GPT-4.1mini API, and store simple image comments.

## Disclaimer

This project provides an experimental AI assistant for drafting radiology reports.
Generated results may contain inaccuracies and must not be used for final medical
diagnosis. Always verify and edit the output with a qualified professional.

The app can also extract burned-in text from uploaded images using GPT-4.1mini OCR.
Overlay images combining segmentation results with the original can be downloaded as PNG files.

## Development

Create a Python 3.11 virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r mvp-medical-app/requirements.txt
```

Run the Streamlit app:

```bash
streamlit run mvp-medical-app/app.py
```

Set `COMMENT_DB_PATH` to control where comments are stored (defaults to `comments.db`).

Run tests:

```bash
pytest
```
