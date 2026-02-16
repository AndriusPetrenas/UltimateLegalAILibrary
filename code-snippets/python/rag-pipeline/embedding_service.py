"""
Multi-provider embedding service supporting:
- OpenAI text-embedding-3-small (1536 dimensions)
- Cohere embed-v3 (1024 dimensions)
- Isaacus Kanon 2 Embedder (1792 dimensions)
- Voyage voyage-3-large (1024 dimensions)
- OpenRouter Qwen3 Embedding 8B (1024 dimensions)
"""

import os
import logging
import requests
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Embedding model configurations with model-specific chunking parameters
# Each model has optimal chunk sizes based on:
# - Maximum input token limit
# - Model architecture (some handle longer context better)
# - Use case optimization (legal docs often need more context)
EMBEDDING_MODELS = {
    "text-embedding-3-small": {
        "provider": "openai",
        "dimensions": 1536,
        "max_tokens": 8191,
        "chunk_size_tokens": 256,  # Good balance for general retrieval
        "chunk_overlap_tokens": 50,
        "description": "OpenAI's efficient embedding model",
        "cost": "$0.02 per 1M tokens"
    },
    "embed-v3": {
        "provider": "cohere",
        "dimensions": 1024,
        "max_tokens": 512,  # Lower limit - need smaller chunks
        "chunk_size_tokens": 384,  # Leave room for ~50 token context prefix
        "chunk_overlap_tokens": 75,
        "description": "Cohere's multilingual embedding model",
        "cost": "$0.10 per 1M tokens"
    },
    "kanon-2-embedder": {
        "provider": "isaacus",
        "dimensions": 1792,
        "max_tokens": 4096,
        "chunk_size_tokens": 512,  # Legal-specialized: benefits from more context
        "chunk_overlap_tokens": 100,
        "description": "Isaacus legal-specialized embeddings",
        "cost": "$0.35 per 1M tokens"
    },
    "voyage-3-large": {
        "provider": "voyage",
        "dimensions": 1024,
        "max_tokens": 32000,
        "chunk_size_tokens": 384,  # Balance between context and precision
        "chunk_overlap_tokens": 75,
        "description": "Voyage AI's high-quality embeddings",
        "cost": "$0.06 per 1M tokens"
    },
    "qwen3-embedding-8b": {
        "provider": "openrouter",
        "dimensions": 1024,
        "max_tokens": 8192,
        "chunk_size_tokens": 256,  # Conservative default
        "chunk_overlap_tokens": 50,
        "description": "Qwen3 8B embedding via OpenRouter",
        "cost": "Variable pricing"
    }
}


def get_chunk_config(model_name: str) -> dict:
    """Get chunking configuration for a specific embedding model.

    Args:
        model_name: Name of the embedding model

    Returns:
        Dictionary with chunk_size_tokens, chunk_overlap_tokens, max_tokens
    """
    config = EMBEDDING_MODELS.get(model_name, EMBEDDING_MODELS["text-embedding-3-small"])
    return {
        "chunk_size_tokens": config.get("chunk_size_tokens", 256),
        "chunk_overlap_tokens": config.get("chunk_overlap_tokens", 50),
        "max_tokens": config.get("max_tokens", 8191)
    }


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        pass


class OpenAIEmbedding(BaseEmbeddingProvider):
    """OpenAI text-embedding-3-small provider"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.model = "text-embedding-3-small"
        self.dimensions = 1536

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # OpenAI has a batch limit, process in chunks
        all_embeddings = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json={
                    "model": self.model,
                    "input": batch
                },
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")

            data = response.json()
            batch_embeddings = [item["embedding"] for item in data["data"]]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._get_embeddings([text])
        return embeddings[0]


class CohereEmbedding(BaseEmbeddingProvider):
    """Cohere embed-v3 provider"""

    def __init__(self):
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
        self.model = "embed-multilingual-v3.0"
        self.dimensions = 1024

    def _get_embeddings(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """Get embeddings from Cohere API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Cohere has a batch limit of 96 texts
        all_embeddings = []
        batch_size = 96

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = requests.post(
                "https://api.cohere.ai/v1/embed",
                headers=headers,
                json={
                    "model": self.model,
                    "texts": batch,
                    "input_type": input_type,
                    "truncate": "END"
                },
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"Cohere API error: {response.text}")
                raise Exception(f"Cohere API error: {response.status_code}")

            data = response.json()
            all_embeddings.extend(data["embeddings"])

        return all_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts, input_type="search_document")

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._get_embeddings([text], input_type="search_query")
        return embeddings[0]


class IsaacusEmbedding(BaseEmbeddingProvider):
    """Isaacus Kanon 2 Embedder provider"""

    def __init__(self):
        self.api_key = os.getenv("ISAACUS_API_KEY")
        if not self.api_key:
            raise ValueError("ISAACUS_API_KEY environment variable not set")
        self.model = "kanon-2-embedder"
        self.dimensions = 1792

    def _get_embeddings(self, texts: List[str], task: str = "retrieval/document") -> List[List[float]]:
        """Get embeddings from Isaacus API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_embeddings = []
        # Process in batches for Isaacus
        batch_size = 50

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = requests.post(
                "https://api.isaacus.com/v1/embeddings",
                headers=headers,
                json={
                    "model": self.model,
                    "texts": batch,
                    "task": task
                },
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"Isaacus API error: {response.text}")
                raise Exception(f"Isaacus API error: {response.status_code}")

            data = response.json()
            # Isaacus returns: {"embeddings": [{"index": 0, "embedding": [...]}], "usage": {...}}
            if "embeddings" in data:
                batch_embeddings = [item["embedding"] for item in data["embeddings"]]
                all_embeddings.extend(batch_embeddings)
            elif "data" in data:
                batch_embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts, task="retrieval/document")

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._get_embeddings([text], task="retrieval/query")
        return embeddings[0]


class VoyageEmbedding(BaseEmbeddingProvider):
    """Voyage AI voyage-3-large provider"""

    def __init__(self):
        self.api_key = os.getenv("VOYAGE_API_KEY")
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY environment variable not set")
        self.model = "voyage-3-large"
        self.dimensions = 1024

    def _get_embeddings(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """Get embeddings from Voyage API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_embeddings = []
        batch_size = 128  # Voyage supports up to 128 texts per batch

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = requests.post(
                "https://api.voyageai.com/v1/embeddings",
                headers=headers,
                json={
                    "model": self.model,
                    "input": batch,
                    "input_type": input_type
                },
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"Voyage API error: {response.text}")
                raise Exception(f"Voyage API error: {response.status_code}")

            data = response.json()
            batch_embeddings = [item["embedding"] for item in data["data"]]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts, input_type="document")

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._get_embeddings([text], input_type="query")
        return embeddings[0]


class OpenRouterEmbedding(BaseEmbeddingProvider):
    """OpenRouter Qwen3 Embedding 8B provider"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        self.model = "qwen/qwen3-embedding-8b"
        self.dimensions = 1024  # Request 1024 dimensions (model supports 32-4096 via MRL)

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_embeddings = []
        batch_size = 50

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers=headers,
                json={
                    "model": self.model,
                    "input": batch,
                    "dimensions": self.dimensions  # Request specific dimension (Qwen3 supports MRL)
                },
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code}")

            data = response.json()
            batch_embeddings = [item["embedding"] for item in data["data"]]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> List[float]:
        embeddings = self._get_embeddings([text])
        return embeddings[0]


class EmbeddingService:
    """
    Main embedding service that routes to the appropriate provider
    based on the model name.
    """

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.model_config = EMBEDDING_MODELS.get(model_name)

        if not self.model_config:
            raise ValueError(f"Unknown embedding model: {model_name}")

        self.provider = self._get_provider()
        self.dimensions = self.model_config["dimensions"]

    def _get_provider(self) -> BaseEmbeddingProvider:
        """Get the appropriate embedding provider based on model name"""
        provider_name = self.model_config["provider"]

        if provider_name == "openai":
            return OpenAIEmbedding()
        elif provider_name == "cohere":
            return CohereEmbedding()
        elif provider_name == "isaacus":
            return IsaacusEmbedding()
        elif provider_name == "voyage":
            return VoyageEmbedding()
        elif provider_name == "openrouter":
            return OpenRouterEmbedding()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        logger.info(f"Embedding {len(texts)} documents with {self.model_name}")
        return self.provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        logger.info(f"Embedding query with {self.model_name}")
        return self.provider.embed_query(text)

    def get_vector_column(self) -> str:
        """Get the database column name for this embedding dimension"""
        if self.dimensions == 1536:
            return "embedding"  # Original column for OpenAI
        elif self.dimensions == 1024:
            return "embedding_1024"
        elif self.dimensions == 1792:
            return "embedding_1792"
        else:
            raise ValueError(f"No column for dimension: {self.dimensions}")

    def get_match_function(self) -> str:
        """Get the RPC function name for matching documents"""
        if self.dimensions == 1536:
            return "match_documents"  # Original function for OpenAI
        elif self.dimensions == 1024:
            return "match_documents_1024"
        elif self.dimensions == 1792:
            return "match_documents_1792"
        else:
            raise ValueError(f"No match function for dimension: {self.dimensions}")


def get_embedding_models_for_ui() -> List[dict]:
    """Get embedding models formatted for UI dropdown"""
    models = []
    for model_name, config in EMBEDDING_MODELS.items():
        models.append({
            "id": model_name,
            "name": model_name,
            "description": config["description"],
            "cost": config["cost"],
            "dimensions": config["dimensions"],
            "provider": config["provider"]
        })
    return models
