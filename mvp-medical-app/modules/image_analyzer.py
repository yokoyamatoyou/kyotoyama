import tempfile
import io
import numpy as np
from PIL import Image
import ants
from antspynet.utilities import brain_extraction


def analyze_image(image_bytes):
    """Analyze an uploaded image and return segmentation results."""
    with tempfile.NamedTemporaryFile(suffix=".nii") as tmp:
        tmp.write(image_bytes)
        tmp.flush()
        image = ants.image_read(tmp.name, pixeltype="float")

    probability_mask = brain_extraction(image, modality="t1")
    mask = ants.threshold_image(probability_mask, 0.5, 1)
    return {
        "original_image": image,
        "segmentation_mask": mask,
        "probability_mask": probability_mask,
    }


def create_overlay_image(original_image, segmentation_mask, color=(255, 0, 0), alpha=0.3):
    """Return a PIL Image with the mask overlaid on the original."""
    orig = original_image.numpy().astype("uint8")
    if orig.ndim == 2:
        orig = np.stack([orig] * 3, axis=-1)
    overlay = orig.copy()
    mask = segmentation_mask.numpy() > 0
    overlay[mask] = ((1 - alpha) * overlay[mask] + alpha * np.array(color)).astype("uint8")
    return Image.fromarray(overlay)


def save_overlay_png(original_image, segmentation_mask, output_path, color=(255, 0, 0), alpha=0.3):
    """Save an overlay PNG image combining original and mask."""
    overlay = create_overlay_image(original_image, segmentation_mask, color, alpha)
    overlay.save(output_path, format="PNG")


def overlay_png_bytes(original_image, segmentation_mask, color=(255, 0, 0), alpha=0.3) -> bytes:
    """Return overlay image bytes in PNG format."""
    overlay = create_overlay_image(original_image, segmentation_mask, color, alpha)
    buf = io.BytesIO()
    overlay.save(buf, format="PNG")
    return buf.getvalue()



def mask_patient_info(image, height_ratio=0.05):
    """Return a copy of the image with the top portion masked.

    This performs a simple black-out of the specified fraction of
    the image height to obscure burned-in patient identifiers.
    """
    arr = image.numpy().copy()
    mask_height = max(1, int(arr.shape[0] * height_ratio))
    if arr.ndim == 3:
        arr[:mask_height, :, :] = 0
    else:
        arr[:mask_height, :] = 0
    return ants.from_numpy(arr, origin=image.origin, spacing=image.spacing, direction=image.direction)
