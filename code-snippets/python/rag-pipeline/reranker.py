"""
Cross-Encoder Reranking Module for QueryLex

Implements reranking using sentence-transformers cross-encoder model
to improve retrieval accuracy by 15-25%.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache

# Lazy load heavy dependencies
_reranker_model = None


def get_reranker_model():
    """Lazy load the cross-encoder model to avoid startup overhead."""
    global _reranker_model
    if _reranker_model is None:
        try:
            from sentence_transformers import CrossEncoder
            # ms-marco-MiniLM-L-6-v2 is fast and effective for reranking
            # ~22M params, ~50-100ms per batch on CPU
            _reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            print("[RERANKER] Loaded cross-encoder/ms-marco-MiniLM-L-6-v2")
        except ImportError:
            print("[RERANKER] sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"[RERANKER] Error loading model: {e}")
            raise
    return _reranker_model


class CrossEncoderReranker:
    """
    Cross-Encoder based reranker for two-stage retrieval.

    Stage 1: Fast bi-encoder retrieval (vector search) - already done
    Stage 2: Cross-encoder reranking for precision (this class)

    The cross-encoder scores query-document pairs jointly,
    which is more accurate than bi-encoder similarity but slower.
    """

    def __init__(self, top_k: int = 5):
        """
        Initialize the reranker.

        Args:
            top_k: Number of documents to return after reranking
        """
        self.top_k = top_k
        self._model = None

    @property
    def model(self):
        """Lazy load the model on first use."""
        if self._model is None:
            self._model = get_reranker_model()
        return self._model

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        document_key: str = 'document',
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cross-encoder scoring.

        Args:
            query: The search query
            documents: List of document dicts from initial retrieval
            document_key: Key containing the document text in each dict
            top_k: Override default top_k for this call

        Returns:
            Reranked list of documents with added 'rerank_score' field
        """
        if not documents:
            return []

        k = top_k if top_k is not None else self.top_k

        # If we have fewer documents than top_k, just return them with scores
        if len(documents) <= k:
            # Still score them for consistency
            return self._score_and_sort(query, documents, document_key)[:k]

        start_time = time.time()

        # Score and sort
        reranked = self._score_and_sort(query, documents, document_key)

        elapsed = time.time() - start_time
        print(f"[RERANKER] Reranked {len(documents)} docs in {elapsed*1000:.0f}ms, returning top {k}")

        return reranked[:k]

    def _score_and_sort(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        document_key: str
    ) -> List[Dict[str, Any]]:
        """Score all documents and sort by score descending."""
        # Build query-document pairs
        pairs = []
        for doc in documents:
            text = doc.get(document_key, '')
            if not text:
                # Try alternative keys
                text = doc.get('text', doc.get('content', ''))
            pairs.append([query, text])

        # Get cross-encoder scores
        try:
            scores = self.model.predict(pairs)
        except Exception as e:
            print(f"[RERANKER] Error scoring documents: {e}")
            # Return original order with default scores
            for doc in documents:
                doc['rerank_score'] = 0.0
            return documents

        # Add scores to documents
        scored_docs = []
        for i, doc in enumerate(documents):
            doc_copy = doc.copy()
            doc_copy['rerank_score'] = float(scores[i])
            # Keep original rank for reference
            doc_copy['original_rank'] = i + 1
            scored_docs.append(doc_copy)

        # Sort by rerank score descending
        scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)

        # Add new rank
        for i, doc in enumerate(scored_docs):
            doc['reranked_position'] = i + 1

        return scored_docs


def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 5,
    enabled: bool = True
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convenience function to rerank search results.

    Args:
        query: Search query
        results: List of search results with 'document' or 'text' field
        top_k: Number of results to return
        enabled: Whether reranking is enabled

    Returns:
        Tuple of (reranked results, metadata about the reranking)
    """
    metadata = {
        'reranking_enabled': enabled,
        'input_count': len(results),
        'output_count': 0,
        'latency_ms': 0
    }

    if not enabled or not results:
        metadata['output_count'] = len(results)
        return results, metadata

    start_time = time.time()

    try:
        reranker = CrossEncoderReranker(top_k=top_k)
        reranked = reranker.rerank(query, results)

        metadata['output_count'] = len(reranked)
        metadata['latency_ms'] = int((time.time() - start_time) * 1000)

        return reranked, metadata

    except Exception as e:
        print(f"[RERANKER] Error during reranking: {e}")
        metadata['error'] = str(e)
        metadata['output_count'] = len(results)
        return results, metadata


# For testing
if __name__ == "__main__":
    # Test the reranker
    test_query = "What are the penalties for antitrust violations?"
    test_docs = [
        {"document": "The Sherman Act prohibits monopolization and attempts to monopolize.", "id": "1"},
        {"document": "Antitrust penalties can include fines up to $100 million for corporations.", "id": "2"},
        {"document": "The weather today is sunny and warm.", "id": "3"},
        {"document": "Criminal penalties for antitrust violations include imprisonment up to 10 years.", "id": "4"},
    ]

    reranked, meta = rerank_results(test_query, test_docs, top_k=3)

    print(f"\nQuery: {test_query}\n")
    print(f"Reranking metadata: {meta}\n")
    print("Reranked results:")
    for doc in reranked:
        print(f"  Score: {doc['rerank_score']:.4f} | Original rank: {doc['original_rank']} | {doc['document'][:60]}...")
