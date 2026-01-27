"""
Legal Citation Parser
Extracts and normalizes legal citations from text.

License: CC0 (Public Domain)
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Citation:
    """Represents a parsed legal citation."""
    full_text: str
    volume: Optional[str] = None
    reporter: Optional[str] = None
    page: Optional[str] = None
    court: Optional[str] = None
    year: Optional[str] = None
    pin_cite: Optional[str] = None
    citation_type: str = "unknown"  # case, statute, regulation


# Common reporter abbreviations
REPORTERS = {
    "U.S.": "United States Reports",
    "S.Ct.": "Supreme Court Reporter",
    "L.Ed.": "Lawyers' Edition",
    "F.2d": "Federal Reporter, Second Series",
    "F.3d": "Federal Reporter, Third Series",
    "F.4th": "Federal Reporter, Fourth Series",
    "F.Supp.": "Federal Supplement",
    "F.Supp.2d": "Federal Supplement, Second Series",
    "F.Supp.3d": "Federal Supplement, Third Series",
}

# Case citation pattern: Volume Reporter Page (Court Year)
CASE_PATTERN = re.compile(
    r'(\d+)\s+'                           # Volume
    r'([A-Z][A-Za-z\.\s]+?)\s+'           # Reporter
    r'(\d+)'                              # Page
    r'(?:,\s*(\d+))?'                     # Pin cite (optional)
    r'\s*\(([^)]+)\s+(\d{4})\)',          # Court and Year
    re.VERBOSE
)

# Statute pattern: Title U.S.C. § Section
STATUTE_PATTERN = re.compile(
    r'(\d+)\s+U\.S\.C\.\s*§\s*(\d+[a-z]?(?:\([a-z0-9]+\))?)',
    re.IGNORECASE
)


def extract_citations(text: str) -> List[Citation]:
    """
    Extract all legal citations from text.

    Args:
        text: Legal text to parse

    Returns:
        List of Citation objects
    """
    citations = []

    # Find case citations
    for match in CASE_PATTERN.finditer(text):
        citations.append(Citation(
            full_text=match.group(0),
            volume=match.group(1),
            reporter=match.group(2).strip(),
            page=match.group(3),
            pin_cite=match.group(4),
            court=match.group(5),
            year=match.group(6),
            citation_type="case"
        ))

    # Find statute citations
    for match in STATUTE_PATTERN.finditer(text):
        citations.append(Citation(
            full_text=match.group(0),
            volume=match.group(1),  # Title
            reporter="U.S.C.",
            page=match.group(2),    # Section
            citation_type="statute"
        ))

    return citations


def normalize_citation(citation: Citation) -> str:
    """
    Convert citation to standard Bluebook format.

    Args:
        citation: Parsed Citation object

    Returns:
        Normalized citation string
    """
    if citation.citation_type == "case":
        result = f"{citation.volume} {citation.reporter} {citation.page}"
        if citation.pin_cite:
            result += f", {citation.pin_cite}"
        result += f" ({citation.court} {citation.year})"
        return result

    elif citation.citation_type == "statute":
        return f"{citation.volume} U.S.C. § {citation.page}"

    return citation.full_text


# Example usage
if __name__ == "__main__":
    sample_text = """
    In Brown v. Board of Education, 347 U.S. 483 (1954), the Supreme Court
    held that segregation was unconstitutional. This was later affirmed in
    Cooper v. Aaron, 358 U.S. 1, 17 (1958). See also 42 U.S.C. § 1983 for
    civil rights actions.
    """

    citations = extract_citations(sample_text)
    for cit in citations:
        print(f"Found: {cit.full_text}")
        print(f"  Type: {cit.citation_type}")
        print(f"  Normalized: {normalize_citation(cit)}")
        print()
