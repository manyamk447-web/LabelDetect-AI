import cv2
import numpy as np
from PIL import Image


def numpy_to_pil(image):
    if image is None:
        return None

    image = np.asarray(image).astype(np.uint8)

    if len(image.shape) == 2:
        return Image.fromarray(image)

    return Image.fromarray(image)


def draw_ocr_boxes(image_rgb, ocr_lines):
    annotated = np.asarray(image_rgb).copy()

    if len(annotated.shape) == 2:
        annotated = cv2.cvtColor(
            annotated,
            cv2.COLOR_GRAY2RGB
        )

    for line in ocr_lines:

        try:
            points = np.array(
                line.bbox,
                dtype=np.int32
            ).reshape((-1, 1, 2))

            cv2.polylines(
                annotated,
                [points],
                True,
                (0, 255, 0),
                2
            )

            x = int(line.bbox[0][0])
            y = int(line.bbox[0][1])

            label = (
                f"{line.text} "
                f"({line.confidence:.2f})"
            )

            cv2.putText(
                annotated,
                label,
                (x, max(20, y - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                1,
                cv2.LINE_AA
            )

        except Exception:
            continue

    return annotated