from functools import cached_property
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from app.logging_utils import get_logger
from app.tasks.base import Task
from app.tasks.image_captioning import task as image_captioning_task
from app.tasks.ocr import task as ocr_task
from app.tasks.translate import task as translate_task
from app.tasks.web_search import task as web_search_task

logger = get_logger(__name__)

class Maestro:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", threshold: float = 0.20, encoder_override: Any | None = None):
        """Initialize the Maestro router.

        embedding_model: name of the embedding model (E5 recommended)
        threshold: minimum cosine similarity to route to a specific model
        """

        self.embedding_model: str = "all-MiniLM-L6-v2"
        self.threshold: float = 0.0
        self.encoder_override: Any | None = None
        self.tasks: list[Task] = [
            translate_task,
            web_search_task,
            image_captioning_task,
            ocr_task,
        ]
        print("Maestro initialized with tasks:", [t.name for t in self.tasks])

    @cached_property
    def encoder(self) -> SentenceTransformer:
        enc = self.encoder_override or SentenceTransformer(self.embedding_model)
        logger.info("Encoder initialized with model: %s", self.embedding_model)
        return enc

    @cached_property
    def task_embeddings(self) -> np.ndarray:
        descs = [t.description for t in self.tasks]
        vectors = self.encoder.encode(descs)
        normalized = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        logger.info("Task embeddings computed for %d tasks", len(self.tasks))
        return normalized

    def find_task(self, query: str) -> Task | None:
        """Return the TaskSpec that best matches the query or None if below threshold."""
        query_vec = self.encoder.encode([query], normalize_embeddings=True)
        scores = (query_vec @ self.task_embeddings.T)[0]

        for task, score in zip(self.tasks, scores):
            logger.info(f"Tâche : {task.name} | Score : {score:.2f}")

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        best_task = self.tasks[best_idx]



        logger.info("Query routed to task: %s (score %.3f)", best_task.name, best_score)
        if best_score < self.threshold:
            logger.info("No task above threshold %.3f; using fallback", self.threshold)
            return None
        return best_task

        # scores = (query_vec @ self.model_vectors.T)[0]
        # best_idx = int(np.argmax(scores))
        # best_score = float(scores[best_idx])
        # best_spec = self.tasks[best_idx]

        # print("\n--- Routing Debug ---")
        # print(f"User query: {query!r}")
        # for spec, score in zip(self.tasks, scores, strict=False):
        #     print(f" {spec.task.value:20s} : {score:.3f}")
        # print("---------------------")

        # # Threshold logic
        # if best_score < self.threshold:
        #     print(f"Pas de modèle suffisamment pertinent - au-dessus du seuil de ({self.threshold}). Using fallback.")
        #     return None

        # print(f"→ Routed to: {best_spec.task.value} (score {best_score:.3f})")
        # return best_spec

    def handle_request(self, query: str, fallback_fn=None) -> str:
        task = self.find_task(query)
        if task is None:
            if fallback_fn:
                return fallback_fn(query)
            return "[No suitable task found]"
        return task.resolve(query)

maestro = Maestro()
