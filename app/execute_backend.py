# %%
def mock_llm(prompt: str):
    """
    A simple mocked LLM that pretends to generate a model output.
    """
    return {
        "response": f"This is a mocked LLM response to: '{prompt}'",
    }


def mock_web_search(query: str):
    """
    A mocked web search that returns a fixed structure.
    """
    return [
        {
            "url": "https://example.com/1",
        },
        {
            "url": "https://example.com/2",
        }
    ]



# Réponse structurée
# Réponse non-structurée

# Réponse de recherche web
# remonter l'information issue d'un document joint
# 
# Traduction
# Code generation
# LLM
# SLM specialized for reformulation
# SLM specialized for 
# TTS

# VLM
# OCR
# image analysis
# image captioning
# depth estimation

# File generation
# image finding
# Image editing
# image generation


class SearchModule:
    def __init__(self):
        self.routes = {
            "web_search": self._web_search,
            "web_search_slm": self._web_search_llm,
            "raw_rag": self._rag,
            "rag_slm": self._llm_rag,

            "llm": self._llm,
            "image_generation": self._vlm,
            "text_to_speech": self._tts,
        }

    def search(self, user_message: str, route: str):
        """
        Dispatches based on the route parameter.
        """
        route = route.lower()

        if route not in self.routes:
            raise ValueError(
                f"Unknown route '{route}'. Valid routes: {list(self.routes.keys())}"
            )

        return self.routes[route](user_message)

    def _llm(self, message):
        return mock_llm(message)

    def _web_search(self, user_message):
        return mock_web_search(user_message)
    
    def _web_search_llm(self, user_message):
        """Web search enhanced with LLM summarization."""
        search_results = mock_web_search(user_message)
        summary = mock_llm(f"Summarize these search results: {search_results}")
        return {
            "search_results": search_results,
            "summary": summary["response"]
        }
    
    def _rag(self, user_message):
        """Raw RAG (Retrieval-Augmented Generation) without LLM."""
        return {
            "retrieved_docs": [
                {"id": "doc1", "content": "Sample document 1 content", "score": 0.95},
                {"id": "doc2", "content": "Sample document 2 content", "score": 0.87}
            ],
            "query": user_message
        }
    
    def _llm_rag(self, user_message):
        """RAG with LLM-enhanced retrieval and generation."""
        rag_results = self._rag(user_message)
        context = " ".join([doc["content"] for doc in rag_results["retrieved_docs"]])
        response = mock_llm(f"Using context: {context}, answer: {user_message}")
        return {
            "retrieved_docs": rag_results["retrieved_docs"],
            "llm_response": response["response"]
        }
    
    def _vlm(self, user_message):
        """Vision-Language Model for image generation."""
        return {
            "generated_image_url": "https://example.com/generated_image.png",
            "prompt": user_message,
            "model": "mock-vlm-1.0"
        }
    
    def _tts(self, user_message):
        """Text-to-Speech conversion."""
        return {
            "audio_url": "https://example.com/audio.mp3",
            "text": user_message,
            "duration_seconds": len(user_message) * 0.1,
            "voice": "default"
        }

# %%
router = SearchModule()

example_llm = router.search("Explain embeddings", route="llm")
example_web = router.search("Python packaging news", route="web_search")
example_llm["response"]

# %%
example_web


