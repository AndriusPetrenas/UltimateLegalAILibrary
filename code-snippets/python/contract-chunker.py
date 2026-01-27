"""
Smart Contract Chunker
Splits legal documents into semantically meaningful chunks for RAG.

License: CC0 (Public Domain)
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chunk:
    """Represents a document chunk."""
    content: str
    chunk_type: str  # section, clause, paragraph, definition
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    parent_section: Optional[str] = None
    start_char: int = 0
    end_char: int = 0


def chunk_contract(
    text: str,
    max_chunk_size: int = 1000,
    overlap: int = 100,
    preserve_sections: bool = True
) -> List[Chunk]:
    """
    Split a contract into chunks suitable for embedding.

    Args:
        text: Full contract text
        max_chunk_size: Maximum characters per chunk
        overlap: Character overlap between chunks
        preserve_sections: Try to keep sections intact

    Returns:
        List of Chunk objects
    """
    chunks = []

    # First, try to split by section headers
    section_pattern = re.compile(
        r'^(\d+(?:\.\d+)*)\s*[.\-–]\s*(.+?)(?=\n)',
        re.MULTILINE
    )

    sections = []
    last_end = 0

    for match in section_pattern.finditer(text):
        # Add text before this section
        if match.start() > last_end:
            preamble = text[last_end:match.start()].strip()
            if preamble:
                sections.append({
                    'number': None,
                    'title': 'Preamble',
                    'start': last_end,
                    'content': preamble
                })

        # Find section end (next section or end of doc)
        next_match = section_pattern.search(text, match.end())
        section_end = next_match.start() if next_match else len(text)

        sections.append({
            'number': match.group(1),
            'title': match.group(2).strip(),
            'start': match.start(),
            'content': text[match.start():section_end].strip()
        })
        last_end = section_end

    # If no sections found, treat whole document as one section
    if not sections:
        sections = [{
            'number': None,
            'title': 'Document',
            'start': 0,
            'content': text
        }]

    # Now chunk each section
    for section in sections:
        section_content = section['content']

        if len(section_content) <= max_chunk_size:
            # Section fits in one chunk
            chunks.append(Chunk(
                content=section_content,
                chunk_type='section',
                section_number=section['number'],
                section_title=section['title'],
                start_char=section['start'],
                end_char=section['start'] + len(section_content)
            ))
        else:
            # Need to split section into smaller chunks
            # Try to split on paragraph boundaries
            paragraphs = re.split(r'\n\s*\n', section_content)

            current_chunk = ""
            chunk_start = section['start']

            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(Chunk(
                            content=current_chunk.strip(),
                            chunk_type='paragraph',
                            section_number=section['number'],
                            section_title=section['title'],
                            start_char=chunk_start,
                            end_char=chunk_start + len(current_chunk)
                        ))
                        chunk_start += len(current_chunk) - overlap

                    # Start new chunk with overlap
                    if overlap > 0 and current_chunk:
                        current_chunk = current_chunk[-overlap:] + para + "\n\n"
                    else:
                        current_chunk = para + "\n\n"

            # Don't forget the last chunk
            if current_chunk.strip():
                chunks.append(Chunk(
                    content=current_chunk.strip(),
                    chunk_type='paragraph',
                    section_number=section['number'],
                    section_title=section['title'],
                    start_char=chunk_start,
                    end_char=chunk_start + len(current_chunk)
                ))

    return chunks


def add_context_prefix(chunk: Chunk) -> str:
    """
    Add contextual prefix to chunk for better retrieval.

    Args:
        chunk: Chunk object

    Returns:
        Chunk content with context prefix
    """
    prefix_parts = []

    if chunk.section_number:
        prefix_parts.append(f"Section {chunk.section_number}")

    if chunk.section_title:
        prefix_parts.append(chunk.section_title)

    if prefix_parts:
        prefix = f"[{' - '.join(prefix_parts)}]\n\n"
        return prefix + chunk.content

    return chunk.content


# Example usage
if __name__ == "__main__":
    sample_contract = """
    MASTER SERVICE AGREEMENT

    This Agreement is entered into as of January 1, 2026.

    1. DEFINITIONS

    1.1 "Services" means the consulting services described in Exhibit A.

    1.2 "Confidential Information" means any non-public information.

    2. SERVICES

    2.1 Scope. Provider shall perform the Services in accordance with
    the specifications set forth in Exhibit A.

    2.2 Standards. All Services shall be performed in a professional
    and workmanlike manner consistent with industry standards.

    3. PAYMENT

    3.1 Fees. Client shall pay Provider the fees set forth in Exhibit B.

    3.2 Expenses. Client shall reimburse Provider for pre-approved expenses.
    """

    chunks = chunk_contract(sample_contract, max_chunk_size=500)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1} ({chunk.chunk_type}):")
        print(f"  Section: {chunk.section_number} - {chunk.section_title}")
        print(f"  Length: {len(chunk.content)} chars")
        print(f"  Preview: {chunk.content[:100]}...")
        print()
