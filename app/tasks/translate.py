import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.tasks.base import Task


def text_query(query):
    """
    Retourne toujours le texte à traiter sous forme de string.
    """
    if isinstance(query, dict):
        return query.get("text", "")
    elif isinstance(query, str):
        return query
    else:
        raise TypeError(f"Unsupported query type: {type(query)}")


# ---------------------------------------------------------------------
#                CONFIG - NLLB-200 1.3B
# ---------------------------------------------------------------------

_MODEL_NAME = "facebook/nllb-200-1.3B"

# Mapping minimal pour ton cas FR ↔ EN
_LANG_DETECT = {
    "fr": "fra_Latn",
    "en": "eng_Latn",
}

# Charge le modèle uniquement au premier appel
_model = None
_tokenizer = None


def _load_nllb():
    global _model, _tokenizer

    if _model is None:
        print("[Translate] Loading NLLB-200 1.3B…")

        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)

        _model = AutoModelForSeq2SeqLM.from_pretrained(
            _MODEL_NAME,
            torch_dtype=torch.float16,  # indispensable pour 1.3B, sinon OOM
            device_map="cuda" if torch.cuda.is_available() else "cpu",          # GPU si dispo, CPU sinon
        )

        print("[Translate] Model loaded successfully.")

    return _tokenizer, _model


# ---------------------------------------------------------------------
#                UTIL : Détection ultra simple de langue
# ---------------------------------------------------------------------

def _detect_language(text: str) -> str:
    """
    On reste frugal → une heuristique ultra simple suffit ici.
    NLLB exige des codes spécifiques (fra_Latn, eng_Latn).
    """
    text_low = text.lower()

    # Quelques heuristiques très efficaces pour FR/EN
    fr_markers = ["é", "è", "ç", "à", "ou", "est", "avec", "pour", "dans"]
    en_markers = ["the ", "and ", "with ", "from ", "you ", "is ", "are "]

    if any(m in text_low for m in fr_markers):
        return "fra_Latn"
    if any(m in text_low for m in en_markers):
        return "eng_Latn"

    # fallback : supposons FR → très conservateur
    return "fra_Latn"


# ---------------------------------------------------------------------
#                FONCTION PRINCIPALE : traduction
# ---------------------------------------------------------------------

def _translate_resolver(query: dict) -> dict:
    """
    Appelé par le routeur.
    Prend un texte (FR ou EN) et renvoie la traduction dans l'autre langue.
    """
    tokenizer, model = _load_nllb()

    # récupérer la partie prompt textuel du dictionnaire query
    text = text_query(query)

    # détecte la langue source
    src_lang = _detect_language(text)

    # déduit la langue cible
    tgt_lang = "eng_Latn" if src_lang == "fra_Latn" else "fra_Latn"

    # encode
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(model.device)

    # génération (beam search pour qualité max)
    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang),
            max_length=1000,
            num_beams=5,
            length_penalty=0.95
        )

    # decode
    translation = tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )[0]

    return translation


# ---------------------------------------------------------------------
#                MODULE TASK EXPORTÉ
# ---------------------------------------------------------------------

task = Task(
    name="Traduction",
    description=(
        "Traduction bilingue haute fidélité (Français <-> Anglais) utilisant NLLB-200 1.3B. "
        "Préserve le sens, le ton, la terminologie spécifique au domaine et les expressions idiomatiques. "
        "Gère les entités et fragments de code en toute sécurité. "
        "Entrée : texte brut en FR ou EN ; "
        "Sortie : texte traduit."
    ),
    resolver=_translate_resolver,
)
