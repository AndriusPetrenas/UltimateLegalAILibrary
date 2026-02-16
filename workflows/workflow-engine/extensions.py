"""
Standalone helper functions for the workflow engine.

Provides the same interface as QueryLex's app.extensions module,
using the RAG pipeline modules directly.

Usage:
    Make sure the rag-pipeline directory is on your Python path:
        sys.path.insert(0, "/path/to/rag-pipeline")

    Then import as usual:
        from extensions import get_authenticated_vector_client, get_embedding_service, device
"""

import os

# Device detection (GPU if available, else CPU)
try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    device = "cpu"

# Cache for embedding service instances
_embedding_service_cache = {}


def get_embedding_service(model_name: str = "text-embedding-3-small"):
    """Get an embedding service instance for the specified model.

    Args:
        model_name: Name of the embedding model (e.g., 'text-embedding-3-small', 'embed-v3')

    Returns:
        EmbeddingService instance configured for the specified model
    """
    global _embedding_service_cache

    if model_name in _embedding_service_cache:
        return _embedding_service_cache[model_name]

    from embedding_service import EmbeddingService
    service = EmbeddingService(model_name=model_name)
    _embedding_service_cache[model_name] = service
    return service


def get_authenticated_vector_client(access_token=None):
    """Get a SupabaseVectorClient.

    In standalone mode, this uses the service key from environment variables.
    In production (QueryLex), this uses the user's JWT access token for RLS.

    Args:
        access_token: Optional JWT access token (ignored in standalone mode)

    Returns:
        SupabaseVectorClient instance
    """
    from supabase_client import SupabaseVectorClient
    return SupabaseVectorClient(use_service_key=True)
