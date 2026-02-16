"""
QueryLex RAG Pipeline - Complete Example

This script demonstrates the full pipeline end-to-end:
  1. Load environment variables
  2. Initialize embedding service
  3. Create a collection in Supabase
  4. Chunk and embed sample text
  5. Store in Supabase
  6. Query with semantic search
  7. Rerank results with cross-encoder
  8. (Optional) Use HyDE for better retrieval

Prerequisites:
  - pip install -r requirements.txt
  - Create a .env file with your API keys (see README.md)
  - Run supabase_setup.sql in your Supabase SQL Editor

Usage:
  python example.py
"""

import os
import sys

# Step 1: Load environment variables from .env file
# -------------------------------------------------
# The .env file should contain your API keys and Supabase credentials.
# See README.md for the full list of environment variables.
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded .env file")
except ImportError:
    print("[WARN] python-dotenv not installed. Using system environment variables.")
    print("       Install with: pip install python-dotenv")


def check_env():
    """Verify required environment variables are set."""
    missing = []

    if not os.getenv("OPENAI_API_KEY") and not os.getenv("MISTRAL_API_KEY"):
        missing.append("OPENAI_API_KEY or MISTRAL_API_KEY (need at least one LLM provider)")

    if not os.getenv("SUPABASE_URL"):
        missing.append("SUPABASE_URL")

    if not os.getenv("SUPABASE_ANON_KEY") and not os.getenv("SUPABASE_SERVICE_KEY"):
        missing.append("SUPABASE_ANON_KEY or SUPABASE_SERVICE_KEY")

    if missing:
        print("\n[ERROR] Missing required environment variables:")
        for m in missing:
            print(f"  - {m}")
        print("\nCreate a .env file with these variables. See README.md for details.")
        sys.exit(1)

    print("[OK] Environment variables configured")


# Step 2: Initialize the embedding service
# -----------------------------------------
def init_embedding_service():
    """Create an embedding service instance."""
    from embedding_service import EmbeddingService

    # Default: OpenAI text-embedding-3-small (1536 dimensions, cheapest)
    # Change to "cohere"/"isaacus"/"voyage"/"openrouter" for other providers
    service = EmbeddingService(provider="openai", model="text-embedding-3-small")
    print(f"[OK] Embedding service initialized (OpenAI text-embedding-3-small, 1536D)")
    return service


# Step 3: Create a collection (dataset) in Supabase
# ---------------------------------------------------
def create_collection(collection_name: str):
    """Create a new collection in Supabase to store documents."""
    from supabase_client import SupabaseVectorClient

    # use_service_key=True bypasses Row Level Security (needed for inserts)
    client = SupabaseVectorClient(use_service_key=True)

    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_model="text-embedding-3-small"  # stored in metadata
        )
        print(f"[OK] Collection '{collection_name}' ready")
        return client
    except Exception as e:
        print(f"[ERROR] Failed to create collection: {e}")
        sys.exit(1)


# Step 4: Chunk text into smaller pieces
# ----------------------------------------
def chunk_text(text: str, chunk_size_tokens: int = 256, chunk_overlap_tokens: int = 50):
    """Split text into token-sized chunks with overlap."""
    from document_processor import count_tokens

    # Simple chunking by sentences (production code uses structure-aware chunking)
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_tokens = count_tokens(sentence)

        if current_tokens + sentence_tokens > chunk_size_tokens and current_chunk:
            # Save current chunk
            chunks.append('. '.join(current_chunk) + '.')
            # Keep last sentence for overlap
            current_chunk = [current_chunk[-1]] if chunk_overlap_tokens > 0 else []
            current_tokens = count_tokens('. '.join(current_chunk)) if current_chunk else 0

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return chunks


# Step 5: Embed and store chunks
# --------------------------------
def embed_and_store(client, collection_name: str, embedding_service, chunks: list, source_name: str):
    """Generate embeddings for chunks and store them in Supabase."""
    print(f"\n--- Embedding {len(chunks)} chunks ---")

    # Generate embeddings for all chunks
    embeddings = embedding_service.embed_documents(chunks)
    print(f"[OK] Generated {len(embeddings)} embeddings ({len(embeddings[0])}D each)")

    # Prepare metadata for each chunk
    metadatas = [
        {"source": source_name, "chunk_index": i, "total_chunks": len(chunks)}
        for i in range(len(chunks))
    ]

    # Store in Supabase
    success = client.add_documents(
        collection_name=collection_name,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        embedding_model="text-embedding-3-small"
    )

    if success:
        print(f"[OK] Stored {len(chunks)} chunks in collection '{collection_name}'")
    else:
        print(f"[ERROR] Failed to store chunks")

    return success


# Step 6: Query the collection
# ------------------------------
def search(client, collection_name: str, embedding_service, query: str, n_results: int = 5):
    """Search for similar documents using semantic search."""
    print(f"\n--- Searching: '{query}' ---")

    # Generate query embedding
    query_embedding = embedding_service.embed_query(query)

    # Search Supabase
    results = client.query_collection(
        collection_name=collection_name,
        query_embedding=query_embedding,
        n_results=n_results,
        embedding_model="text-embedding-3-small"
    )

    documents = results["documents"][0]
    similarities = results["distances"][0]
    metadatas = results["metadatas"][0]

    print(f"[OK] Found {len(documents)} results\n")

    for i, (doc, sim, meta) in enumerate(zip(documents, similarities, metadatas)):
        print(f"  Result {i+1} (similarity: {sim:.4f}):")
        print(f"    Source: {meta.get('source', 'unknown')}, chunk {meta.get('chunk_index', '?')}")
        print(f"    Text: {doc[:150]}...")
        print()

    return results


# Step 7: Rerank results with cross-encoder
# --------------------------------------------
def rerank(query: str, results: dict, top_k: int = 3):
    """Rerank search results using cross-encoder for better accuracy."""
    from reranker import rerank_results

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Format for reranker
    docs_for_rerank = [
        {
            "document": doc,
            "metadata": meta,
            "distance": dist,
            "id": f"doc_{i}"
        }
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances))
    ]

    print(f"--- Reranking {len(docs_for_rerank)} results ---")
    reranked, stats = rerank_results(
        query=query,
        results=docs_for_rerank,
        top_k=top_k,
        enabled=True
    )

    print(f"[OK] Reranked to top {len(reranked)} results")
    print(f"    Model: {stats.get('model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')}")
    print(f"    Time: {stats.get('rerank_time_ms', 0):.0f}ms\n")

    for i, doc in enumerate(reranked):
        print(f"  Reranked {i+1} (score: {doc.get('rerank_score', 0):.4f}):")
        print(f"    Text: {doc['document'][:150]}...")
        print()

    return reranked


# ============================================================
# Main: Run the full pipeline
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("QueryLex RAG Pipeline - Example")
    print("=" * 60)

    # Check environment
    check_env()

    # Sample legal text (replace with your own documents)
    SAMPLE_TEXT = """
    Article 101 of the Treaty on the Functioning of the European Union (TFEU)
    prohibits agreements between undertakings, decisions by associations of
    undertakings and concerted practices which may affect trade between Member
    States and which have as their object or effect the prevention, restriction
    or distortion of competition within the internal market.

    Such agreements are automatically void under Article 101(2). However,
    Article 101(3) provides an exemption where the agreement contributes to
    improving production or distribution, or to promoting technical or economic
    progress, while allowing consumers a fair share of the resulting benefit.

    The European Commission has exclusive competence to grant individual
    exemptions under Article 101(3). National competition authorities and
    national courts can apply Articles 101(1) and 101(2) directly.

    Fines for infringement of Article 101 can reach up to 10% of the
    undertaking's total worldwide annual turnover. The Commission has imposed
    significant fines in cartel cases, including the truck cartel case where
    fines totaled over 3.8 billion euros.

    Article 102 TFEU prohibits the abuse of a dominant position within the
    internal market. A dominant position is not itself prohibited, but its
    abuse is. Examples of abuse include imposing unfair purchase or selling
    prices, limiting production or markets, applying dissimilar conditions
    to equivalent transactions, and making contracts subject to supplementary
    obligations which have no connection with the subject of the contracts.

    The General Data Protection Regulation (GDPR), formally known as Regulation
    (EU) 2016/679, is a regulation on data protection and privacy in the EU.
    It addresses the transfer of personal data outside the EU and EEA areas.
    The GDPR's primary aim is to give individuals control over their personal data.

    Under Article 6 of the GDPR, processing of personal data is lawful only if
    at least one of six legal bases applies: consent, contract performance,
    legal obligation, vital interests, public task, or legitimate interests.

    Data controllers must implement appropriate technical and organizational
    measures to ensure compliance. Violations can result in fines of up to
    20 million euros or 4% of annual global turnover, whichever is higher.
    """

    COLLECTION_NAME = "example-legal-docs"

    # Initialize services
    embedding_service = init_embedding_service()
    client = create_collection(COLLECTION_NAME)

    # Chunk the sample text
    chunks = chunk_text(SAMPLE_TEXT)
    print(f"[OK] Split text into {len(chunks)} chunks")

    # Embed and store
    embed_and_store(client, COLLECTION_NAME, embedding_service, chunks, "eu-competition-law.txt")

    # Search
    query = "What are the fines for GDPR violations?"
    results = search(client, COLLECTION_NAME, embedding_service, query, n_results=5)

    # Rerank
    reranked = rerank(query, results, top_k=3)

    # Cleanup hint
    print("=" * 60)
    print("Done! To delete the example collection, run:")
    print(f"  client.delete_collection('{COLLECTION_NAME}')")
    print("=" * 60)
