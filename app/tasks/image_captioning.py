"""Image captioning task resolver.

Usage example (requires `transformers` and model download):

    from PIL import Image
    from app.tasks.image_captioning import _resolver

    img = Image.open('/path/to/image.png')
    out = _resolver(img)
    print(out['caption'], out['time_seconds'])

Note: URL fetching is intentionally omitted to avoid network calls inside the resolver; pass
an already-downloaded PIL Image or a local path.
"""

from pathlib import Path
from typing import Any

from PIL import Image

from app.tasks.base import Task

try:
    # Optional imports: transformers may not be installed in lightweight environments.
    from transformers import (
        AutoImageProcessor,
        AutoTokenizer,
        VisionEncoderDecoderModel,
    )
except Exception:
    AutoTokenizer = None  # type: ignore
    AutoImageProcessor = None  # type: ignore
    VisionEncoderDecoderModel = None  # type: ignore


_GLOBAL_MODEL: dict[str, Any] = {}


model = VisionEncoderDecoderModel.from_pretrained("cnmoro/tiny-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("cnmoro/tiny-image-captioning")
image_processor = AutoImageProcessor.from_pretrained("cnmoro/tiny-image-captioning", use_fast=True)


def _open_image(source: str | Path | Image.Image) -> Image.Image:
    """Accept a local file path, URL (not implemented), or PIL Image and return an RGB PIL Image.

    Note: URL support is intentionally not implemented to avoid network calls in the task function.
    If you need URL support, call `requests` externally and pass a PIL Image.
    """
    if isinstance(source, Image.Image):
        return source.convert("RGB")

    p = Path(str(source))
    if p.exists():
        return Image.open(p).convert("RGB")

    raise ValueError(f"Image source not found or unsupported: {source}")


def _resolver(
    query: str
 ) -> dict[str, Any]:
    img = _open_image("/home/onyxia/work/Router-POC/resouces/image copy.png")
    pixel_values = image_processor(img, return_tensors="pt").pixel_values
    generated_ids = model.generate(
        pixel_values,
        temperature=0.7,
        top_p=1,
        top_k=50,
        num_beams=3,
        max_length=25,
        min_length=1,
    )
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text


task = Task(
    name="Génération de légendes d'images",
    description=(
        "Générer des légendes descriptives et adaptées au contexte pour des images. "
        "Utile pour l'accessibilité, la modération de contenu et la génération de métadonnées. "
        "Entrée : image unique ou objet PIL Image ; "
        "Sortie : une courte légende descriptive."
        "Exemple : Légende-moi cette image !"
    ),
    resolver=_resolver,
)
