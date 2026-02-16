"""
LLM Utilities for RAG Enhancement Features

Provides a shared interface for LLM calls used by:
- SAC (Summary-Augmented Chunking)
- HyDE (Hypothetical Document Embeddings)
- Query Decomposition
- Metadata Extraction

Uses cheap, fast models for cost efficiency.
Default: Mistral Nemo (EU-based, GDPR compliant, fast, no training on API data)
"""

import os
import time
import json
import random
from typing import Optional, Dict, Any, List
from functools import lru_cache
from openai import APIError, APIConnectionError, RateLimitError, APIStatusError


# Cost tracking (approximate costs per 1K tokens)
MODEL_COSTS = {
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "deepseek-chat": {"input": 0.00014, "output": 0.00028},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    # Mistral models (EU-based, GDPR compliant, no training on API data)
    "open-mistral-nemo": {"input": 0.00015, "output": 0.00015},  # Mistral Nemo - fast & cheap
    "mistral-small-latest": {"input": 0.0001, "output": 0.0003},  # Mistral Small
}


class RAGLLMClient:
    """
    Lightweight LLM client for RAG enhancement tasks.
    Uses the cheapest available model for cost efficiency.
    """

    def __init__(self, preferred_model: str = None):
        """
        Initialize the LLM client.

        Args:
            preferred_model: Override default model selection
        """
        self.model = preferred_model or self._select_model()
        self.client = self._create_client()
        self.total_cost = 0.0
        self.call_count = 0

    def _select_model(self) -> str:
        """Select the best available model based on configured API keys."""
        # Priority order: Mistral (EU, fast, no training) > DeepSeek > OpenAI
        if os.getenv("MISTRAL_API_KEY"):
            return "open-mistral-nemo"  # EU-based, GDPR compliant, fast, no training on data
        if os.getenv("DEEPSEEK_API_KEY"):
            return "deepseek-chat"
        if os.getenv("OPENAI_API_KEY"):
            return "gpt-4o-mini"  # Cheapest OpenAI option
        if os.getenv("OPENROUTER_API_KEY"):
            return "openai/gpt-4o-mini"  # Via OpenRouter
        return "gpt-4o-mini"  # Default

    def _create_client(self):
        """Create the appropriate client based on model selection and available API keys."""
        from openai import OpenAI

        model_lower = self.model.lower()

        # Check for Mistral models with Mistral API key
        if "mistral" in model_lower and os.getenv("MISTRAL_API_KEY"):
            return OpenAI(
                api_key=os.getenv("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1"
            )

        # Check for DeepSeek models with DeepSeek API key
        if "deepseek" in model_lower and os.getenv("DEEPSEEK_API_KEY"):
            return OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
            )

        # OpenRouter prefix format (openai/gpt-4o, anthropic/claude-3)
        if self.model.startswith("openai/") or self.model.startswith("anthropic/") or self.model.startswith("meta-llama/"):
            if os.getenv("OPENROUTER_API_KEY"):
                return OpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )

        # OpenAI models (gpt-4o, gpt-4o-mini, o1-*, etc.)
        if any(x in model_lower for x in ["gpt-", "o1-", "o3-"]):
            if os.getenv("OPENAI_API_KEY"):
                return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            # Fallback to OpenRouter for OpenAI models
            if os.getenv("OPENROUTER_API_KEY"):
                # Prefix model name for OpenRouter
                if not self.model.startswith("openai/"):
                    self.model = f"openai/{self.model}"
                return OpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )

        # Claude models
        if "claude" in model_lower:
            if os.getenv("ANTHROPIC_API_KEY"):
                # Use Anthropic directly (requires anthropic SDK)
                # For now, route through OpenRouter which uses OpenAI-compatible API
                pass
            if os.getenv("OPENROUTER_API_KEY"):
                # Prefix model name for OpenRouter
                if not self.model.startswith("anthropic/"):
                    self.model = f"anthropic/{self.model}"
                return OpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )

        # Gemini models - route through OpenRouter
        if "gemini" in model_lower:
            if os.getenv("OPENROUTER_API_KEY"):
                if not self.model.startswith("google/"):
                    self.model = f"google/{self.model}"
                return OpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )

        # Llama/Qwen models - route through OpenRouter
        if any(x in model_lower for x in ["llama", "qwen"]):
            if os.getenv("OPENROUTER_API_KEY"):
                return OpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )

        # Default fallback: try OpenRouter if available, else OpenAI
        if os.getenv("OPENROUTER_API_KEY"):
            return OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )

        # Last resort: direct OpenAI
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.3,
        max_retries: int = 5
    ) -> str:
        """
        Generate a completion with automatic retry on transient errors.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            max_retries: Maximum number of retry attempts for transient errors

        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model.replace("openai/", "").replace("anthropic/", ""),
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Track costs
                self.call_count += 1
                if hasattr(response, 'usage') and response.usage:
                    self._track_cost(response.usage.prompt_tokens, response.usage.completion_tokens)

                return response.choices[0].message.content.strip()

            except (RateLimitError, APIConnectionError) as e:
                # Always retry rate limits and connection errors
                last_error = e
                wait_time = self._calculate_backoff(attempt)
                print(f"[LLM_UTILS] {type(e).__name__} on attempt {attempt + 1}/{max_retries}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)

            except APIStatusError as e:
                # Retry on 502, 503, 500 (server errors)
                if e.status_code in (500, 502, 503, 504):
                    last_error = e
                    wait_time = self._calculate_backoff(attempt)
                    print(f"[LLM_UTILS] Server error {e.status_code} on attempt {attempt + 1}/{max_retries}. Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    # Don't retry client errors (4xx except 429)
                    print(f"[LLM_UTILS] Client error {e.status_code}: {e}")
                    raise

            except APIError as e:
                # Generic API error - retry with backoff
                last_error = e
                wait_time = self._calculate_backoff(attempt)
                print(f"[LLM_UTILS] API error on attempt {attempt + 1}/{max_retries}: {e}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)

            except Exception as e:
                # Unknown error - log and raise immediately
                print(f"[LLM_UTILS] Unexpected error in completion: {e}")
                raise

        # All retries exhausted
        print(f"[LLM_UTILS] All {max_retries} retry attempts exhausted. Last error: {last_error}")
        raise last_error if last_error else Exception("Unknown error after retries")

    def _calculate_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """
        Calculate exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-indexed)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds with random jitter
        """
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s, ...
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Add random jitter (±25%) to avoid thundering herd
        jitter = delay * 0.25 * (2 * random.random() - 1)
        return delay + jitter

    def _track_cost(self, input_tokens: int, output_tokens: int):
        """Track approximate cost of API call."""
        model_key = self.model.replace("openai/", "").replace("anthropic/", "")
        costs = MODEL_COSTS.get(model_key, {"input": 0.001, "output": 0.002})

        cost = (input_tokens / 1000) * costs["input"] + (output_tokens / 1000) * costs["output"]
        self.total_cost += cost

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "model": self.model,
            "call_count": self.call_count,
            "total_cost_usd": round(self.total_cost, 6)
        }


# Singleton instance for reuse
_llm_client: Optional[RAGLLMClient] = None


def get_rag_llm_client() -> RAGLLMClient:
    """Get or create the shared LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = RAGLLMClient()
        print(f"[LLM_UTILS] Initialized RAG LLM client with model: {_llm_client.model}")
    return _llm_client


def generate_completion(
    prompt: str,
    system_prompt: str = None,
    max_tokens: int = 500,
    temperature: float = 0.3
) -> str:
    """
    Convenience function for generating completions.

    Args:
        prompt: User prompt
        system_prompt: System prompt (optional)
        max_tokens: Maximum tokens
        temperature: Sampling temperature

    Returns:
        Generated text
    """
    client = get_rag_llm_client()
    return client.complete(prompt, system_prompt, max_tokens, temperature)


# For testing
if __name__ == "__main__":
    print("Testing RAG LLM Client...")

    try:
        client = get_rag_llm_client()
        print(f"Using model: {client.model}")

        response = client.complete(
            "What is Article 101 TFEU about? Answer in one sentence.",
            system_prompt="You are a legal expert. Be concise."
        )
        print(f"Response: {response}")
        print(f"Stats: {client.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
