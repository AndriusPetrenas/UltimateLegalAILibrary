"""
Agentic RAG - Multi-step reasoning with iterative search and evaluation.

This module implements an agentic approach to RAG where an LLM agent:
1. Plans the search strategy
2. Executes searches
3. Evaluates results for sufficiency
4. Iteratively refines the search until satisfied or max iterations reached

Key benefits:
- Handles complex queries requiring multiple search angles
- Self-correcting: agent can reformulate queries based on poor results
- Transparent reasoning: tracks search strategy and iteration metadata
"""

import json
import time
from typing import Dict, List, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class AgenticSearchResult:
    """Result from an agentic search session."""
    documents: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    iterations: int
    total_searches: int
    search_history: List[Dict[str, Any]]
    final_evaluation: Dict[str, Any]


class AgenticSearcher:
    """
    Agentic RAG implementation with iterative search and evaluation.

    The agent uses the following loop:
    1. Analyze the query and plan search strategy
    2. Execute search with current query
    3. Evaluate results - are they sufficient?
    4. If not sufficient and iterations remain, refine query and repeat
    5. Merge all results using RRF and return

    This is an ALTERNATIVE to the standard single-pass pipeline.
    When agentic_enabled=True, it replaces the standard retrieval flow.
    """

    # Planning prompt - determines search strategy
    PLAN_PROMPT = """You are a legal research planning assistant. Analyze this legal question and create a search plan.

Question: {query}

Think about:
1. What are the key legal concepts mentioned?
2. Are there multiple aspects to this question that need separate searches?
3. What search terms would best find relevant legal provisions?

Respond with a JSON object:
{{
    "analysis": "Brief analysis of the question (1-2 sentences)",
    "search_queries": ["query1", "query2"],
    "expected_document_types": ["contract", "regulation", "case law", etc.]
}}

Keep search_queries to 1-3 focused queries. Each should target a specific aspect."""

    # Evaluation prompt - determines if results are sufficient
    EVALUATE_PROMPT = """You are evaluating search results for a legal question.

Original Question: {query}

Search Query Used: {search_query}

Results Retrieved (showing first {num_shown} of {num_total}):
{results_preview}

Evaluate these results:
1. Do they contain information relevant to the question?
2. Are there clear gaps in coverage?
3. Would a different search query find better results?

Respond with a JSON object:
{{
    "sufficient": true/false,
    "relevance_score": 0.0-1.0,
    "coverage_assessment": "Brief assessment of what's covered vs missing",
    "next_query": "A better search query if not sufficient, or null if sufficient",
    "reasoning": "Why you made this assessment"
}}"""

    def __init__(
        self,
        llm_client,
        search_fn: Callable,
        max_iterations: int = 3,
        min_relevance_threshold: float = 0.6
    ):
        """
        Initialize the Agentic Searcher.

        Args:
            llm_client: LLM client with .complete() method for planning/evaluation
            search_fn: Function that performs vector search.
                       Signature: search_fn(query, n_results) -> dict with documents/metadatas
            max_iterations: Maximum search iterations (default: 3)
            min_relevance_threshold: Minimum relevance score to consider results sufficient
        """
        self.llm = llm_client
        self.search_fn = search_fn
        self.max_iterations = max_iterations
        self.min_relevance_threshold = min_relevance_threshold

    def search(
        self,
        query: str,
        n_results: int = 8,
        settings: Dict[str, Any] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Perform agentic search with iterative refinement.

        Args:
            query: User's legal question
            n_results: Number of results to return
            settings: Optional retrieval settings

        Returns:
            Tuple of (results_dict, agent_metadata)
            - results_dict: Standard format with documents, metadatas, etc.
            - agent_metadata: Iteration history, search queries used, etc.
        """
        start_time = time.time()
        all_results = []
        search_history = []

        # Step 1: Plan the search strategy
        plan = self._plan_search(query)
        search_queries = plan.get("search_queries", [query])

        # If planning failed, fallback to original query
        if not search_queries:
            search_queries = [query]

        current_query = search_queries[0]
        iteration = 0
        final_evaluation = {"sufficient": False, "relevance_score": 0.0}

        # Step 2-4: Iterative search and evaluation loop
        while iteration < self.max_iterations:
            iteration += 1

            # Execute search
            try:
                results = self.search_fn(current_query, n_results)

                if results and results.get('documents') and results['documents'][0]:
                    # Extract documents with metadata
                    docs_with_meta = []
                    for i, (doc, meta) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0]
                    )):
                        docs_with_meta.append({
                            'document': doc,
                            'metadata': meta,
                            'search_query': current_query,
                            'iteration': iteration,
                            'rank': i
                        })
                    all_results.extend(docs_with_meta)

                    # Record search history
                    search_history.append({
                        'iteration': iteration,
                        'query': current_query,
                        'num_results': len(docs_with_meta),
                        'timestamp': time.time()
                    })

                    # Evaluate results
                    evaluation = self._evaluate_results(
                        query=query,
                        search_query=current_query,
                        results=docs_with_meta
                    )
                    final_evaluation = evaluation

                    # Check if sufficient
                    if evaluation.get("sufficient", False):
                        break

                    if evaluation.get("relevance_score", 0) >= self.min_relevance_threshold:
                        break

                    # Get next query for refinement
                    next_query = evaluation.get("next_query")
                    if next_query and next_query != current_query:
                        current_query = next_query
                    elif len(search_queries) > iteration:
                        # Use next planned query
                        current_query = search_queries[iteration]
                    else:
                        # No more queries to try
                        break
                else:
                    # No results, try next query if available
                    search_history.append({
                        'iteration': iteration,
                        'query': current_query,
                        'num_results': 0,
                        'timestamp': time.time()
                    })

                    if len(search_queries) > iteration:
                        current_query = search_queries[iteration]
                    else:
                        break

            except Exception as e:
                print(f"[AGENTIC] Error in iteration {iteration}: {e}")
                search_history.append({
                    'iteration': iteration,
                    'query': current_query,
                    'error': str(e),
                    'timestamp': time.time()
                })
                break

        # Step 5: Merge results using RRF
        merged_results = self._merge_results(all_results, n_results)

        # Build metadata
        elapsed_time = time.time() - start_time
        agent_metadata = {
            'agentic_enabled': True,
            'iterations': iteration,
            'total_searches': len(search_history),
            'search_history': search_history,
            'initial_plan': plan,
            'final_evaluation': final_evaluation,
            'elapsed_time_seconds': round(elapsed_time, 2),
            'queries_used': list(set(h['query'] for h in search_history))
        }

        # Format results in standard format
        results_dict = {
            'documents': [[r['document'] for r in merged_results]],
            'metadatas': [[r['metadata'] for r in merged_results]],
            'distances': [[r.get('rrf_score', 1.0) for r in merged_results]],
            'ids': [[f"agentic_{i}" for i in range(len(merged_results))]]
        }

        return results_dict, agent_metadata

    def _plan_search(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to plan the search strategy.

        Args:
            query: User's question

        Returns:
            Plan dict with search_queries and analysis
        """
        try:
            prompt = self.PLAN_PROMPT.format(query=query)
            response = self.llm.complete(prompt, max_tokens=500)

            # Parse JSON response
            # Handle potential markdown code blocks
            response_text = response.strip()
            if response_text.startswith("```"):
                # Remove markdown code block
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            plan = json.loads(response_text)
            print(f"[AGENTIC] Search plan: {plan.get('analysis', 'No analysis')}")
            print(f"[AGENTIC] Planned queries: {plan.get('search_queries', [])}")
            return plan

        except json.JSONDecodeError as e:
            print(f"[AGENTIC] Failed to parse plan JSON: {e}")
            return {"search_queries": [query], "analysis": "Planning failed, using original query"}
        except Exception as e:
            print(f"[AGENTIC] Planning error: {e}")
            return {"search_queries": [query], "analysis": f"Planning error: {str(e)}"}

    def _evaluate_results(
        self,
        query: str,
        search_query: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to evaluate search results.

        Args:
            query: Original user question
            search_query: Query used for this search
            results: List of result dicts with document and metadata

        Returns:
            Evaluation dict with sufficient, relevance_score, next_query
        """
        try:
            # Build results preview (first 3 results, truncated)
            preview_parts = []
            for i, r in enumerate(results[:3]):
                doc_preview = r['document'][:500] + "..." if len(r['document']) > 500 else r['document']
                source = r['metadata'].get('source', 'Unknown')
                preview_parts.append(f"Result {i+1} (Source: {source}):\n{doc_preview}\n")

            results_preview = "\n".join(preview_parts)

            prompt = self.EVALUATE_PROMPT.format(
                query=query,
                search_query=search_query,
                results_preview=results_preview,
                num_shown=min(3, len(results)),
                num_total=len(results)
            )

            response = self.llm.complete(prompt, max_tokens=400)

            # Parse JSON response
            response_text = response.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            evaluation = json.loads(response_text)
            print(f"[AGENTIC] Evaluation: sufficient={evaluation.get('sufficient')}, "
                  f"relevance={evaluation.get('relevance_score')}")
            return evaluation

        except json.JSONDecodeError as e:
            print(f"[AGENTIC] Failed to parse evaluation JSON: {e}")
            # Default to sufficient to avoid infinite loops
            return {"sufficient": True, "relevance_score": 0.5, "reasoning": "Evaluation parsing failed"}
        except Exception as e:
            print(f"[AGENTIC] Evaluation error: {e}")
            return {"sufficient": True, "relevance_score": 0.5, "reasoning": f"Evaluation error: {str(e)}"}

    def _merge_results(
        self,
        all_results: List[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Merge results from multiple iterations using Reciprocal Rank Fusion (RRF).

        Args:
            all_results: All results from all iterations
            max_results: Maximum number of results to return

        Returns:
            Merged and deduplicated results sorted by RRF score
        """
        if not all_results:
            return []

        # Group results by document content (for deduplication)
        doc_scores = {}
        k = 60  # RRF constant

        for result in all_results:
            # Use document content as key for deduplication
            doc_key = result['document'][:200]  # First 200 chars as fingerprint

            if doc_key not in doc_scores:
                doc_scores[doc_key] = {
                    'document': result['document'],
                    'metadata': result['metadata'],
                    'rrf_score': 0.0,
                    'iterations_found': [],
                    'queries_found': []
                }

            # Add RRF contribution: 1 / (k + rank)
            rank = result.get('rank', 0)
            doc_scores[doc_key]['rrf_score'] += 1.0 / (k + rank + 1)

            # Track which iterations found this document
            iteration = result.get('iteration', 1)
            if iteration not in doc_scores[doc_key]['iterations_found']:
                doc_scores[doc_key]['iterations_found'].append(iteration)

            query = result.get('search_query', '')
            if query and query not in doc_scores[doc_key]['queries_found']:
                doc_scores[doc_key]['queries_found'].append(query)

        # Sort by RRF score (descending)
        sorted_results = sorted(
            doc_scores.values(),
            key=lambda x: x['rrf_score'],
            reverse=True
        )

        return sorted_results[:max_results]


def agentic_search(
    query: str,
    llm_client,
    search_fn: Callable,
    n_results: int = 8,
    max_iterations: int = 3,
    settings: Dict[str, Any] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Convenience function for agentic search.

    Args:
        query: User's question
        llm_client: LLM client with .complete() method
        search_fn: Search function
        n_results: Number of results
        max_iterations: Max iterations
        settings: Retrieval settings

    Returns:
        Tuple of (results_dict, agent_metadata)
    """
    searcher = AgenticSearcher(
        llm_client=llm_client,
        search_fn=search_fn,
        max_iterations=max_iterations
    )

    return searcher.search(query, n_results, settings)
