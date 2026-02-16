"""
Query Decomposition Module for QueryLex

Breaks complex multi-part legal queries into simpler sub-queries
for more comprehensive retrieval.

Cost: ~$0.001-0.005 per query (depending on complexity)
Impact: +15-25% recall for complex analytical questions
"""

import json
import re
from typing import List, Dict, Any, Tuple


# Query Decomposition Prompts
DECOMPOSE_SYSTEM_PROMPT = """You are a legal research assistant. Your task is to analyze complex legal questions and break them into simpler sub-queries that can be searched independently.

Rules:
1. Only decompose if the question has multiple distinct parts
2. Each sub-query should be searchable independently
3. Preserve legal terminology and specificity
4. Return 2-4 sub-queries maximum
5. If the query is already simple, return it unchanged

Output format: JSON array of strings, e.g., ["sub-query 1", "sub-query 2"]"""

DECOMPOSE_USER_PROMPT_TEMPLATE = """Analyze this legal question and break it into simpler searchable sub-queries if needed:

Question: {query}

If the question is simple, return: ["{query}"]
If complex, return the sub-queries as a JSON array."""


class QueryDecomposer:
    """
    Query decomposition for complex legal questions.

    Breaks multi-part queries into simpler sub-queries
    that can be searched independently.
    """

    def __init__(self, enabled: bool = True, max_subqueries: int = 4):
        """
        Initialize query decomposer.

        Args:
            enabled: Whether decomposition is enabled
            max_subqueries: Maximum number of sub-queries to generate
        """
        self.enabled = enabled
        self.max_subqueries = max_subqueries
        self._client = None
        self.stats = {
            "queries_processed": 0,
            "decompositions": 0,
            "total_subqueries": 0,
            "errors": 0,
            "total_time_ms": 0
        }

    @property
    def client(self):
        """Lazy load the LLM client."""
        if self._client is None:
            from llm_utils import get_rag_llm_client
            self._client = get_rag_llm_client()
        return self._client

    def should_decompose(self, query: str) -> bool:
        """
        Heuristic check if query likely needs decomposition.

        Args:
            query: User's search query

        Returns:
            True if decomposition is recommended
        """
        if not query or len(query) < 20:
            return False

        # Indicators of complex queries
        complexity_indicators = [
            r'\b(and|or)\b.*\b(and|or)\b',  # Multiple conjunctions
            r'\b(compare|contrast|difference|versus|vs\.?)\b',  # Comparison
            r'\b(relationship|connection|interaction)\s+between\b',  # Relationships
            r'\b(analyze|evaluate|assess)\b.*\b(implications?|consequences?|effects?)\b',  # Analysis
            r'\?.*\?',  # Multiple questions
            r'\b(first|second|third|finally|also|additionally)\b',  # Enumeration
        ]

        for pattern in complexity_indicators:
            if re.search(pattern, query, re.IGNORECASE):
                return True

        # Long queries with multiple clauses
        if len(query.split()) > 20:
            return True

        return False

    def decompose(self, query: str) -> List[str]:
        """
        Decompose a complex query into sub-queries.

        Args:
            query: User's search query

        Returns:
            List of sub-queries (may be single-element if not decomposed)
        """
        import time
        start_time = time.time()

        self.stats["queries_processed"] += 1

        if not self.enabled:
            return [query]

        # Quick heuristic check
        if not self.should_decompose(query):
            return [query]

        prompt = DECOMPOSE_USER_PROMPT_TEMPLATE.format(query=query)

        try:
            response = self.client.complete(
                prompt=prompt,
                system_prompt=DECOMPOSE_SYSTEM_PROMPT,
                max_tokens=300,
                temperature=0.2  # Low temperature for consistent parsing
            )

            # Parse JSON response
            subqueries = self._parse_response(response, query)

            elapsed_ms = int((time.time() - start_time) * 1000)
            self.stats["total_time_ms"] += elapsed_ms

            if len(subqueries) > 1:
                self.stats["decompositions"] += 1
                self.stats["total_subqueries"] += len(subqueries)
                print(f"[QueryDecomposer] Decomposed into {len(subqueries)} sub-queries with {self.client.model} ({elapsed_ms}ms)")

            return subqueries[:self.max_subqueries]

        except Exception as e:
            print(f"[QueryDecomposer] Error: {e}")
            self.stats["errors"] += 1
            return [query]

    def _parse_response(self, response: str, original_query: str) -> List[str]:
        """Parse LLM response into list of sub-queries."""
        try:
            # Try to extract JSON array from response
            # Handle cases where response has extra text
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                subqueries = json.loads(json_match.group())
                if isinstance(subqueries, list) and all(isinstance(q, str) for q in subqueries):
                    # Filter out empty strings
                    return [q.strip() for q in subqueries if q.strip()]
        except json.JSONDecodeError:
            pass

        # Fallback: try to split by newlines or numbered items
        lines = response.strip().split('\n')
        subqueries = []
        for line in lines:
            # Remove numbering, bullets, etc.
            cleaned = re.sub(r'^[\d\.\-\*\•]+\s*', '', line.strip())
            cleaned = re.sub(r'^["\']+|["\']+$', '', cleaned)  # Remove quotes
            if cleaned and len(cleaned) > 10:
                subqueries.append(cleaned)

        if subqueries:
            return subqueries

        # Final fallback: return original
        return [original_query]

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        if self._client:
            stats["llm_stats"] = self.client.get_stats()
        return stats


def decompose_query(
    query: str,
    enabled: bool = True,
    max_subqueries: int = 4
) -> Tuple[List[str], Dict[str, Any]]:
    """
    Convenience function to decompose a query.

    Args:
        query: User's search query
        enabled: Whether decomposition is enabled
        max_subqueries: Maximum sub-queries

    Returns:
        Tuple of (sub-queries, stats)
    """
    decomposer = QueryDecomposer(enabled=enabled, max_subqueries=max_subqueries)
    subqueries = decomposer.decompose(query)
    return subqueries, decomposer.get_stats()


def merge_results(
    results_per_query: List[List[Dict[str, Any]]],
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Merge results from multiple sub-queries using Reciprocal Rank Fusion.

    Args:
        results_per_query: List of result lists from each sub-query
        max_results: Maximum results to return

    Returns:
        Merged and deduplicated results
    """
    if not results_per_query:
        return []

    if len(results_per_query) == 1:
        return results_per_query[0][:max_results]

    # RRF constant
    k = 60

    # Calculate RRF scores
    doc_scores = {}
    doc_contents = {}

    for query_results in results_per_query:
        for rank, doc in enumerate(query_results):
            # Use document text as unique identifier
            doc_id = doc.get('document', doc.get('text', ''))[:500]

            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
                doc_contents[doc_id] = doc

            # RRF formula: 1 / (k + rank)
            doc_scores[doc_id] += 1.0 / (k + rank + 1)

    # Sort by RRF score
    sorted_docs = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)

    # Build result list
    merged = []
    for doc_id in sorted_docs[:max_results]:
        doc = doc_contents[doc_id].copy()
        doc['rrf_score'] = doc_scores[doc_id]
        merged.append(doc)

    return merged


# For testing
if __name__ == "__main__":
    print("Testing Query Decomposer...")

    test_queries = [
        # Simple - should not decompose
        "What is GDPR?",
        "Article 101 TFEU",

        # Complex - should decompose
        "Compare the merger control regimes in the EU and US, analyzing their respective notification thresholds and review timelines",
        "What are the penalties for antitrust violations and how do they differ between horizontal and vertical agreements?",
        "Explain the relationship between data protection and competition law, and analyze how the GDPR affects merger assessments",
    ]

    try:
        decomposer = QueryDecomposer(enabled=True)

        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"Should decompose (heuristic): {decomposer.should_decompose(query)}")

            subqueries = decomposer.decompose(query)
            print(f"Sub-queries ({len(subqueries)}):")
            for i, sq in enumerate(subqueries, 1):
                print(f"  {i}. {sq}")

        print(f"\n{'='*60}")
        print(f"Stats: {decomposer.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
