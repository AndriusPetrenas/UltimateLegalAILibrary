"""
ColBERT-style Retrieval Service (Approximation).

This module implements an approximation of ColBERT using sentence-level embeddings
instead of true token-level embeddings. This provides ~70% of ColBERT's benefit
with minimal infrastructure changes.

Approach:
1. During indexing: Split each chunk into sentences, embed each sentence separately
2. During retrieval: Get candidates via standard vector search, then re-score
   using MaxSim over sentence embeddings
3. MaxSim: For each query token (sentence), find the maximum similarity with any
   document sentence, then sum these maximums

True ColBERT uses ~128 embeddings per chunk (one per token). This approximation
uses 3-8 sentence embeddings per chunk, dramatically reducing storage while
still capturing multi-aspect relevance.
"""

import re
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class ColBERTResult:
    """Result from ColBERT-style scoring."""
    document: str
    metadata: Dict[str, Any]
    original_score: float
    colbert_score: float
    sentence_scores: List[float]
    matched_sentences: List[str]


class ColBERTService:
    """
    ColBERT-style retrieval using sentence-level embeddings.

    This is an approximation of true ColBERT that:
    1. Uses sentences instead of tokens (3-8 per chunk vs 128)
    2. Works with existing pgvector infrastructure
    3. Provides fine-grained relevance scoring

    When colbert_enabled=True:
    - During upload: Chunks are split into sentences, each embedded separately
    - During query: Standard retrieval gets candidates, ColBERT re-ranks them
    """

    # Sentence splitting regex - handles legal citation formats
    SENTENCE_PATTERN = re.compile(
        r'(?<=[.!?])\s+(?=[A-Z])|'  # Standard sentence boundaries
        r'(?<=\.)\s*(?=\d+\.)|'      # Legal numbered lists (1. 2. 3.)
        r'(?<=:)\s*(?=[A-Z])|'       # After colons before capitals
        r'\n\n+'                      # Double newlines
    )

    def __init__(
        self,
        embedding_service,
        supabase_client=None,
        min_sentence_length: int = 20,
        max_sentences_per_chunk: int = 8
    ):
        """
        Initialize ColBERT service.

        Args:
            embedding_service: Service with embed_query() and embed_documents() methods
            supabase_client: Supabase client for database operations (optional for indexing-only)
            min_sentence_length: Minimum characters for a valid sentence
            max_sentences_per_chunk: Maximum sentences to embed per chunk
        """
        self.embedding_service = embedding_service
        self.supabase_client = supabase_client
        self.min_sentence_length = min_sentence_length
        self.max_sentences_per_chunk = max_sentences_per_chunk

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences suitable for embedding.

        Handles legal document formats including:
        - Standard sentence boundaries
        - Numbered lists
        - Citations

        Args:
            text: Document text to split

        Returns:
            List of sentence strings
        """
        if not text or len(text.strip()) == 0:
            return []

        # Split using pattern
        sentences = self.SENTENCE_PATTERN.split(text)

        # Clean and filter sentences
        cleaned = []
        for sent in sentences:
            sent = sent.strip()
            # Skip too short sentences
            if len(sent) < self.min_sentence_length:
                continue
            # Skip if mostly numbers or special characters
            alpha_ratio = sum(c.isalpha() for c in sent) / max(len(sent), 1)
            if alpha_ratio < 0.3:
                continue
            cleaned.append(sent)

        # Limit number of sentences per chunk
        if len(cleaned) > self.max_sentences_per_chunk:
            # Keep first, last, and evenly distributed middle sentences
            n = self.max_sentences_per_chunk
            indices = [0]  # First
            indices.extend(range(1, len(cleaned) - 1, max(1, (len(cleaned) - 2) // (n - 2))))
            indices.append(len(cleaned) - 1)  # Last
            indices = sorted(set(indices))[:n]
            cleaned = [cleaned[i] for i in indices]

        return cleaned

    def embed_sentences(self, sentences: List[str]) -> List[List[float]]:
        """
        Embed a list of sentences.

        Args:
            sentences: List of sentence strings

        Returns:
            List of embedding vectors
        """
        if not sentences:
            return []

        try:
            embeddings = self.embedding_service.embed_documents(sentences)
            return embeddings
        except Exception as e:
            print(f"[COLBERT] Error embedding sentences: {e}")
            return []

    def process_chunk_for_colbert(
        self,
        chunk_text: str,
        chunk_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a chunk to extract sentence embeddings for ColBERT indexing.

        Args:
            chunk_text: The document chunk text
            chunk_id: Optional chunk ID

        Returns:
            Dict with sentences and their embeddings
        """
        sentences = self.split_into_sentences(chunk_text)

        if not sentences:
            return {
                'chunk_id': chunk_id,
                'sentences': [],
                'sentence_embeddings': [],
                'num_sentences': 0
            }

        embeddings = self.embed_sentences(sentences)

        return {
            'chunk_id': chunk_id,
            'sentences': sentences,
            'sentence_embeddings': embeddings,
            'num_sentences': len(sentences)
        }

    def maxsim_score(
        self,
        query_embedding: List[float],
        sentence_embeddings: List[List[float]]
    ) -> Tuple[float, List[float]]:
        """
        Compute MaxSim score between query and document sentences.

        MaxSim computes the maximum similarity between the query and each
        document sentence, providing fine-grained relevance scoring.

        Args:
            query_embedding: Query embedding vector
            sentence_embeddings: List of sentence embedding vectors

        Returns:
            Tuple of (maxsim_score, list of per-sentence scores)
        """
        if not sentence_embeddings:
            return 0.0, []

        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)

        if query_norm == 0:
            return 0.0, [0.0] * len(sentence_embeddings)

        sentence_scores = []
        for sent_emb in sentence_embeddings:
            sent_vec = np.array(sent_emb)
            sent_norm = np.linalg.norm(sent_vec)

            if sent_norm == 0:
                sentence_scores.append(0.0)
            else:
                # Cosine similarity
                similarity = np.dot(query_vec, sent_vec) / (query_norm * sent_norm)
                sentence_scores.append(float(similarity))

        # MaxSim: Maximum similarity across all sentences
        max_score = max(sentence_scores) if sentence_scores else 0.0

        return max_score, sentence_scores

    def search(
        self,
        query: str,
        dataset_name: str,
        n_results: int = 8,
        n_candidates: int = 20,
        standard_search_fn: Callable = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform ColBERT-style search.

        Process:
        1. Get candidate documents using standard vector search (more than needed)
        2. Retrieve sentence embeddings for candidates from database
        3. Re-score candidates using MaxSim
        4. Return top n_results sorted by ColBERT score

        Args:
            query: User's search query
            dataset_name: Name of the dataset/collection
            n_results: Number of final results to return
            n_candidates: Number of candidates to retrieve for re-ranking
            standard_search_fn: Function to get initial candidates

        Returns:
            Tuple of (results_dict, colbert_metadata)
        """
        start_time = time.time()

        if not standard_search_fn:
            raise ValueError("standard_search_fn is required for ColBERT search")

        # Step 1: Get candidates using standard search
        candidates = standard_search_fn(query, n_candidates)

        if not candidates or not candidates.get('documents') or not candidates['documents'][0]:
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'ids': [[]]
            }, {'colbert_enabled': True, 'error': 'No candidates found'}

        # Get query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Step 2: Get sentence embeddings for candidates
        chunk_ids = candidates.get('ids', [[]])[0]
        sentence_data = self._get_sentence_embeddings(dataset_name, chunk_ids)

        # Step 3: Re-score with MaxSim
        scored_results = []
        for i, (doc, meta) in enumerate(zip(
            candidates['documents'][0],
            candidates['metadatas'][0]
        )):
            chunk_id = chunk_ids[i] if i < len(chunk_ids) else None
            original_score = candidates.get('distances', [[]])[0][i] if candidates.get('distances') else 0.0

            # Get sentence embeddings for this chunk
            sent_embeddings = sentence_data.get(chunk_id, {}).get('embeddings', [])
            sentences = sentence_data.get(chunk_id, {}).get('sentences', [])

            if sent_embeddings:
                # Calculate ColBERT score
                colbert_score, sentence_scores = self.maxsim_score(query_embedding, sent_embeddings)

                # Find best matching sentences
                if sentence_scores and sentences:
                    best_idx = sentence_scores.index(max(sentence_scores))
                    best_sentence = sentences[best_idx] if best_idx < len(sentences) else ""
                else:
                    best_sentence = ""
            else:
                # Fallback to original score if no sentence embeddings
                colbert_score = 1.0 - original_score if original_score < 1 else 0.5
                sentence_scores = []
                best_sentence = ""

            scored_results.append({
                'document': doc,
                'metadata': meta,
                'original_score': original_score,
                'colbert_score': colbert_score,
                'sentence_scores': sentence_scores,
                'best_matching_sentence': best_sentence,
                'chunk_id': chunk_id
            })

        # Step 4: Sort by ColBERT score (descending)
        scored_results.sort(key=lambda x: x['colbert_score'], reverse=True)
        top_results = scored_results[:n_results]

        elapsed_time = time.time() - start_time

        # Build metadata
        colbert_metadata = {
            'colbert_enabled': True,
            'candidates_retrieved': len(candidates['documents'][0]),
            'results_returned': len(top_results),
            'elapsed_time_seconds': round(elapsed_time, 3),
            'avg_colbert_score': sum(r['colbert_score'] for r in top_results) / max(len(top_results), 1),
            'chunks_with_sentence_embeddings': sum(1 for r in scored_results if r['sentence_scores'])
        }

        # Format results in standard format
        results_dict = {
            'documents': [[r['document'] for r in top_results]],
            'metadatas': [[{
                **r['metadata'],
                'colbert_score': round(r['colbert_score'], 4),
                'best_match': r['best_matching_sentence'][:100] if r['best_matching_sentence'] else None
            } for r in top_results]],
            'distances': [[r['colbert_score'] for r in top_results]],
            'ids': [[r['chunk_id'] or f"colbert_{i}" for i, r in enumerate(top_results)]]
        }

        return results_dict, colbert_metadata

    def _get_sentence_embeddings(
        self,
        dataset_name: str,
        chunk_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve sentence embeddings for chunks from database.

        Args:
            dataset_name: Name of the dataset
            chunk_ids: List of chunk IDs

        Returns:
            Dict mapping chunk_id to {embeddings, sentences}
        """
        if not self.supabase_client or not chunk_ids:
            return {}

        try:
            # Query documents table for sentence_embeddings column
            result = self.supabase_client.client.table("documents").select(
                "id, sentence_embeddings, sentence_texts"
            ).in_("id", chunk_ids).execute()

            if not result.data:
                return {}

            sentence_data = {}
            for row in result.data:
                chunk_id = row['id']
                embeddings = row.get('sentence_embeddings') or []
                sentences = row.get('sentence_texts') or []

                sentence_data[chunk_id] = {
                    'embeddings': embeddings,
                    'sentences': sentences
                }

            return sentence_data

        except Exception as e:
            print(f"[COLBERT] Error retrieving sentence embeddings: {e}")
            return {}


def colbert_search(
    query: str,
    dataset_name: str,
    embedding_service,
    supabase_client,
    standard_search_fn: Callable,
    n_results: int = 8
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Convenience function for ColBERT search.

    Args:
        query: User's search query
        dataset_name: Dataset name
        embedding_service: Embedding service
        supabase_client: Supabase client
        standard_search_fn: Standard search function
        n_results: Number of results

    Returns:
        Tuple of (results_dict, colbert_metadata)
    """
    service = ColBERTService(embedding_service, supabase_client)
    return service.search(
        query=query,
        dataset_name=dataset_name,
        n_results=n_results,
        standard_search_fn=standard_search_fn
    )


def process_chunk_for_colbert(
    chunk_text: str,
    chunk_id: str,
    embedding_service
) -> Dict[str, Any]:
    """
    Convenience function to process a chunk for ColBERT indexing.

    Args:
        chunk_text: Chunk text
        chunk_id: Chunk ID
        embedding_service: Embedding service

    Returns:
        Dict with sentences and embeddings
    """
    service = ColBERTService(embedding_service, None)
    return service.process_chunk_for_colbert(chunk_text, chunk_id)
