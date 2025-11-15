from sentence_transformers import SentenceTransformer
import numpy as np


class ModelRouter:
    def __init__(self, model_descriptions, model_functions, embedding_model="all-MiniLM-L6-v2", threshold=0.40):
        """
        model_descriptions: dict {model_name: description text}
        model_functions: dict {model_name: function_to_call}
        embedding_model: name of the embedding model (E5 recommended)
        threshold: minimum cosine similarity to route to a specific model
        """
        self.model_descriptions = model_descriptions
        self.model_functions = model_functions
        self.threshold = threshold

        # Load embedding model (stocké sous le nom de "encoder")
        self.encoder = SentenceTransformer(embedding_model)

        # Precompute description embeddings
        self.model_names = list(model_descriptions.keys())
        desc_texts = [model_descriptions[name] for name in self.model_names]

        # fait encoder sous forme vectorielle au modèle encoder nos descriptions textuelles
        self.model_vectors = self.encoder.encode(desc_texts, normalize_embeddings=True)
        print("Router initialized with models:", self.model_names)

    def route(self, query):
        """
        Returns the name of the best model for the query,
        or None if no model matches the threshold.
        """

        # Encode query with the model "encoder"
        query_vec = self.encoder.encode([query], normalize_embeddings=True)

        # Compute cosine scores - plus le score est élevé, plus les embeddings sont proches
        scores = (query_vec @ self.model_vectors.T)[0]

        # Identify best model
        best_idx = np.argmax(scores) # renvoie l’indice du modèle dont la description est la plus proche de la requête.
        best_score = scores[best_idx] # renvoie le score correspondant à cet indice
        best_model = self.model_names[best_idx] # renvoie le nom du modèle correspondant à cet indice

        # Debug display
        print("\n--- Routing Debug ---")
        print(f"User query: {query!r}") # Le !r force l’affichage repr(), donc les guillemets et caractères spéciaux sont visibles
        for name, score in zip(self.model_names, scores):
            print(f" {name:20s} : {score:.3f}")
        print("---------------------")

        # Threshold logic - si aucun modèle n'obtient un score de similarité cosine supérieur à treshold, il répond par ce texte :
        if best_score < self.threshold:
            print(f"Pas de modèle suffisamment pertinent - au-dessus du seuil de ({self.threshold}). Using fallback.")
            return None

        print(f"→ Routed to: {best_model} (score {best_score:.3f})")
        return best_model

    def handle_request(self, query, fallback_fn=None):
        """
        Route the query and execute the corresponding model function.
        fallback_fn: function to call if no model matches threshold
        """
        model_name = self.route(query)
        if model_name is None:
            if fallback_fn:
                return fallback_fn(query)
            else:
                return "[No suitable model found]"
        else:
            fn = self.model_functions[model_name]
            return fn(query)




#######################################################################

#                   utilisation du nom du meilleur modèle
#                   pour lui envoyer le prompt utilisateur

#######################################################################


# --- Exemple de fonctions simulant les modèles ---
def summarizer(prompt):
    return f"[Résumé automatique] {prompt[:50]}..."

def translator(prompt):
    return f"[Traduction FR↔EN] {prompt}"

def math_explainer(prompt):
    return f"[Explication Maths] {prompt}"

def python_coder(prompt):
    return f"[Code Python] {prompt}"



# --- Exemple d’utilisation ---
if __name__ == "__main__":

    # Définir les modèles
    descriptions = {
        "summarizer": "Résumé automatique de textes courts, ton concis et neutre.",
        "translator": "Traduction français ↔ anglais, fidélité au sens.",
        "math_explainer": "Explication claire de concepts mathématiques simples.",
        "python_coder": "Génération de code Python clair, commenté."
    }

    functions = {
        "summarizer": summarizer,
        "translator": translator,
        "math_explainer": math_explainer,
        "python_coder": python_coder
    }

    router = ModelRouter(descriptions, functions)

    # Exemple de requêtes
    queries = [
        "Peux-tu m'expliquer comment fonctionne une dérivée ?",
        "Résume-moi ce paragraphe en 5 phrases.",
        "Traduis ce texte en anglais.",
        "Écris un script Python pour scraper un site.",
        "Comment réparer une fuite d'eau ?"
    ]

    # Fonction de fallback
    def general_fallback(prompt):
        return f"[Fallback] Je ne sais pas exactement quel modèle utiliser pour: {prompt}"

    # Exécution
    for q in queries:
        response = router.handle_request(q, fallback_fn=general_fallback)
        print("Response:", response)