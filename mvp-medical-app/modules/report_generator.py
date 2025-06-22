from pydantic import BaseModel, Field
from typing import Optional
from PIL import Image
import openai
import io
import base64


class LesionFinding(BaseModel):
    is_finding_present: bool = Field(description="Whether a lesion is present")
    finding_summary: Optional[str] = Field(description="Short summary")
    detailed_description: Optional[str] = Field(description="Detailed description")
    confidence_score: Optional[float] = Field(description="Confidence 0-1")
    anatomical_location: Optional[str] = Field(description="Approximate location")


def _image_to_data_url(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def generate_structured_report(original_image, probability_mask, api_key):
    """Generate a structured report using GPT-4.1mini."""
    client = openai.OpenAI(api_key=api_key)

    original_pil = Image.fromarray(original_image.numpy().astype("uint8"))
    mask_pil = Image.fromarray((probability_mask.numpy() * 255).astype("uint8"))

    orig_url = _image_to_data_url(original_pil)
    mask_url = _image_to_data_url(mask_pil)

    prompt = (
        "You are a medical imaging assistant. "
        "Analyze the provided MRI and probability mask and return JSON report."
    )

    response = client.chat.completions.create(
        model="gpt-4.1mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": orig_url}}]},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": mask_url}}]},
        ],
        response_format={"type": "json_object"},
    )

    try:
        content = response.choices[0].message.content
        return LesionFinding.model_validate_json(content)
    except Exception:
        return None
