"""
SAC (Summary-Augmented Chunking) Module for QueryLex

Generates contextual summaries for document chunks using LLM.
These summaries are prepended to chunks to preserve document context
that would otherwise be lost during chunking.

Cost: ~$0.001-0.01 per chunk (depending on chunk size and model)
Impact: +10-20% retrieval accuracy for context-dependent queries
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


# SAC Prompts
SAC_SYSTEM_PROMPT = """You are a legal document analyst. Your task is to generate a brief contextual summary for a document chunk.

The summary should:
1. Identify the document type (contract, regulation, case, memo, etc.)
2. Capture the main topic/subject matter
3. Note any key legal concepts, parties, or provisions mentioned
4. Be concise (2-3 sentences max)

This summary will be prepended to the chunk to help with search retrieval."""

SAC_USER_PROMPT_TEMPLATE = """Generate a brief contextual summary for this legal document chunk:

Document Source: {source}
Chunk Position: {position} of {total_chunks}

--- CHUNK CONTENT ---
{content}
--- END CHUNK ---

Provide a 2-3 sentence summary that captures the context and main points of this chunk."""


class SACGenerator:
    """
    Summary-Augmented Chunking generator.

    Generates LLM summaries for document chunks to preserve context.
    """

    def __init__(self, enabled: bool = True, batch_size: int = 5):
        """
        Initialize SAC generator.

        Args:
            enabled: Whether SAC is enabled
            batch_size: Number of chunks to process in parallel
        """
        self.enabled = enabled
        self.batch_size = batch_size
        self._client = None
        self.stats = {
            "chunks_processed": 0,
            "summaries_generated": 0,
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

    def generate_summary(
        self,
        chunk_text: str,
        source: str = "Unknown",
        position: int = 1,
        total_chunks: int = 1
    ) -> str:
        """
        Generate a contextual summary for a single chunk.

        Args:
            chunk_text: The chunk content
            source: Document source/filename
            position: Chunk position in document
            total_chunks: Total chunks in document

        Returns:
            Generated summary
        """
        if not self.enabled:
            return ""

        if not chunk_text or len(chunk_text.strip()) < 50:
            return ""

        prompt = SAC_USER_PROMPT_TEMPLATE.format(
            source=source,
            position=position,
            total_chunks=total_chunks,
            content=chunk_text[:2000]  # Limit input size
        )

        try:
            summary = self.client.complete(
                prompt=prompt,
                system_prompt=SAC_SYSTEM_PROMPT,
                max_tokens=150,
                temperature=0.2
            )
            return summary.strip()
        except Exception as e:
            print(f"[SAC] Error generating summary: {e}")
            self.stats["errors"] += 1
            return ""

    def enhance_chunk(
        self,
        chunk_text: str,
        source: str = "Unknown",
        position: int = 1,
        total_chunks: int = 1
    ) -> Tuple[str, str]:
        """
        Enhance a chunk with a prepended summary.

        Args:
            chunk_text: Original chunk text
            source: Document source
            position: Chunk position
            total_chunks: Total chunks

        Returns:
            Tuple of (enhanced_text, summary)
        """
        summary = self.generate_summary(chunk_text, source, position, total_chunks)

        if summary:
            enhanced = f"[CONTEXT: {summary}]\n\n{chunk_text}"
            self.stats["summaries_generated"] += 1
        else:
            enhanced = chunk_text

        self.stats["chunks_processed"] += 1
        return enhanced, summary

    def enhance_chunks_batch(
        self,
        chunks: List[Dict[str, Any]],
        source: str = "Unknown",
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Enhance multiple chunks with summaries.

        Args:
            chunks: List of chunk dicts with 'text' and 'metadata' keys
            source: Document source
            progress_callback: Optional callback(processed, total) for progress

        Returns:
            Enhanced chunks with summaries added
        """
        if not self.enabled:
            return chunks

        start_time = time.time()
        total = len(chunks)
        enhanced_chunks = []

        print(f"[SAC] Processing {total} chunks from '{source}' with {self.client.model}...")

        for i, chunk in enumerate(chunks):
            text = chunk.get('text', chunk.get('document', ''))
            metadata = chunk.get('metadata', {})

            enhanced_text, summary = self.enhance_chunk(
                chunk_text=text,
                source=source,
                position=i + 1,
                total_chunks=total
            )

            # Update chunk with enhanced text and summary
            enhanced_chunk = chunk.copy()
            enhanced_chunk['text'] = enhanced_text
            enhanced_chunk['document'] = enhanced_text  # For compatibility
            enhanced_chunk['metadata'] = {
                **metadata,
                'sac_summary': summary,
                'sac_enhanced': bool(summary)
            }
            enhanced_chunks.append(enhanced_chunk)

            if progress_callback:
                progress_callback(i + 1, total)

            # Log progress every 10 chunks
            if (i + 1) % 10 == 0:
                print(f"[SAC] Processed {i + 1}/{total} chunks...")

        elapsed_ms = int((time.time() - start_time) * 1000)
        self.stats["total_time_ms"] += elapsed_ms

        print(f"[SAC] Completed {total} chunks in {elapsed_ms}ms "
              f"({self.stats['summaries_generated']} summaries, {self.stats['errors']} errors)")

        return enhanced_chunks

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        if self._client:
            stats["llm_stats"] = self.client.get_stats()
        return stats


def apply_sac_to_chunks(
    chunks: List[Dict[str, Any]],
    source: str = "Unknown",
    enabled: bool = True,
    progress_callback=None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convenience function to apply SAC to a list of chunks.

    Args:
        chunks: List of chunks to enhance
        source: Document source name
        enabled: Whether SAC is enabled
        progress_callback: Optional progress callback

    Returns:
        Tuple of (enhanced_chunks, stats)
    """
    generator = SACGenerator(enabled=enabled)
    enhanced = generator.enhance_chunks_batch(chunks, source, progress_callback)
    return enhanced, generator.get_stats()


# For testing
if __name__ == "__main__":
    print("Testing SAC Generator...")

    test_chunks = [
        {
            "text": """Article 101 TFEU prohibits agreements between undertakings, decisions by
            associations of undertakings and concerted practices which may affect trade between
            Member States and which have as their object or effect the prevention, restriction
            or distortion of competition within the internal market.""",
            "metadata": {"source": "test.pdf", "page": 1}
        },
        {
            "text": """The European Commission has exclusive competence to grant exemptions under
            Article 101(3) TFEU. Such exemptions may be granted where the agreement contributes
            to improving production or distribution, or to promoting technical or economic progress.""",
            "metadata": {"source": "test.pdf", "page": 2}
        }
    ]

    try:
        enhanced, stats = apply_sac_to_chunks(test_chunks, source="test.pdf", enabled=True)

        print(f"\nStats: {stats}")
        print("\nEnhanced chunks:")
        for i, chunk in enumerate(enhanced):
            print(f"\n--- Chunk {i+1} ---")
            print(f"SAC Summary: {chunk['metadata'].get('sac_summary', 'N/A')}")
            print(f"Text preview: {chunk['text'][:200]}...")

    except Exception as e:
        print(f"Error: {e}")
