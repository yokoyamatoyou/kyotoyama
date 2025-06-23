from PIL import Image
import openai
import io
import base64
from modules.image_analyzer import mask_patient_info


def _image_to_data_url(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def extract_burned_in_text(image, api_key: str) -> str | None:
    """Extract burned-in text from an image using GPT-4.1mini OCR."""
    client = openai.OpenAI(api_key=api_key)

    masked = mask_patient_info(image)
    pil = Image.fromarray(masked.numpy().astype("uint8"))
    img_url = _image_to_data_url(pil)

    prompt = (
        "You are an OCR assistant. "
        "Return all visible text from the provided medical image as plain text."
    )

    response = client.chat.completions.create(
        model="gpt-4.1mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": img_url}}]},
        ],
    )

    try:
        return response.choices[0].message.content
    except Exception:
        return None
