"""
Supabase Vector Store Client for RAG Pipeline

Provides vector storage and similarity search using Supabase (PostgreSQL + pgvector).
Supports multiple embedding dimensions (1536, 1024, 1792) with dedicated columns
and RPC functions for each.

Requirements:
    pip install supabase httpx numpy

Environment variables:
    SUPABASE_URL          - Your Supabase project URL
    SUPABASE_ANON_KEY     - Supabase anonymous/public key
    SUPABASE_SERVICE_KEY  - Supabase service role key (for admin operations)
"""

import os
import json
import re
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from supabase import create_client, Client, ClientOptions
import httpx

# Read config from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Embedding model dimension mappings
EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "embed-v3": 1024,
    "kanon-2-embedder": 1792,
    "voyage-3-large": 1024,
    "qwen3-embedding-8b": 1024
}

# Column mappings for different embedding dimensions
EMBEDDING_COLUMNS = {
    1536: "embedding_1536",     # OpenAI text-embedding-3-small
    1024: "embedding_1024",     # Cohere, Voyage, Qwen3
    1792: "embedding_1792"      # Kanon 2
}

# RPC function mappings for different embedding dimensions
MATCH_FUNCTIONS = {
    1536: "match_documents_1536",
    1024: "match_documents_1024",
    1792: "match_documents_1792"
}

# Filtered match functions (for legal source filtering)
MATCH_FUNCTIONS_FILTERED = {
    1536: "match_documents_1536_filtered",
    1024: "match_documents_1024_filtered",
    1792: "match_documents_1792_filtered"
}


def _sanitize_content_for_db(text: str) -> str:
    """
    Sanitize text content for PostgreSQL insertion.
    Removes NULL chars and invalid Unicode while preserving international characters.
    """
    if not text or not isinstance(text, str):
        return text or ""

    # Remove NULL characters (PostgreSQL JSONB doesn't support \u0000)
    text = text.replace('\x00', '')

    # Remove control chars except tab, newline, carriage return
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

    # Remove problematic Unicode characters
    text = text.replace('\ufffd', '')  # Replacement character
    text = text.replace('\ufeff', '').replace('\ufffe', '')  # BOMs

    # Remove private use area and surrogate pairs
    text = re.sub(r'[\ue000-\uf8ff]', '', text)
    text = re.sub(r'[\ud800-\udfff]', '', text)

    return text

# Configure longer timeouts for Supabase connections
SUPABASE_TIMEOUT = httpx.Timeout(
    connect=30.0,    # 30 seconds to establish connection
    read=120.0,      # 120 seconds to read response (important for large uploads)
    write=120.0,     # 120 seconds to write request
    pool=30.0        # 30 seconds to acquire connection from pool
)


class SupabaseVectorClient:
    """Client for Supabase vector database operations."""

    def __init__(self, use_service_key: bool = False):
        """Initialize Supabase client.

        Args:
            use_service_key: Whether to use service key for admin operations
        """
        if not SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")

        key = SUPABASE_SERVICE_KEY if use_service_key and SUPABASE_SERVICE_KEY else SUPABASE_ANON_KEY
        if not key:
            raise ValueError("SUPABASE_ANON_KEY or SUPABASE_SERVICE_KEY environment variable is required")

        # Create client with extended timeout configuration
        self.client: Client = create_client(
            SUPABASE_URL,
            key,
            options=ClientOptions(
                postgrest_client_timeout=120,
                storage_client_timeout=120,
            )
        )
        self.use_service_key = use_service_key

    def create_collection(self, name: str, user_id: str = None, retrieval_settings: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Create a new collection (dataset).

        Args:
            name: Collection name
            user_id: UUID of the user creating the collection (optional)
            retrieval_settings: RAG retrieval configuration (optional)
            **kwargs: Additional metadata

        Returns:
            Collection metadata
        """
        collection_data = {
            "name": name,
            "metadata": kwargs
        }

        if user_id:
            collection_data["user_id"] = user_id

        if retrieval_settings is not None:
            collection_data["retrieval_settings"] = retrieval_settings
        else:
            # Default retrieval settings (free features ON, LLM features OFF)
            collection_data["retrieval_settings"] = {
                "search_mode": "hybrid",
                "reranking_enabled": True,
                "legal_tokenization": True,
                "sac_enabled": False,
                "hyde_enabled": False,
                "query_decomposition_enabled": False,
                "agentic_enabled": False,
                "colbert_enabled": False,
                "metadata_extraction": {
                    "document_type": True,
                    "date": True,
                    "jurisdiction": False,
                    "parties": False,
                    "practice_area": False
                }
            }

        result = self.client.table("collections").insert(collection_data).execute()

        if result.data:
            return {"name": name, "id": result.data[0]["id"]}
        else:
            raise Exception(f"Failed to create collection: {result}")

    def _get_collection_data(self, name: str) -> Dict[str, Any]:
        """Get raw collection data by name."""
        result = self.client.table("collections").select("*").eq("name", name).execute()

        if not result.data:
            raise Exception(f"Collection '{name}' not found")

        return result.data[0]

    def get_collection(self, name: str):
        """Get collection by name. Returns SupabaseCollection object."""
        collection_data = self._get_collection_data(name)
        return SupabaseCollection(self, name, collection_data)

    def get_or_create_collection(self, name: str, user_id: str = None, **kwargs):
        """Get existing collection or create new one."""
        try:
            return self.get_collection(name)
        except Exception:
            collection_data = self.create_collection(name, user_id=user_id, **kwargs)
            return SupabaseCollection(self, name, collection_data)

    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections."""
        result = self.client.table("collections").select("*").execute()
        return result.data or []

    def delete_collection(self, name: str) -> bool:
        """Delete a collection and all its documents."""
        try:
            collection = self._get_collection_data(name)
            collection_id = collection["id"]

            self.client.table("documents").delete().eq("collection_id", collection_id).execute()

            result = self.client.table("collections").delete().eq("name", name).execute()

            if not result.data or len(result.data) == 0:
                print(f"[DELETE] WARNING: No collection deleted for '{name}'")
                return False

            return True
        except Exception as e:
            print(f"[DELETE] Error deleting collection '{name}': {e}")
            return False

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None,
        embedding_model: str = None,
        sentence_embeddings: List[List[List[float]]] = None,
        sentence_texts: List[List[str]] = None
    ) -> bool:
        """Add documents to a collection.

        Uses direct table inserts when using service key (bypasses RLS),
        or secure RPC when using anon key (respects RLS).

        Args:
            collection_name: Name of the collection
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents
            embedding_model: Embedding model name (determines which column to use)
            sentence_embeddings: Optional sentence-level embeddings for ColBERT
            sentence_texts: Optional sentence texts for ColBERT

        Returns:
            True if successful
        """
        try:
            if metadatas is None:
                metadatas = [{}] * len(documents)
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            collection = self._get_collection_data(collection_name)
            collection_id = collection["id"]

            if embedding_model is None:
                collection_metadata = collection.get("metadata", {})
                embedding_model = collection_metadata.get("embedding_model", "text-embedding-3-small")

            dimension = EMBEDDING_DIMENSIONS.get(embedding_model, 1536)
            embedding_column = EMBEDDING_COLUMNS.get(dimension, "embedding")
            print(f"[DOCUMENTS] Using embedding column '{embedding_column}' for model '{embedding_model}' ({dimension}D)")

            # Prepare documents
            doc_data = []
            for i, (doc, embedding, metadata, doc_id) in enumerate(zip(documents, embeddings, metadatas, ids)):
                doc_entry = {
                    "id": doc_id,
                    "content": _sanitize_content_for_db(doc),
                    "metadata": metadata
                }
                doc_entry[embedding_column] = embedding

                if sentence_embeddings and i < len(sentence_embeddings) and sentence_embeddings[i]:
                    doc_entry["sentence_embeddings"] = sentence_embeddings[i]
                if sentence_texts and i < len(sentence_texts) and sentence_texts[i]:
                    doc_entry["sentence_texts"] = sentence_texts[i]

                doc_data.append(doc_entry)

            # Insert in batches
            batch_size = 100
            successful_batches = 0
            total_batches = (len(doc_data) + batch_size - 1) // batch_size

            for i in range(0, len(doc_data), batch_size):
                batch = doc_data[i:i + batch_size]
                batch_num = i // batch_size + 1
                max_retries = 5

                if self.use_service_key:
                    for attempt in range(max_retries):
                        try:
                            rows = []
                            for doc in batch:
                                row = {
                                    "id": doc["id"],
                                    "collection_id": collection_id,
                                    "content": doc["content"],
                                    "metadata": doc["metadata"]
                                }
                                row[embedding_column] = doc.get(embedding_column)
                                if doc.get("sentence_embeddings"):
                                    row["sentence_embeddings"] = doc["sentence_embeddings"]
                                if doc.get("sentence_texts"):
                                    row["sentence_texts"] = doc["sentence_texts"]
                                rows.append(row)

                            result = self.client.table("documents").insert(rows).execute()

                            if result.data:
                                successful_batches += 1
                                print(f"Inserted batch {batch_num}/{total_batches} ({len(rows)} documents)")
                                break
                        except Exception as batch_error:
                            print(f"Error on batch {batch_num}, attempt {attempt + 1}/{max_retries}: {batch_error}")
                            if attempt < max_retries - 1:
                                time.sleep(3 + 2 ** attempt)
                    continue

                # RPC path (anon key with RLS)
                for attempt in range(max_retries):
                    try:
                        result = self.client.rpc(
                            'insert_documents_secure',
                            {
                                'p_collection_name': collection_name,
                                'p_documents': batch
                            }
                        ).execute()

                        if result.data and result.data.get('success'):
                            successful_batches += 1
                            print(f"Inserted batch {batch_num}/{total_batches}")
                            break
                    except Exception as batch_error:
                        print(f"Error on batch {batch_num}, attempt {attempt + 1}/{max_retries}: {batch_error}")
                        if attempt < max_retries - 1:
                            time.sleep(3 + 2 ** attempt)

            print(f"Document insertion completed. {successful_batches}/{total_batches} batches successful.")
            return successful_batches > 0

        except Exception as e:
            print(f"Error adding documents to collection {collection_name}: {e}")
            return False

    def query_collection(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5,
        where: Dict[str, Any] = None,
        embedding_model: str = None
    ) -> Dict[str, List[Any]]:
        """Query a collection for similar documents using pgvector similarity search.

        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filters
            embedding_model: Embedding model name (determines which RPC function to use)

        Returns:
            Dictionary with documents, metadatas, distances, and ids
        """
        try:
            collection = self._get_collection_data(collection_name)
            collection_id = collection["id"]

            if embedding_model is None:
                collection_metadata = collection.get("metadata", {})
                embedding_model = collection_metadata.get("embedding_model", "text-embedding-3-small")

            dimension = EMBEDDING_DIMENSIONS.get(embedding_model, 1536)
            match_function = MATCH_FUNCTIONS.get(dimension, "match_documents")

            rpc_result = self.client.rpc(
                match_function,
                {
                    "collection_id": collection_id,
                    "query_embedding": query_embedding,
                    "match_threshold": 0.0,
                    "match_count": n_results
                }
            ).execute()

            if not rpc_result.data:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

            documents, metadatas, distances, ids = [], [], [], []
            for doc in rpc_result.data:
                documents.append(doc["content"])
                metadatas.append(doc["metadata"] or {})
                distances.append(doc["similarity"])
                ids.append(doc["id"])

            return {
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances],
                "ids": [ids]
            }

        except Exception as e:
            print(f"Error querying collection {collection_name}: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

    def query_collection_filtered(
        self,
        collection_ids: List[str],
        query_embedding: List[float],
        n_results: int = 10,
        embedding_model: str = None,
        filter_conditions: List[Dict] = None
    ) -> Dict[str, List[Any]]:
        """Query across multiple collections with per-key OR metadata filtering.

        Uses filtered RPC functions that accept a JSONB array of condition
        objects. A document matches if ANY condition is satisfied (OR across keys).

        Args:
            collection_ids: List of collection UUIDs to search across
            query_embedding: Query embedding vector
            n_results: Number of results to return
            embedding_model: Embedding model name
            filter_conditions: List of condition dicts from resolve_filters()

        Returns:
            Dictionary with documents, metadatas, distances, and ids
        """
        empty_result = {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

        try:
            if embedding_model is None:
                embedding_model = "text-embedding-3-small"

            dimension = EMBEDDING_DIMENSIONS.get(embedding_model, 1536)
            match_function = MATCH_FUNCTIONS_FILTERED.get(dimension)
            if not match_function:
                return empty_result

            rpc_params = {
                "p_collection_ids": collection_ids,
                "query_embedding": query_embedding,
                "match_threshold": 0.0,
                "match_count": n_results,
            }
            if filter_conditions:
                rpc_params["filter_conditions"] = filter_conditions

            rpc_result = self.client.rpc(match_function, rpc_params).execute()

            if not rpc_result.data:
                return empty_result

            documents, metadatas, distances, ids = [], [], [], []
            for doc in rpc_result.data:
                documents.append(doc["content"])
                metadatas.append(doc["metadata"] or {})
                distances.append(doc["similarity"])
                ids.append(doc["id"])

            return {
                "documents": [documents],
                "metadatas": [metadatas],
                "distances": [distances],
                "ids": [ids]
            }

        except Exception as e:
            print(f"[QUERY_FILTERED] ERROR: {e}")
            return empty_result

    def get_collection_embedding_model(self, collection_name: str) -> str:
        """Get the embedding model used by a collection."""
        try:
            collection = self._get_collection_data(collection_name)
            metadata = collection.get("metadata", {})
            return metadata.get("embedding_model", "text-embedding-3-small")
        except Exception as e:
            print(f"Error getting embedding model for {collection_name}: {e}")
            return "text-embedding-3-small"

    def get_retrieval_settings(self, collection_name: str) -> Dict[str, Any]:
        """Get the retrieval settings for a collection."""
        default_settings = {
            "search_mode": "hybrid",
            "reranking_enabled": True,
            "legal_tokenization": True,
            "sac_enabled": False,
            "hyde_enabled": False,
            "query_decomposition_enabled": False,
            "agentic_enabled": False,
            "colbert_enabled": False,
            "metadata_extraction": {
                "document_type": True,
                "date": True,
                "jurisdiction": False,
                "parties": False,
                "practice_area": False
            }
        }

        try:
            collection = self._get_collection_data(collection_name)
            settings = collection.get("retrieval_settings")

            if settings is None:
                return default_settings

            merged = {**default_settings, **settings}
            if "metadata_extraction" in settings:
                merged["metadata_extraction"] = {
                    **default_settings["metadata_extraction"],
                    **settings["metadata_extraction"]
                }
            return merged

        except Exception as e:
            print(f"Error getting retrieval settings for {collection_name}: {e}")
            return default_settings


class SupabaseCollection:
    """Wrapper class providing a ChromaDB-compatible interface for Supabase collections."""

    def __init__(self, client: SupabaseVectorClient, name: str, collection_data: Dict[str, Any]):
        self.client = client
        self.name = name
        self.collection_data = collection_data

    def add(self, documents: List[str], embeddings: List[List[float]] = None,
            metadatas: List[Dict[str, Any]] = None, ids: List[str] = None,
            embedding_model: str = None, sentence_embeddings: List[List[List[float]]] = None,
            sentence_texts: List[List[str]] = None):
        """Add documents to the collection."""
        if embeddings is None:
            raise ValueError("Embeddings are required for Supabase implementation")

        return self.client.add_documents(
            collection_name=self.name,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
            embedding_model=embedding_model,
            sentence_embeddings=sentence_embeddings,
            sentence_texts=sentence_texts
        )

    def query(self, query_embeddings: List[List[float]], n_results: int = 5,
              where: Dict[str, Any] = None, embedding_model: str = None, **kwargs):
        """Query the collection for similar documents."""
        if not query_embeddings or not query_embeddings[0]:
            raise ValueError("Query embeddings are required")

        return self.client.query_collection(
            collection_name=self.name,
            query_embedding=query_embeddings[0],
            n_results=n_results,
            where=where,
            embedding_model=embedding_model
        )

    def get(self, ids: List[str] = None, where: Dict[str, Any] = None,
            include: List[str] = None, **kwargs):
        """Get documents from the collection by ID."""
        return self.client.get_documents(
            collection_name=self.name,
            ids=ids,
            where=where,
            include=include
        )

    def delete(self, ids: List[str], **kwargs):
        """Delete documents from the collection."""
        return self.client.delete_documents(
            collection_name=self.name,
            ids=ids
        )

    def count(self) -> int:
        """Count documents in the collection."""
        return self.client.count_documents(self.name)


# Singleton instance
_supabase_client_instance = None


def get_supabase_client(use_service_key: bool = False) -> SupabaseVectorClient:
    """Get or create a Supabase client instance."""
    global _supabase_client_instance
    if _supabase_client_instance is None or use_service_key:
        _supabase_client_instance = SupabaseVectorClient(use_service_key=use_service_key)
    return _supabase_client_instance
