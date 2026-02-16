"""
HyDE (Hypothetical Document Embeddings) Module for QueryLex

Generates hypothetical document passages that would answer the query,
then uses those for retrieval instead of the raw query.

Cost: ~$0.001-0.005 per query (depending on model)
Impact: +10-30% retrieval accuracy for conceptual/complex queries
"""

from typing import List, Dict, Any, Optional, Tuple


# HyDE Prompts
HYDE_SYSTEM_PROMPT = """You are a legal document expert. Given a legal question, write a hypothetical passage that would directly answer that question.

The passage should:
1. Be written as if it's from an actual legal document (contract, regulation, case law, etc.)
2. Use appropriate legal terminology and style
3. Be factual and authoritative in tone
4. Be 2-4 sentences long
5. Directly address the question asked

Do NOT include phrases like "According to..." or "The answer is..." - write as if you ARE the source document."""

HYDE_USER_PROMPT_TEMPLATE = """Question: {query}

Write a hypothetical legal document passage that would answer this question:"""


class HyDEGenerator:
    """
    Hypothetical Document Embeddings generator.

    Generates hypothetical document passages for improved retrieval.
    """

    def __init__(self, enabled: bool = True, num_hypothetical: int = 1):
        """
        Initialize HyDE generator.

        Args:
            enabled: Whether HyDE is enabled
            num_hypothetical: Number of hypothetical documents to generate
        """
        self.enabled = enabled
        self.num_hypothetical = num_hypothetical
        self._client = None
        self.stats = {
            "queries_processed": 0,
            "hypotheticals_generated": 0,
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

    def generate_hypothetical(self, query: str) -> str:
        """
        Generate a hypothetical document passage for a query.

        Args:
            query: User's search query

        Returns:
            Hypothetical document passage
        """
        if not self.enabled:
            return query

        if not query or len(query.strip()) < 10:
            return query

        prompt = HYDE_USER_PROMPT_TEMPLATE.format(query=query)

        try:
            hypothetical = self.client.complete(
                prompt=prompt,
                system_prompt=HYDE_SYSTEM_PROMPT,
                max_tokens=200,
                temperature=0.5  # Some creativity for diverse hypotheticals
            )

            self.stats["hypotheticals_generated"] += 1
            return hypothetical.strip()

        except Exception as e:
            print(f"[HyDE] Error generating hypothetical: {e}")
            self.stats["errors"] += 1
            return query  # Fall back to original query

    def expand_query(self, query: str) -> Tuple[str, List[str]]:
        """
        Expand a query with hypothetical documents.

        Args:
            query: Original user query

        Returns:
            Tuple of (primary_search_text, list_of_hypotheticals)
        """
        import time
        start_time = time.time()

        self.stats["queries_processed"] += 1

        if not self.enabled:
            return query, []

        hypotheticals = []
        for _ in range(self.num_hypothetical):
            hyp = self.generate_hypothetical(query)
            if hyp and hyp != query:
                hypotheticals.append(hyp)

        elapsed_ms = int((time.time() - start_time) * 1000)
        self.stats["total_time_ms"] += elapsed_ms

        if hypotheticals:
            # Use the hypothetical for search (better semantic match)
            # but keep original query for context
            primary = hypotheticals[0]
            print(f"[HyDE] Generated hypothetical with {self.client.model} ({elapsed_ms}ms): {primary[:100]}...")
            return primary, hypotheticals

        return query, []

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        if self._client:
            stats["llm_stats"] = self.client.get_stats()
        return stats


def apply_hyde(
    query: str,
    enabled: bool = True,
    num_hypothetical: int = 1
) -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Convenience function to apply HyDE to a query.

    Args:
        query: User's search query
        enabled: Whether HyDE is enabled
        num_hypothetical: Number of hypotheticals to generate

    Returns:
        Tuple of (search_text, hypotheticals, stats)
    """
    generator = HyDEGenerator(enabled=enabled, num_hypothetical=num_hypothetical)
    search_text, hypotheticals = generator.expand_query(query)
    return search_text, hypotheticals, generator.get_stats()


# For testing
if __name__ == "__main__":
    print("Testing HyDE Generator...")

    test_queries = [
        "What are the penalties for antitrust violations in the EU?",
        "How does GDPR define personal data?",
        "When can a contract be terminated for breach?",
    ]

    try:
        generator = HyDEGenerator(enabled=True)

        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")

            search_text, hypotheticals = generator.expand_query(query)

            print(f"\nHypothetical document:")
            print(f"  {search_text}")

        print(f"\n{'='*60}")
        print(f"Stats: {generator.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
