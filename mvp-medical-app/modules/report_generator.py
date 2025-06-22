from pydantic import BaseModel, Field
from typing import Optional
from PIL import Image
import google.generativeai as genai
import io


class LesionFinding(BaseModel):
    is_finding_present: bool = Field(description="Whether a lesion is present")
    finding_summary: Optional[str] = Field(description="Short summary")
    detailed_description: Optional[str] = Field(description="Detailed description")
    confidence_score: Optional[float] = Field(description="Confidence 0-1")
    anatomical_location: Optional[str] = Field(description="Approximate location")


def generate_structured_report(original_image, probability_mask, api_key):
    """Generate a structured report using Gemini."""
    genai.configure(api_key=api_key)

    original_pil = Image.fromarray(original_image.numpy().astype("uint8"))
    mask_pil = Image.fromarray((probability_mask.numpy() * 255).astype("uint8"))

    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=LesionFinding,
    )
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
    )

    prompt = (
        "You are a medical imaging assistant. "
        "Analyze the provided MRI and probability mask and return JSON report."
    )

    response = model.generate_content([prompt, original_pil, mask_pil])
    try:
        return LesionFinding.model_validate_json(response.text)
    except Exception:
        return None
