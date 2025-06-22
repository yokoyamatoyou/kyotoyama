import tempfile
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
