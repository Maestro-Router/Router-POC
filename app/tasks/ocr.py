from app.tasks.base import Task
import easyocr
import numpy as np
from PIL import Image
import io
import cv2


reader = easyocr.Reader(['en'])

def _resolver(query: str) -> str:
    img = cv2.imread("/Users/damien/git/hackathon/resouces/image.png")
    results = reader.readtext(img)
    extracted_texts = [res[1] for res in results]
    return "\n".join(extracted_texts)

task = Task(
    name="OCR",
    description=(
        "Optical Character Recognition for images and scanned documents. Returns extracted "
        "text along with confidence metadata when available. Input: images or image URLs; "
        "Output: raw extracted text and structured fields for tables/forms. Edge cases: low-"
        "quality images, handwriting, mixed languages - resolver should attempt language "
        "detection and fallback gracefully."
    ),
    resolver=_resolver,
)
