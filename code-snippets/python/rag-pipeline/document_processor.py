"""
Utilities for processing legal documents and creating embeddings.

Features:
- Token-based chunking (using tiktoken) for consistent semantic units
- Structure-aware chunking for legal documents (Article, Section, etc.)
- Template-based contextual prefixes for improved retrieval
- Multi-level hierarchical chunking with metadata preservation
"""

import os
from typing import List, Dict, Any, Tuple
import uuid
import ssl
import urllib3
import time
import tiktoken
from langchain_community.embeddings import HuggingFaceEmbeddings
# Lazy import for document processing libraries to avoid startup issues
import torch
from tqdm import tqdm
from supabase_client import SupabaseVectorClient, SupabaseCollection

# Disable SSL warnings and configure SSL context to handle SSL errors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize tiktoken encoder (cl100k_base is used by OpenAI models)
# This provides consistent token counting across different embedding models
try:
    TOKENIZER = tiktoken.get_encoding("cl100k_base")
except Exception:
    TOKENIZER = None


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for

    Returns:
        Number of tokens (falls back to character estimate if tiktoken unavailable)
    """
    if TOKENIZER is None:
        # Fallback: estimate ~4 chars per token
        return len(text) // 4
    return len(TOKENIZER.encode(text))


def generate_context_prefix(
    doc_title: str = None,
    section_info: Dict[str, Any] = None,
    legal_metadata: Dict[str, Any] = None
) -> str:
    """Generate a template-based context prefix for a chunk.

    This provides document/section context without requiring an LLM call.
    Research shows contextual prefixes improve retrieval by ~49% (Anthropic, 2024).

    Args:
        doc_title: Source document filename/title
        section_info: Section metadata (section_id, section_num, type, etc.)
        legal_metadata: Extracted legal metadata (article_refs, entities, etc.)

    Returns:
        Context prefix string to prepend to chunk before embedding
    """
    parts = []

    # Document source
    if doc_title:
        # Clean up filename for display
        clean_title = doc_title.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        parts.append(f"Document: {clean_title}")

    # Section information
    if section_info:
        if section_id := section_info.get("section_id"):
            parts.append(f"Section: {section_id}")
        elif section_num := section_info.get("section_num"):
            parts.append(f"Section: {section_num}")

        # Add section type context
        section_type = section_info.get("type", "")
        if section_type == "legal_section":
            parts.append("Type: Legal provision")
        elif section_type == "subsection":
            if subsec_id := section_info.get("subsection_id"):
                parts.append(f"Subsection: {subsec_id}")
        elif section_type == "numbered_item":
            if item_num := section_info.get("item_num"):
                parts.append(f"Item: {item_num}")

    # Legal metadata for richer context
    if legal_metadata:
        # Article/section references
        if refs := legal_metadata.get("article_refs"):
            refs_str = ", ".join(refs[:3])  # Limit to 3
            parts.append(f"References: {refs_str}")

        # Legal entities mentioned
        if entities := legal_metadata.get("legal_entities"):
            unique_entities = list(set(e.lower() for e in entities))[:3]
            parts.append(f"Entities: {', '.join(unique_entities)}")

        # Dates if present
        if dates := legal_metadata.get("dates"):
            parts.append(f"Dates: {dates[0]}")  # First date only

        # Citations
        if citations := legal_metadata.get("citations"):
            parts.append(f"Cites: {citations[0]}")  # First citation only

    if not parts:
        return ""

    return f"[{' | '.join(parts)}] "

class LegalDocumentProcessor:
    """Processor for legal documents with specialized handling for legal terminology.

    Features:
    - Token-based chunking for consistent semantic units
    - Structure-aware chunking (Article, Section, subsection detection)
    - Template-based contextual prefixes for improved retrieval
    - Legal metadata extraction (citations, entities, dates)
    """

    # Default chunking parameters (token-based)
    DEFAULT_CHUNK_SIZE_TOKENS = 256  # ~1024 chars, optimal for legal text
    DEFAULT_CHUNK_OVERLAP_TOKENS = 50  # ~200 chars, 20% overlap
    DEFAULT_CONTEXT_PREFIX_MAX_TOKENS = 50  # Reserve tokens for context prefix

    def __init__(
        self,
        embedding_model: str = None,
        device: str = None,
        chunk_size_tokens: int = None,
        chunk_overlap_tokens: int = None,
        use_contextual_prefixes: bool = True,
        embedding_service = None
    ):
        """Initialize the document processor.

        Args:
            embedding_model: Name of the HuggingFace embedding model (only used if embedding_service not provided)
            device: Device to use for embeddings ('cuda' or 'cpu')
            chunk_size_tokens: Target chunk size in tokens (default: 256)
            chunk_overlap_tokens: Overlap between chunks in tokens (default: 50)
            use_contextual_prefixes: Whether to add context prefixes to chunks (default: True)
            embedding_service: Optional external embedding service (with embed_query and embed_documents methods).
                               When provided, this service is used instead of HuggingFaceEmbeddings.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Use external embedding service if provided, otherwise fall back to HuggingFace
        if embedding_service is not None:
            self.embeddings = embedding_service
            self._using_external_embedding_service = True
            print(f"[DOC_PROCESSOR] Using external embedding service: {type(embedding_service).__name__}")
        else:
            if not embedding_model:
                embedding_model = "BAAI/bge-large-en-v1.5"  # Default fallback
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={"device": self.device}
            )
            self._using_external_embedding_service = False

        # Chunking configuration
        self.chunk_size_tokens = chunk_size_tokens or self.DEFAULT_CHUNK_SIZE_TOKENS
        self.chunk_overlap_tokens = chunk_overlap_tokens or self.DEFAULT_CHUNK_OVERLAP_TOKENS
        self.use_contextual_prefixes = use_contextual_prefixes

        # Initialize Supabase client
        try:
            self.supabase_client = SupabaseVectorClient(use_service_key=True)
        except Exception as e:
            print(f"Warning: Could not connect to Supabase: {e}")
            self.supabase_client = None
    
    def _generate_embeddings_with_retry(self, texts: List[str], max_retries: int = 3) -> List[List[float]]:
        """Generate embeddings with retry logic for SSL errors.

        Args:
            texts: List of texts to embed
            max_retries: Maximum number of retry attempts

        Returns:
            List of embedding vectors
        """
        for attempt in range(max_retries):
            try:
                # Try to generate embeddings
                embeddings = self.embeddings.embed_documents(texts)
                return embeddings
            except (ssl.SSLError, Exception) as e:
                if "EOF occurred in violation of protocol" in str(e) or "SSL" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        print(f"SSL error on attempt {attempt + 1}, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)

                        # Only reinitialize for HuggingFace embeddings (not external services)
                        if not self._using_external_embedding_service:
                            try:
                                self.embeddings = HuggingFaceEmbeddings(
                                    model_name=self.embeddings.model_name,
                                    model_kwargs={"device": self.device}
                                )
                            except Exception as reinit_e:
                                print(f"Failed to reinitialize embeddings model: {reinit_e}")
                    else:
                        print(f"SSL error persists after {max_retries} attempts: {e}")
                        raise
                else:
                    # Non-SSL error, raise immediately
                    raise
    
    def _generate_query_embedding_with_retry(self, query: str, max_retries: int = 3) -> List[float]:
        """Generate query embedding with retry logic for SSL errors.

        Args:
            query: Query text to embed
            max_retries: Maximum number of retry attempts

        Returns:
            Query embedding vector
        """
        for attempt in range(max_retries):
            try:
                # Try to generate query embedding
                embedding = self.embeddings.embed_query(query)
                return embedding
            except (ssl.SSLError, Exception) as e:
                if "EOF occurred in violation of protocol" in str(e) or "SSL" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        print(f"SSL error on query attempt {attempt + 1}, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)

                        # Only reinitialize for HuggingFace embeddings (not external services)
                        if not self._using_external_embedding_service:
                            try:
                                self.embeddings = HuggingFaceEmbeddings(
                                    model_name=self.embeddings.model_name,
                                    model_kwargs={"device": self.device}
                                )
                            except Exception as reinit_e:
                                print(f"Failed to reinitialize embeddings model: {reinit_e}")
                    else:
                        print(f"SSL error persists after {max_retries} attempts on query: {e}")
                        raise
                else:
                    # Non-SSL error, raise immediately
                    raise
    
    def process_document(
        self,
        file_path: str,
        chunk_size_tokens: int = None,
        chunk_overlap_tokens: int = None
    ) -> List[Dict[str, Any]]:
        """Process a single document and return chunked text with metadata.

        Args:
            file_path: Path to the document
            chunk_size_tokens: Override chunk size in tokens (uses instance default if None)
            chunk_overlap_tokens: Override overlap in tokens (uses instance default if None)

        Returns:
            List of chunk dictionaries with 'text', 'text_with_context', and 'metadata'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Use instance defaults if not specified
        chunk_size = chunk_size_tokens or self.chunk_size_tokens
        chunk_overlap = chunk_overlap_tokens or self.chunk_overlap_tokens

        # Extract document title from filename
        doc_title = os.path.basename(file_path)

        # Get document processing libraries from main module
        try:
            from unstructured.partition.pdf import partition_pdf as partition_pdf_func
        except ImportError:
            raise ImportError("unstructured library not available. Install with: pip install unstructured[pdf]")

        # Extract text from PDF using unstructured
        elements = partition_pdf_func(
            file_path,
            strategy="hi_res",
            infer_table_structure=True
        )

        # Process text elements
        texts = []
        for element in elements:
            if hasattr(element, 'text'):
                text = element.text
                if text:
                    # Import cleaner (should be loaded at startup)
                    try:
                        from unstructured.cleaners.core import clean_extra_whitespace
                    except ImportError:
                        # If cleaner not available, use basic cleanup
                        def clean_extra_whitespace(text):
                            return ' '.join(text.split())

                    # Clean text
                    text = clean_extra_whitespace(text)
                    texts.append(text)

        # Chunk the text with contextual prefixes
        chunks = self._chunk_text(
            texts=texts,
            chunk_size_tokens=chunk_size,
            chunk_overlap_tokens=chunk_overlap,
            doc_title=doc_title
        )

        return chunks
    
    def _chunk_text(
        self,
        texts: List[str],
        chunk_size_tokens: int,
        chunk_overlap_tokens: int,
        doc_title: str = None
    ) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks using token-based sizing.

        This method uses a multi-level approach:
        1. Detect legal structure (Article, Section, etc.)
        2. Split by structure when possible
        3. Fall back to sentence grouping for unstructured text
        4. Generate contextual prefixes for each chunk

        Args:
            texts: List of text strings from document
            chunk_size_tokens: Target chunk size in tokens
            chunk_overlap_tokens: Overlap between chunks in tokens
            doc_title: Document filename for context prefix

        Returns:
            List of chunk dictionaries with:
            - 'text': Original chunk text
            - 'text_with_context': Chunk with contextual prefix (for embedding)
            - 'metadata': Chunk metadata including structure info
        """
        import re
        import nltk

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        from nltk.tokenize import sent_tokenize

        # Precompile regex patterns for legal structure detection
        section_pattern = re.compile(
            r"(Article|Section|Regulation|ARTICLE|SECTION|§|Chapter|Part|Title|Rule)\s+(\d+[\.\d]*\w*)",
            re.IGNORECASE
        )
        subsection_pattern = re.compile(r"^\s*\(?([a-z])\)\s+", re.IGNORECASE | re.MULTILINE)
        numbered_pattern = re.compile(r"^\s*(\d+)\.\s+", re.MULTILINE)

        # Legal metadata extraction patterns
        legal_patterns = {
            "article_refs": re.compile(
                r"(Article|Section|Regulation|§)\s+(\d+[\.\d]*\w*)",
                re.IGNORECASE
            ),
            "date_patterns": re.compile(
                r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)|"
                r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2})[,\s]+(\d{4})",
                re.IGNORECASE
            ),
            "citation_patterns": re.compile(
                r"\(\s*([12]\d{3})\s*\)\s*(\d+)\s*([A-Za-z]+)\s*(\d+)",
                re.IGNORECASE
            ),
            "legal_entity": re.compile(
                r"\b(plaintiff|defendant|respondent|appellant|applicant|claimant|"
                r"court|judge|justice|tribunal|council|committee|commission|"
                r"parliament|legislature|government|minister|authority)\b",
                re.IGNORECASE
            ),
        }

        chunks_with_metadata = []

        def extract_legal_metadata(text: str) -> Dict[str, Any]:
            """Extract legal metadata from text chunk."""
            metadata = {}

            # Article/section references
            refs = legal_patterns["article_refs"].findall(text)
            if refs:
                metadata["article_refs"] = [f"{r[0]} {r[1]}" for r in refs[:5]]

            # Dates
            dates = legal_patterns["date_patterns"].findall(text)
            if dates:
                metadata["dates"] = [f"{d[0]}, {d[1]}" for d in dates[:3]]

            # Citations
            citations = legal_patterns["citation_patterns"].findall(text)
            if citations:
                metadata["citations"] = [f"({c[0]}) {c[1]} {c[2]} {c[3]}" for c in citations[:3]]

            # Legal entities
            entities = legal_patterns["legal_entity"].findall(text)
            if entities:
                metadata["legal_entities"] = list(set(e.lower() for e in entities))[:5]

            return metadata

        def split_by_tokens(
            text: str,
            max_tokens: int,
            overlap_tokens: int,
            base_metadata: Dict[str, Any]
        ) -> List[Dict[str, Any]]:
            """Split text into token-sized chunks with overlap."""
            results = []
            sentences = sent_tokenize(text)

            current_chunk = []
            current_tokens = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                sentence_tokens = count_tokens(sentence)

                # If single sentence exceeds max, split by characters as fallback
                if sentence_tokens > max_tokens:
                    # Save current chunk if any
                    if current_chunk:
                        chunk_text = " ".join(current_chunk)
                        results.append({
                            "text": chunk_text,
                            "metadata": {**base_metadata, "token_count": current_tokens}
                        })
                        current_chunk = []
                        current_tokens = 0

                    # Split long sentence by approximate token boundaries
                    words = sentence.split()
                    word_chunk = []
                    word_tokens = 0

                    for word in words:
                        word_token_count = count_tokens(word + " ")
                        if word_tokens + word_token_count > max_tokens and word_chunk:
                            chunk_text = " ".join(word_chunk)
                            results.append({
                                "text": chunk_text,
                                "metadata": {**base_metadata, "token_count": word_tokens, "type": "word_split"}
                            })
                            # Keep overlap
                            overlap_words = max(1, len(word_chunk) * overlap_tokens // max_tokens)
                            word_chunk = word_chunk[-overlap_words:] + [word]
                            word_tokens = count_tokens(" ".join(word_chunk))
                        else:
                            word_chunk.append(word)
                            word_tokens += word_token_count

                    if word_chunk:
                        chunk_text = " ".join(word_chunk)
                        results.append({
                            "text": chunk_text,
                            "metadata": {**base_metadata, "token_count": count_tokens(chunk_text), "type": "word_split"}
                        })
                    continue

                # Check if adding sentence exceeds limit
                if current_tokens + sentence_tokens > max_tokens and current_chunk:
                    # Save current chunk
                    chunk_text = " ".join(current_chunk)
                    results.append({
                        "text": chunk_text,
                        "metadata": {**base_metadata, "token_count": current_tokens}
                    })

                    # Start new chunk with overlap (keep last N tokens worth of sentences)
                    overlap_chunk = []
                    overlap_token_count = 0
                    for s in reversed(current_chunk):
                        s_tokens = count_tokens(s)
                        if overlap_token_count + s_tokens <= overlap_tokens:
                            overlap_chunk.insert(0, s)
                            overlap_token_count += s_tokens
                        else:
                            break

                    current_chunk = overlap_chunk + [sentence]
                    current_tokens = overlap_token_count + sentence_tokens
                else:
                    current_chunk.append(sentence)
                    current_tokens += sentence_tokens

            # Add final chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                results.append({
                    "text": chunk_text,
                    "metadata": {**base_metadata, "token_count": count_tokens(chunk_text)}
                })

            return results

        # Process each text block
        for text_idx, text in enumerate(texts):
            text_tokens = count_tokens(text)

            # Skip very short texts (less than 25 tokens)
            if text_tokens < 25:
                chunks_with_metadata.append({
                    "text": text,
                    "metadata": {
                        "type": "short_fragment",
                        "token_count": text_tokens,
                        "text_index": text_idx
                    }
                })
                continue

            # 1. Try to identify legal sections
            section_matches = list(section_pattern.finditer(text))

            if len(section_matches) > 1:
                # Text contains multiple identifiable sections - split by them
                for i, match in enumerate(section_matches):
                    start_pos = match.start()
                    end_pos = section_matches[i + 1].start() if i < len(section_matches) - 1 else len(text)

                    section_text = text[start_pos:end_pos].strip()
                    section_id = match.group(0).strip()
                    section_num = match.group(2).strip()

                    section_metadata = {
                        "type": "legal_section",
                        "section_id": section_id,
                        "section_num": section_num,
                        "text_index": text_idx
                    }

                    section_tokens = count_tokens(section_text)

                    if section_tokens <= chunk_size_tokens:
                        # Section fits in one chunk
                        chunks_with_metadata.append({
                            "text": section_text,
                            "metadata": {**section_metadata, "token_count": section_tokens}
                        })
                    else:
                        # Section too large - split by tokens
                        sub_chunks = split_by_tokens(
                            section_text,
                            chunk_size_tokens,
                            chunk_overlap_tokens,
                            section_metadata
                        )
                        chunks_with_metadata.extend(sub_chunks)
            else:
                # No clear section structure - try paragraphs or sentence grouping
                paragraphs = re.split(r"\n\s*\n", text)

                if len(paragraphs) > 1:
                    for para_idx, para in enumerate(paragraphs):
                        para = para.strip()
                        if not para:
                            continue

                        para_metadata = {
                            "type": "paragraph",
                            "paragraph_index": para_idx,
                            "text_index": text_idx
                        }

                        para_tokens = count_tokens(para)

                        if para_tokens <= chunk_size_tokens:
                            chunks_with_metadata.append({
                                "text": para,
                                "metadata": {**para_metadata, "token_count": para_tokens}
                            })
                        else:
                            sub_chunks = split_by_tokens(
                                para,
                                chunk_size_tokens,
                                chunk_overlap_tokens,
                                para_metadata
                            )
                            chunks_with_metadata.extend(sub_chunks)
                else:
                    # Single block of text - split by sentences/tokens
                    block_metadata = {
                        "type": "text_block",
                        "text_index": text_idx
                    }

                    if text_tokens <= chunk_size_tokens:
                        chunks_with_metadata.append({
                            "text": text,
                            "metadata": {**block_metadata, "token_count": text_tokens}
                        })
                    else:
                        sub_chunks = split_by_tokens(
                            text,
                            chunk_size_tokens,
                            chunk_overlap_tokens,
                            block_metadata
                        )
                        chunks_with_metadata.extend(sub_chunks)

        # 2. Extract legal metadata and generate context prefixes for each chunk
        final_chunks = []
        for chunk_idx, chunk_data in enumerate(chunks_with_metadata):
            chunk_text = chunk_data["text"]
            chunk_metadata = chunk_data["metadata"]

            # Extract legal metadata from chunk content
            legal_metadata = extract_legal_metadata(chunk_text)
            if legal_metadata:
                chunk_metadata["legal_metadata"] = legal_metadata

            # Generate context prefix
            if self.use_contextual_prefixes:
                context_prefix = generate_context_prefix(
                    doc_title=doc_title,
                    section_info=chunk_metadata,
                    legal_metadata=legal_metadata
                )
                text_with_context = context_prefix + chunk_text
            else:
                context_prefix = ""
                text_with_context = chunk_text

            # Add source document to metadata
            chunk_metadata["source"] = doc_title
            chunk_metadata["chunk_index"] = chunk_idx
            chunk_metadata["has_context_prefix"] = bool(context_prefix)

            final_chunks.append({
                "text": chunk_text,  # Original text (stored in DB)
                "text_with_context": text_with_context,  # Text with prefix (for embedding)
                "context_prefix": context_prefix,  # Just the prefix
                "metadata": chunk_metadata
            })

        return final_chunks
    
    def create_ragmodel(
        self,
        documents_dir: str,
        ragmodel_name: str,
        file_filter: str = "*.pdf",
        metadata_extractor=None
    ) -> Tuple[int, int]:
        """Process multiple documents and create a Supabase collection.

        Uses token-based chunking with contextual prefixes for improved retrieval.
        Embeddings are generated from text_with_context (includes context prefix)
        while original text is stored in the database.

        Args:
            documents_dir: Directory containing documents
            ragmodel_name: Name for the collection
            file_filter: Filter for files to process
            metadata_extractor: Optional function to extract metadata from filenames

        Returns:
            Tuple of (number of documents processed, number of chunks created)
        """
        import glob

        # Create or get collection using Supabase
        if self.supabase_client:
            collection_data = self.supabase_client.get_or_create_collection(ragmodel_name)
            collection = SupabaseCollection(self.supabase_client, ragmodel_name, collection_data)
        else:
            raise Exception("Supabase client not available for ragmodel creation")

        # Get list of PDF files
        file_paths = glob.glob(os.path.join(documents_dir, file_filter))

        doc_count = 0
        chunk_count = 0

        # Process each document
        for file_path in tqdm(file_paths, desc="Processing documents"):
            try:
                # Extract base filename
                filename = os.path.basename(file_path)

                # Process document - now returns list of chunk dictionaries
                chunks = self.process_document(file_path)

                if not chunks:
                    continue

                # Prepare for database insertion
                documents = []  # Original text (stored in DB)
                texts_for_embedding = []  # Text with context prefix (for embedding)
                metadatas = []
                ids = []

                # Extract base metadata if provided
                base_metadata = {}
                if metadata_extractor:
                    base_metadata = metadata_extractor(filename)

                # Process each chunk
                for chunk_data in chunks:
                    chunk_text = chunk_data["text"]
                    text_with_context = chunk_data["text_with_context"]
                    chunk_metadata = chunk_data["metadata"]

                    # Skip very short chunks (less than 25 tokens)
                    token_count = chunk_metadata.get("token_count", 0)
                    if token_count < 25:
                        continue

                    # Generate proper UUID for database compliance
                    chunk_id = str(uuid.uuid4())

                    # Merge with base metadata
                    final_metadata = {
                        **chunk_metadata,
                        **base_metadata
                    }

                    documents.append(chunk_text)  # Store original text
                    texts_for_embedding.append(text_with_context)  # Embed with context
                    metadatas.append(final_metadata)
                    ids.append(chunk_id)

                # Add to database in batches
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    end_idx = min(i + batch_size, len(documents))

                    batch_docs = documents[i:end_idx]  # Original text for storage
                    batch_texts_for_embed = texts_for_embedding[i:end_idx]  # Context-enhanced for embedding
                    batch_meta = metadatas[i:end_idx]
                    batch_ids = ids[i:end_idx]

                    # Generate embeddings from text WITH context prefix
                    # This improves retrieval by ~49% (Anthropic research)
                    try:
                        batch_embeddings = self._generate_embeddings_with_retry(batch_texts_for_embed)

                        # Store original text (without prefix) in database
                        # The embedding captures the contextual meaning
                        collection.add(
                            documents=batch_docs,
                            embeddings=batch_embeddings,
                            metadatas=batch_meta,
                            ids=batch_ids
                        )
                    except (ssl.SSLError, Exception) as e:
                        if "EOF occurred in violation of protocol" in str(e):
                            print(f"SSL error encountered, retrying batch {i//batch_size + 1}: {e}")
                            # Retry with smaller batch
                            for doc, text_embed, meta, doc_id in zip(
                                batch_docs, batch_texts_for_embed, batch_meta, batch_ids
                            ):
                                try:
                                    doc_embedding = self._generate_embeddings_with_retry([text_embed])
                                    collection.add(
                                        documents=[doc],
                                        embeddings=doc_embedding,
                                        metadatas=[meta],
                                        ids=[doc_id]
                                    )
                                except Exception as retry_e:
                                    print(f"Failed to add document {doc_id}: {retry_e}")
                        else:
                            raise e

                doc_count += 1
                chunk_count += len(documents)

                print(f"Processed {filename}: {len(documents)} chunks "
                      f"(contextual prefixes: {sum(1 for m in metadatas if m.get('has_context_prefix'))})")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return doc_count, chunk_count
    
    def query_ragmodel(
        self, 
        ragmodel_name: str, 
        query: str, 
        n_results: int = 5,
        use_hybrid_search: bool = True,
        use_reranking: bool = True
    ) -> Dict[str, Any]:
        """Query a ragmodel with a natural language query.
        
        Args:
            ragmodel_name: Name of the Chroma collection
            query: Natural language query
            n_results: Number of results to return
            use_hybrid_search: Whether to use hybrid search (vector + BM25)
            use_reranking: Whether to rerank results for better relevance
            
        Returns:
            Dictionary with query results
        """
        # Import numpy for array operations
        import numpy as np
        
        # Get collection using Supabase
        if self.supabase_client:
            collection_data = self.supabase_client.get_collection(ragmodel_name)
            collection = SupabaseCollection(self.supabase_client, ragmodel_name, collection_data)
        else:
            raise Exception("Supabase client not available for ragmodel query")
        
        # 1. Hybrid Search: Combine vector search with keyword search
        if use_hybrid_search:
            # Vector search component
            vector_results = collection.query(
                query_texts=[query],
                n_results=min(n_results * 2, 20)  # Get more results for hybrid reranking
            )
            
            # Keyword search component (using where filter with $contains operator)
            # Split query into keywords
            keywords = [kw.strip() for kw in query.lower().split() if len(kw.strip()) > 3]
            
            # Get unique document IDs from vector search
            vector_doc_ids = vector_results["ids"][0]
            all_results = {
                "ids": [vector_doc_ids],
                "documents": [vector_results["documents"][0]],
                "metadatas": [vector_results["metadatas"][0]],
                "distances": [vector_results["distances"][0]] if "distances" in vector_results else None
            }
            
            # If we have keywords, enhance with keyword search
            if keywords:
                # For each significant keyword, find matching documents
                for keyword in keywords[:3]:  # Limit to top 3 keywords
                    try:
                        # Use metadata $contains filter as keyword search
                        keyword_results = collection.query(
                            query_texts=[query],
                            where_document={"$contains": keyword},
                            n_results=min(n_results, 10)
                        )
                        
                        # Merge results if we found any
                        if keyword_results["ids"][0]:
                            for i, doc_id in enumerate(keyword_results["ids"][0]):
                                # Skip if already in results
                                if doc_id in vector_doc_ids:
                                    continue
                                
                                # Add new items to result lists
                                all_results["ids"][0].append(doc_id)
                                all_results["documents"][0].append(keyword_results["documents"][0][i])
                                all_results["metadatas"][0].append(keyword_results["metadatas"][0][i])
                                if all_results["distances"] is not None:
                                    # Assign a distance value slightly worse than the worst vector distance
                                    max_dist = max(all_results["distances"][0]) if all_results["distances"][0] else 1.0
                                    all_results["distances"][0].append(max_dist * 1.1)
                    except Exception as e:
                        print(f"Error in keyword search for '{keyword}': {str(e)}")
            
            results = all_results
            
            # 2. Reranking: Use cross-encoder to rerank combined results
            if use_reranking and len(results["documents"][0]) > 0:
                try:
                    from sentence_transformers import CrossEncoder
                    
                    # Check if we have more documents than requested results
                    if len(results["documents"][0]) > n_results:
                        # Load cross-encoder model for reranking
                        reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=self.device)
                        
                        # Prepare document-query pairs for reranking
                        pairs = [(query, doc) for doc in results["documents"][0]]
                        
                        # Get relevance scores
                        rerank_scores = reranker.predict(pairs)
                        
                        # Create index based on scores
                        rerank_indexes = np.argsort(-np.array(rerank_scores))  # Sort in descending order
                        
                        # Reorder all result components based on reranking
                        results["documents"][0] = [results["documents"][0][i] for i in rerank_indexes[:n_results]]
                        results["ids"][0] = [results["ids"][0][i] for i in rerank_indexes[:n_results]]
                        results["metadatas"][0] = [results["metadatas"][0][i] for i in rerank_indexes[:n_results]]
                        if results["distances"] is not None:
                            results["distances"][0] = [results["distances"][0][i] for i in rerank_indexes[:n_results]]
                except Exception as e:
                    print(f"Error in reranking: {str(e)}")
        else:
            # Standard vector search if hybrid search is disabled
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
        return results

    def query_dataset(self, dataset_name, query, n_results=5, use_hybrid_search=True, use_reranking=True, where=None, source_filters=None):
        """Query the Supabase collection for relevant documents and metadatas with enhanced retrieval.

        Args:
            source_filters: List of active UI filter keys (e.g. ['codes', 'cour_de_cassation']).
                When provided, uses filtered RPC functions to restrict results by legal source metadata.
        """
        if self.supabase_client:
            try:
                # Generate query embedding with retry logic
                query_embedding = self._generate_query_embedding_with_retry(query)

                # If source filters are active, use filtered query path (legal sources mode)
                if source_filters:
                    from legal_filters import resolve_filters
                    filter_conditions = resolve_filters(source_filters)
                    print(f"[QUERY] Legal sources mode: {len(source_filters)} filter keys -> "
                          f"conditions={filter_conditions}")

                    # Gather legal source collection IDs only (no user dataset)
                    collection_ids = []
                    try:
                        all_collections = self.supabase_client.client.table("collections") \
                            .select("id, metadata") \
                            .execute()
                        if all_collections.data:
                            for col in all_collections.data:
                                meta = col.get("metadata") or {}
                                if meta.get("source_type") == "legal_source":
                                    collection_ids.append(col["id"])
                        print(f"[QUERY] Found {len(collection_ids)} legal source collections")
                    except Exception as e:
                        print(f"[QUERY] Warning: could not fetch legal collections: {e}")
                        import traceback
                        traceback.print_exc()

                    if collection_ids:
                        try:
                            filtered_results = self.supabase_client.query_collection_filtered(
                                collection_ids=collection_ids,
                                query_embedding=query_embedding,
                                n_results=n_results,
                                filter_conditions=filter_conditions,
                            )
                            return filtered_results
                        except Exception as e:
                            print(f"[QUERY] ERROR in query_collection_filtered: {e}")
                            import traceback
                            traceback.print_exc()
                            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
                    else:
                        print("[QUERY] No legal source collections found")
                        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

                if use_hybrid_search:
                    # Step 1: Vector similarity search - get more results for reranking
                    vector_results = self.supabase_client.query_collection(
                        collection_name=dataset_name,
                        query_embedding=query_embedding,
                        n_results=min(n_results * 3, 30),  # Get 3x results for better reranking
                        where=where
                    )
                    
                    # Step 2: Keyword-based search using Supabase full-text search
                    # Extract keywords from query
                    import re
                    keywords = [word.lower() for word in re.findall(r'\b\w+\b', query) 
                               if len(word) > 3 and word.lower() not in {'what', 'when', 'where', 'which', 'that', 'this', 'from', 'with'}]
                    
                    # Initialize combined results
                    all_documents = vector_results.get("documents", [[]])[0]
                    all_metadatas = vector_results.get("metadatas", [[]])[0]
                    all_distances = vector_results.get("distances", [[]])[0]
                    all_ids = vector_results.get("ids", [[]])[0]
                    seen_ids = set(all_ids)
                    
                    # Perform keyword search for each significant keyword
                    for keyword in keywords[:3]:  # Limit to top 3 keywords
                        try:
                            # Search in document content using Supabase's text search
                            keyword_results = self.supabase_client.search_documents_by_content(
                                collection_name=dataset_name,
                                search_text=keyword,
                                n_results=10
                            )
                            
                            # Merge keyword results with vector results
                            if keyword_results and keyword_results.get("ids"):
                                for i, doc_id in enumerate(keyword_results["ids"][0]):
                                    if doc_id not in seen_ids:
                                        all_ids.append(doc_id)
                                        all_documents.append(keyword_results["documents"][0][i])
                                        all_metadatas.append(keyword_results["metadatas"][0][i])
                                        # Assign slightly worse distance for keyword matches
                                        max_dist = max(all_distances) if all_distances else 1.0
                                        all_distances.append(max_dist * 1.2)
                                        seen_ids.add(doc_id)
                        except Exception as e:
                            print(f"Keyword search for '{keyword}' failed: {e}")
                    
                    # Prepare results for reranking
                    results = {
                        "documents": [all_documents],
                        "metadatas": [all_metadatas],
                        "distances": [all_distances],
                        "ids": [all_ids]
                    }
                    
                    # Step 3: Rerank results using Cross-Encoder (more accurate than bi-encoder)
                    if use_reranking and len(all_documents) > n_results:
                        try:
                            from reranker import rerank_results

                            # Prepare documents for reranking
                            docs_for_rerank = []
                            for i, doc in enumerate(all_documents[:30]):  # Limit to 30 for performance
                                docs_for_rerank.append({
                                    'document': doc,
                                    'metadata': all_metadatas[i] if i < len(all_metadatas) else {},
                                    'distance': all_distances[i] if i < len(all_distances) else 1.0,
                                    'id': all_ids[i] if i < len(all_ids) else f"doc_{i}"
                                })

                            # Apply cross-encoder reranking
                            reranked, rerank_meta = rerank_results(
                                query=query,
                                results=docs_for_rerank,
                                top_k=n_results,
                                enabled=True
                            )

                            print(f"[QUERY] Cross-encoder reranking: {rerank_meta['input_count']} -> {rerank_meta['output_count']} docs in {rerank_meta.get('latency_ms', 0)}ms")

                            # Reconstruct results in expected format
                            results = {
                                "documents": [[doc['document'] for doc in reranked]],
                                "metadatas": [[doc['metadata'] for doc in reranked]],
                                "distances": [[doc.get('distance', 1.0) for doc in reranked]],
                                "ids": [[doc['id'] for doc in reranked]],
                                "rerank_scores": [[doc.get('rerank_score', 0.0) for doc in reranked]]
                            }
                        except ImportError as e:
                            print(f"[QUERY] Cross-encoder not available, falling back to bi-encoder: {e}")
                            # Fall back to bi-encoder reranking
                            import numpy as np
                            doc_embeddings = self._generate_embeddings_with_retry(all_documents[:20])
                            query_emb_array = np.array(query_embedding)
                            doc_emb_array = np.array(doc_embeddings)
                            similarities = np.dot(doc_emb_array, query_emb_array) / (
                                np.linalg.norm(doc_emb_array, axis=1) * np.linalg.norm(query_emb_array)
                            )
                            top_indices = np.argsort(-similarities)[:n_results]
                            results = {
                                "documents": [[all_documents[i] for i in top_indices]],
                                "metadatas": [[all_metadatas[i] for i in top_indices]],
                                "distances": [[all_distances[i] for i in top_indices]],
                                "ids": [[all_ids[i] for i in top_indices]]
                            }
                        except Exception as e:
                            print(f"[QUERY] Reranking failed: {e}")
                            # Fall back to truncating results
                            results = {
                                "documents": [all_documents[:n_results]],
                                "metadatas": [all_metadatas[:n_results]],
                                "distances": [all_distances[:n_results]],
                                "ids": [all_ids[:n_results]]
                            }
                else:
                    # Standard vector search only
                    results = self.supabase_client.query_collection(
                        collection_name=dataset_name,
                        query_embedding=query_embedding,
                        n_results=n_results,
                        where=where
                    )
                
                return results
                
            except Exception as e:
                print(f"Error querying Supabase dataset {dataset_name}: {e}")
                return {
                    "documents": [[]],
                    "metadatas": [[]],
                    "distances": [[]],
                    "ids": [[]]
                }
        else:
            print("Supabase not available for query_dataset")
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "ids": [[]]
            }