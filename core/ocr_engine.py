# core/ocr_engine.py

from dataclasses import dataclass
from typing import List
import numpy as np
import cv2

from paddleocr import PaddleOCR


@dataclass
class OCRLine:
    text: str
    confidence: float
    bbox: list


class OCREngine:

    def __init__(self):
        print("Initializing PaddleOCR...")

        self.engine_type="PaddleOCR"

        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=True
        )

        print("PaddleOCR initialized successfully.")

    def run_ocr(
        self,
        image,
        min_confidence=0.20
    ) -> List[OCRLine]:

        print("\n========== OCR START ==========")

        # ------------------------------------------------
        # 1. Validate image
        # ------------------------------------------------
        if image is None:
            print("ERROR: Image is None")
            return []

        print("Input type:", type(image))

        # ------------------------------------------------
        # 2. Convert image to numpy
        # ------------------------------------------------
        if hasattr(image, "convert"):
            image = np.array(image.convert("RGB"))

        image = np.asarray(image)

        print("Image shape:", image.shape)
        print("Image dtype:", image.dtype)

        if image.size == 0:
            print("ERROR: Empty image")
            return []

        # ------------------------------------------------
        # 3. Convert grayscale/BGR to RGB
        # ------------------------------------------------
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        elif image.shape[2] == 3:
            # If preprocessing supplied RGB, keep it.
            # PaddleOCR accepts numpy images.
            pass

        # ------------------------------------------------
        # 4. Resize small images
        # ------------------------------------------------
        h, w = image.shape[:2]

        print("Original size:", w, "x", h)

        if w < 1200:
            scale = 1200 / w

            new_w = int(w * scale)
            new_h = int(h * scale)

            image = cv2.resize(
                image,
                (new_w, new_h),
                interpolation=cv2.INTER_CUBIC
            )

            print("Resized to:", new_w, "x", new_h)

        # ------------------------------------------------
        # 5. Run PaddleOCR 3.x
        # ------------------------------------------------
        try:

            print("Running PaddleOCR...")

            results = list(self.ocr.predict(image))

            print("Number of OCR results:", len(results))

        except Exception as e:

            print("PADDLE OCR ERROR:")
            print(repr(e))

            return []

        # ------------------------------------------------
        # 6. Extract result
        # ------------------------------------------------

        lines = []

        for result_index, result in enumerate(results):

            print("\n--- OCR Result", result_index, "---")

            # PaddleOCR 3.x result can expose .json
            data = None

            if hasattr(result, "json"):

                try:
                    json_result = result.json

                    if callable(json_result):
                        json_result = json_result()

                    if isinstance(json_result, dict):
                        data = json_result.get("res", json_result)

                except Exception as e:
                    print("JSON extraction error:", e)

            # Some versions expose .res directly
            if data is None and hasattr(result, "res"):

                data = result.res

            # Some versions behave like dictionaries
            if data is None and isinstance(result, dict):

                data = result.get("res", result)

            if data is None:

                print("Could not extract OCR result structure.")

                print("Result type:", type(result))

                try:
                    print(result)
                except:
                    pass

                continue

            # ------------------------------------------------
            # PaddleOCR 3.x fields
            # ------------------------------------------------

            rec_texts = data.get("rec_texts", [])
            rec_scores = data.get("rec_scores", [])
            rec_boxes = data.get("rec_boxes", [])

            print("Detected text count:", len(rec_texts))

            for i, text in enumerate(rec_texts):

                if text is None:
                    continue

                text = str(text).strip()

                if not text:
                    continue

                # confidence
                try:
                    confidence = float(rec_scores[i])
                except:
                    confidence = 1.0

                # bounding box
                try:

                    bbox = np.asarray(rec_boxes[i]).tolist()

                except:

                    bbox = []

                print(
                    f"OCR: {text} | confidence={confidence:.3f}"
                )

                # IMPORTANT:
                # Do NOT use 0.35 initially.
                # Product packaging contains small text.
                if confidence >= min_confidence:

                    lines.append(
                        OCRLine(
                            text=text,
                            confidence=confidence,
                            bbox=bbox
                        )
                    )

        print("\n========== OCR COMPLETE ==========")
        print("Final OCR lines:", len(lines))

        for line in lines:
            print(
                f"{line.text} "
                f"(confidence={line.confidence:.2f})"
            )

        return lines


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

_ocr_engine = None


def get_ocr_engine():

    global _ocr_engine

    if _ocr_engine is None:
        _ocr_engine = OCREngine()

    return _ocr_engine


def run_ocr(image, min_confidence=0.20):

    engine = get_ocr_engine()

    return engine.run_ocr(
        image,
        min_confidence=min_confidence
    )