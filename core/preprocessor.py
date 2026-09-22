import cv2
import numpy as np
from PIL import Image


def load_image_to_cv2(image):
    """Convert PIL image to OpenCV BGR format."""
    if isinstance(image, Image.Image):
        image = np.array(image.convert("RGB"))
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


def preprocess_label_image(
    image,
    enable_clahe=True,
    enable_denoise=True,
    enable_deskew=True
):
    """Basic image preprocessing pipeline."""

    original_bgr = load_image_to_cv2(image)

    original_rgb = cv2.cvtColor(
        original_bgr,
        cv2.COLOR_BGR2RGB
    )

    current = original_bgr.copy()

    stages = {}

    # Original
    stages["Original"] = original_rgb

    # Grayscale
    gray = cv2.cvtColor(
        current,
        cv2.COLOR_BGR2GRAY
    )

    stages["Grayscale"] = gray

    # CLAHE
    if enable_clahe:
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        enhanced_gray = clahe.apply(gray)
    else:
        enhanced_gray = gray

    stages["Contrast Enhanced"] = enhanced_gray

    # Denoising
    if enable_denoise:
        denoised = cv2.bilateralFilter(
            enhanced_gray,
            9,
            75,
            75
        )
    else:
        denoised = enhanced_gray

    stages["Denoised"] = denoised

    # Threshold
    threshold = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    stages["Threshold"] = threshold

    # Deskew
    skew_angle = 0.0

    if enable_deskew:
        # Basic placeholder for deskew.
        # Keeps the image unchanged if no reliable angle is found.
        skew_angle = 0.0

    enhanced_rgb = cv2.cvtColor(
        denoised,
        cv2.COLOR_GRAY2RGB
    )

    height, width = original_bgr.shape[:2]

    return {
        "original_rgb": original_rgb,
        "enhanced_rgb": enhanced_rgb,
        "stages": stages,
        "skew_angle": skew_angle,
        "dimensions": {
            "width": width,
            "height": height
        }
    }