
import cv2
import easyocr

from app.tasks.base import Task

reader = easyocr.Reader(['en'])

def _resolver(query: str) -> str:
    img = cv2.imread("/home/onyxia/work/Router-POC/resouces/image.png")
    results = reader.readtext(img)
    extracted_texts = [res[1] for res in results]
    return "\n".join(extracted_texts)

task = Task(
    name="OCR",
    description=(
        "Reconnaissance optique de caractères pour images et documents scannés. "
        "Renvoie le texte extrait avec les métadonnées de confiance lorsque disponibles. "
        "Entrée : images ou URL d'images ; "
        "Sortie : texte brut extrait et champs structurés pour tableaux/formulaires. "
        "Cas particuliers : images de faible qualité, écriture manuscrite, langues mixtes - "
        "le résolveur doit tenter la détection de la langue et gérer les cas limites avec souplesse."
    ),
    resolver=_resolver,
)
