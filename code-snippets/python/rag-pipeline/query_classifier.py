"""
Adaptive RAG Query Classifier for QueryLex

Implements heuristic-based query classification to route queries
to appropriate retrieval strategies without requiring an LLM.

Query Types:
- FACTUAL: Simple factoid questions (who, what, when, where)
- KEYWORD: Specific term or definition lookups
- COMPLEX: Multi-part or analytical questions
- CONCEPTUAL: Abstract or explanatory questions
"""

import re
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Types of queries for adaptive retrieval."""
    FACTUAL = "factual"      # Simple factoid questions
    KEYWORD = "keyword"      # Specific term lookups
    COMPLEX = "complex"      # Multi-part analytical questions
    CONCEPTUAL = "conceptual"  # Abstract/explanatory questions


@dataclass
class QueryClassification:
    """Result of query classification."""
    query_type: QueryType
    confidence: float
    reasoning: str

    # Retrieval parameters
    n_results: int
    use_hybrid_search: bool
    use_reranking: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            'query_type': self.query_type.value,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'n_results': self.n_results,
            'use_hybrid_search': self.use_hybrid_search,
            'use_reranking': self.use_reranking
        }


class AdaptiveQueryClassifier:
    """
    Heuristic-based query classifier for adaptive RAG.

    Routes queries to appropriate retrieval strategies based on
    linguistic patterns without requiring an LLM call.
    """

    # Factual query patterns (who, what, when, where, which)
    FACTUAL_PATTERNS = [
        r'^(who|what|when|where|which)\s+',
        r'\b(is|was|are|were)\s+(the|a|an)\b',
        r'^(how many|how much)\b',
        r'\b(name|date|year|amount|number)\s+of\b',
    ]

    # Keyword/definition patterns
    KEYWORD_PATTERNS = [
        r'^(define|definition|meaning|what is)\b',
        r'\b(means?|refer(s|ring)?\s+to)\b',
        r'^"[^"]+"$',  # Quoted search
        r'^\w+(\s+\w+){0,2}$',  # 1-3 word queries
    ]

    # Complex/analytical patterns
    COMPLEX_PATTERNS = [
        r'\b(compare|contrast|analyze|evaluate|assess)\b',
        r'\b(and|or|but|however|whereas)\b.*\b(and|or|but|however|whereas)\b',
        r'\b(implications?|consequences?|effects?|impacts?)\b',
        r'\b(should|must|shall|may)\b.*\b(if|when|unless|provided)\b',
        r'\?.*\?',  # Multiple questions
    ]

    # Conceptual/explanatory patterns
    CONCEPTUAL_PATTERNS = [
        r'^(how|why|explain|describe)\b',
        r'\b(concept|principle|theory|doctrine)\b',
        r'\b(relationship|connection|distinction)\s+between\b',
        r'\b(generally|typically|usually|overall)\b',
    ]

    # Legal-specific patterns
    LEGAL_PATTERNS = [
        r'\b(article|section|paragraph|clause)\s+\d+',
        r'\b(regulation|directive|statute|act)\b',
        r'\b(case|ruling|judgment|decision)\b',
        r'\b(penalty|fine|sanction|liability)\b',
    ]

    def __init__(self):
        """Initialize the classifier with compiled patterns."""
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.factual_re = [re.compile(p, re.IGNORECASE) for p in self.FACTUAL_PATTERNS]
        self.keyword_re = [re.compile(p, re.IGNORECASE) for p in self.KEYWORD_PATTERNS]
        self.complex_re = [re.compile(p, re.IGNORECASE) for p in self.COMPLEX_PATTERNS]
        self.conceptual_re = [re.compile(p, re.IGNORECASE) for p in self.CONCEPTUAL_PATTERNS]
        self.legal_re = [re.compile(p, re.IGNORECASE) for p in self.LEGAL_PATTERNS]

    def classify(self, query: str) -> QueryClassification:
        """
        Classify a query and determine retrieval parameters.

        Args:
            query: User's search query

        Returns:
            QueryClassification with type and retrieval parameters
        """
        if not query or not query.strip():
            return self._default_classification()

        query = query.strip()

        # Calculate scores for each type
        scores = {
            QueryType.FACTUAL: self._score_factual(query),
            QueryType.KEYWORD: self._score_keyword(query),
            QueryType.COMPLEX: self._score_complex(query),
            QueryType.CONCEPTUAL: self._score_conceptual(query),
        }

        # Apply legal domain boost
        legal_boost = self._legal_boost(query)

        # Find best match
        best_type = max(scores.keys(), key=lambda k: scores[k])
        best_score = scores[best_type]

        # Calculate confidence
        total_score = sum(scores.values()) or 1
        confidence = min(0.95, best_score / total_score + 0.1)

        # Build reasoning
        reasoning = f"Matched {best_type.value} patterns"
        if legal_boost > 0:
            reasoning += " (legal domain detected)"

        # Get retrieval parameters based on type
        params = self._get_retrieval_params(best_type, query, legal_boost)

        return QueryClassification(
            query_type=best_type,
            confidence=confidence,
            reasoning=reasoning,
            **params
        )

    def _score_factual(self, query: str) -> float:
        """Score query for factual type."""
        score = 0
        for pattern in self.factual_re:
            if pattern.search(query):
                score += 1

        # Short queries with question words are likely factual
        if len(query.split()) <= 6:
            score += 0.5

        return score

    def _score_keyword(self, query: str) -> float:
        """Score query for keyword type."""
        score = 0
        for pattern in self.keyword_re:
            if pattern.search(query):
                score += 1

        # Very short queries are likely keyword searches
        words = query.split()
        if len(words) <= 3:
            score += 1.5
        if len(words) == 1:
            score += 1

        return score

    def _score_complex(self, query: str) -> float:
        """Score query for complex type."""
        score = 0
        for pattern in self.complex_re:
            if pattern.search(query):
                score += 1

        # Longer queries with conjunctions are likely complex
        words = query.split()
        if len(words) > 15:
            score += 1
        if len(words) > 25:
            score += 1

        return score

    def _score_conceptual(self, query: str) -> float:
        """Score query for conceptual type."""
        score = 0
        for pattern in self.conceptual_re:
            if pattern.search(query):
                score += 1

        # Medium-length "how" or "why" queries
        words = query.split()
        if 5 <= len(words) <= 15:
            if query.lower().startswith(('how', 'why')):
                score += 0.5

        return score

    def _legal_boost(self, query: str) -> float:
        """Calculate legal domain boost."""
        boost = 0
        for pattern in self.legal_re:
            if pattern.search(query):
                boost += 0.3
        return min(boost, 1.0)

    def _get_retrieval_params(
        self,
        query_type: QueryType,
        query: str,
        legal_boost: float
    ) -> Dict[str, Any]:
        """Get retrieval parameters based on query type."""

        # Base parameters per type
        params = {
            QueryType.FACTUAL: {
                'n_results': 5,
                'use_hybrid_search': True,
                'use_reranking': True,
            },
            QueryType.KEYWORD: {
                'n_results': 3,  # Fewer results for specific lookups
                'use_hybrid_search': True,  # Keywords benefit from hybrid
                'use_reranking': False,  # Less need for reranking
            },
            QueryType.COMPLEX: {
                'n_results': 10,  # More context needed
                'use_hybrid_search': True,
                'use_reranking': True,
            },
            QueryType.CONCEPTUAL: {
                'n_results': 8,
                'use_hybrid_search': True,
                'use_reranking': True,
            },
        }

        base_params = params.get(query_type, params[QueryType.FACTUAL])

        # Legal domain adjustments
        if legal_boost > 0.5:
            base_params['n_results'] = min(base_params['n_results'] + 2, 12)
            base_params['use_reranking'] = True

        return base_params

    def _default_classification(self) -> QueryClassification:
        """Return default classification for empty queries."""
        return QueryClassification(
            query_type=QueryType.FACTUAL,
            confidence=0.5,
            reasoning="Default classification (empty query)",
            n_results=5,
            use_hybrid_search=True,
            use_reranking=True,
        )


def classify_query(query: str) -> Tuple[QueryType, Dict[str, Any]]:
    """
    Convenience function to classify a query.

    Args:
        query: User's search query

    Returns:
        Tuple of (QueryType, retrieval_params dict)
    """
    classifier = AdaptiveQueryClassifier()
    result = classifier.classify(query)
    return result.query_type, {
        'n_results': result.n_results,
        'use_hybrid_search': result.use_hybrid_search,
        'use_reranking': result.use_reranking,
    }


def get_adaptive_retrieval_params(
    query: str,
    base_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get adaptive retrieval parameters based on query and base settings.

    This respects the model's base settings but can adjust n_results
    based on query complexity.

    Args:
        query: User's search query
        base_settings: Model's retrieval settings

    Returns:
        Merged retrieval parameters
    """
    classifier = AdaptiveQueryClassifier()
    classification = classifier.classify(query)

    # Start with base settings
    params = {
        'use_hybrid_search': base_settings.get('search_mode', 'hybrid') == 'hybrid',
        'use_reranking': base_settings.get('reranking_enabled', True),
        'n_results': classification.n_results,  # Adaptive based on query
    }

    # Log for debugging
    print(f"[ADAPTIVE] Query type: {classification.query_type.value} "
          f"(confidence: {classification.confidence:.2f}) -> n_results={params['n_results']}")

    return params


# For testing
if __name__ == "__main__":
    test_queries = [
        "What is Article 101 TFEU?",
        "GDPR",
        "How does the European Commission enforce antitrust regulations and what are the implications for cross-border mergers?",
        "Explain the concept of force majeure in contract law",
        "penalty for antitrust violations",
        "Compare the merger control regimes in the EU and US, analyzing their respective thresholds and notification requirements",
        "Who was the judge in the Microsoft antitrust case?",
        "Define tortious interference",
    ]

    classifier = AdaptiveQueryClassifier()

    print("Adaptive Query Classifier Test\n" + "=" * 60)

    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"  Type: {result.query_type.value} (confidence: {result.confidence:.2f})")
        print(f"  Params: n={result.n_results}, hybrid={result.use_hybrid_search}, rerank={result.use_reranking}")
        print(f"  Reasoning: {result.reasoning}")
