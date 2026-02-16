"""
Legal Tokenization Module for QueryLex

Implements NUPunkt-style legal tokenization that properly handles
legal abbreviations, citations, and domain-specific patterns.
"""

import re
from typing import List, Optional, Set


class LegalTokenizer:
    """
    Legal-domain tokenizer that properly handles legal abbreviations,
    citations, and specialized terminology.

    Based on NUPunkt principles - prevents sentence splitting on legal
    abbreviations like "Art.", "Reg.", "Corp.", "Inc.", etc.
    """

    # Legal abbreviations that should NOT end a sentence
    LEGAL_ABBREVIATIONS: Set[str] = {
        # Article/Section references
        'art', 'arts', 'sec', 'secs', 'sect', 'par', 'para', 'paras',
        'ch', 'chs', 'chap', 'chaps', 'pt', 'pts', 'div', 'divs',
        'cl', 'cls', 'subpar', 'subpars', 'subsec', 'subsecs',

        # Legal titles and entities
        'corp', 'inc', 'ltd', 'llc', 'llp', 'plc', 'co', 'cos',
        'assn', 'assoc', 'bros', 'dept', 'div', 'est',

        # Court and legal terms
        'ct', 'cts', 'cir', 'dist', 'app', 'supp', 'rev', 'aff',
        'j', 'jj', 'cj', 'aj', 'pj', 'sjj',
        'v', 'vs', 'no', 'nos', 'et', 'al', 'seq',

        # Regulatory bodies
        'reg', 'regs', 'stat', 'stats', 'pub', 'priv',
        'fed', 'nat', 'int', 'intl',

        # Legal document types
        'aff', 'cert', 'decl', 'def', 'defs', 'ex', 'exs', 'exh',
        'mot', 'op', 'ops', 'pet', 'pl', 'pls', 'resp', 'stip',

        # Common abbreviations
        'mr', 'mrs', 'ms', 'dr', 'prof', 'hon', 'esq',
        'jr', 'sr', 'ii', 'iii', 'iv',
        'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec',

        # EU/International legal abbreviations
        'eu', 'ec', 'ecj', 'cjeu', 'wto', 'un', 'echr', 'eur',
        'tfeu', 'teu', 'gdpr', 'sfdr',

        # French legal abbreviations
        'c', 'civ', 'com', 'crim', 'soc', 'ass', 'plén',
        'cass', 'req', 'bull', 'jcp', 'gaz', 'pal',

        # German legal abbreviations
        'bgb', 'hgb', 'stgb', 'zpo', 'gg', 'bgbl',
        'bgh', 'bverfg', 'olg', 'lg', 'ag',

        # Misc legal
        'amend', 'appx', 'auth', 'bankr', 'bk', 'bl', 'const',
        'cong', 'ctr', 'ed', 'eds', 'eg', 'esp', 'etc', 'fig', 'figs',
        'ibid', 'ie', 'infra', 'inst', 'mar', 'misc', 'op', 'orig',
        'passim', 'perm', 'prac', 'prob', 'proc', 'prop', 'pub',
        'pty', 'qtd', 'ser', 'sess', 'spec', 'supr', 'tit', 'trans',
        'univ', 'viz', 'vol', 'vols'
    }

    # Patterns for legal citations
    CITATION_PATTERNS = [
        # US Case citations: 123 F.3d 456, 789 U.S. 123
        r'\d+\s+[A-Z][a-z]*\.?\s*\d*[a-z]*\.?\s+\d+',
        # European citations: Case C-123/45
        r'[Cc]ase\s+[A-Z]-\d+/\d+',
        # Section/Article references: § 123, Art. 5
        r'[§Aa]rt\.?\s*\d+',
        r'[Ss]ec\.?\s*\d+',
    ]

    def __init__(self, enabled: bool = True):
        """
        Initialize the legal tokenizer.

        Args:
            enabled: Whether legal tokenization is enabled
        """
        self.enabled = enabled
        self._abbrev_pattern = self._build_abbrev_pattern()

    def _build_abbrev_pattern(self) -> re.Pattern:
        """Build regex pattern for detecting legal abbreviations."""
        # Sort by length (longest first) to match longest abbreviations first
        sorted_abbrevs = sorted(self.LEGAL_ABBREVIATIONS, key=len, reverse=True)
        # Build pattern that matches abbreviation followed by period
        pattern = r'\b(' + '|'.join(re.escape(a) for a in sorted_abbrevs) + r')\.'
        return re.compile(pattern, re.IGNORECASE)

    def protect_abbreviations(self, text: str) -> str:
        """
        Protect legal abbreviations from sentence splitting.

        Replaces periods after abbreviations with a placeholder that
        won't be treated as sentence boundaries.
        """
        if not self.enabled:
            return text

        # Replace abbreviation periods with placeholder
        protected = self._abbrev_pattern.sub(r'\1<ABBREV_DOT>', text)

        return protected

    def restore_abbreviations(self, text: str) -> str:
        """Restore protected abbreviations to their original form."""
        return text.replace('<ABBREV_DOT>', '.')

    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while respecting legal abbreviations.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        if not text:
            return []

        if not self.enabled:
            # Simple sentence splitting
            return self._simple_sentence_split(text)

        # Protect abbreviations
        protected = self.protect_abbreviations(text)

        # Split on sentence boundaries
        sentences = self._simple_sentence_split(protected)

        # Restore abbreviations
        restored = [self.restore_abbreviations(s) for s in sentences]

        return [s.strip() for s in restored if s.strip()]

    def _simple_sentence_split(self, text: str) -> List[str]:
        """Basic sentence splitting on common boundaries."""
        # Split on period, exclamation, question mark followed by space and capital
        # or end of string
        pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def tokenize_words(self, text: str) -> List[str]:
        """
        Tokenize text into words while preserving legal terms.

        Args:
            text: Input text

        Returns:
            List of word tokens
        """
        if not text:
            return []

        if not self.enabled:
            # Simple word tokenization
            return re.findall(r'\b\w+\b', text)

        # Protect legal terms with periods (e.g., "Inc.", "Corp.")
        protected = self.protect_abbreviations(text)

        # Tokenize
        tokens = re.findall(r'\b[\w<>_]+\b', protected)

        # Restore and clean
        restored = []
        for token in tokens:
            clean = self.restore_abbreviations(token)
            if clean:
                restored.append(clean)

        return restored

    def normalize_legal_text(self, text: str) -> str:
        """
        Normalize legal text for better processing.

        - Normalizes whitespace
        - Preserves legal citations
        - Handles common legal formatting issues

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        if not text:
            return ""

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Normalize common legal variations
        replacements = [
            (r'\bsection\s+', 'Section '),
            (r'\barticle\s+', 'Article '),
            (r'\bparagraph\s+', 'Paragraph '),
            (r'\bclause\s+', 'Clause '),
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text.strip()


def preprocess_legal_query(query: str, enabled: bool = True) -> str:
    """
    Preprocess a legal query for better retrieval.

    Args:
        query: User's search query
        enabled: Whether legal tokenization is enabled

    Returns:
        Preprocessed query
    """
    tokenizer = LegalTokenizer(enabled=enabled)
    return tokenizer.normalize_legal_text(query)


def preprocess_legal_document(text: str, enabled: bool = True) -> str:
    """
    Preprocess a legal document for chunking.

    Args:
        text: Document text
        enabled: Whether legal tokenization is enabled

    Returns:
        Preprocessed text ready for chunking
    """
    tokenizer = LegalTokenizer(enabled=enabled)
    return tokenizer.normalize_legal_text(text)


def get_legal_sentences(text: str, enabled: bool = True) -> List[str]:
    """
    Split legal text into sentences respecting abbreviations.

    Args:
        text: Input text
        enabled: Whether legal tokenization is enabled

    Returns:
        List of sentences
    """
    tokenizer = LegalTokenizer(enabled=enabled)
    return tokenizer.tokenize_sentences(text)


# For testing
if __name__ == "__main__":
    test_texts = [
        "Art. 101 TFEU prohibits anticompetitive agreements. See Corp. v. Inc., 123 F.3d 456.",
        "The SEC issued Reg. D under the Securities Act. Prof. Smith analyzed the ruling.",
        "Pursuant to Art. 5 para. 1 lit. a of the GDPR, processing shall be lawful.",
        "John Doe Jr. filed a motion. Dr. Smith testified as expert witness.",
    ]

    tokenizer = LegalTokenizer(enabled=True)

    print("Legal Tokenizer Test\n" + "=" * 50)

    for text in test_texts:
        print(f"\nOriginal: {text}")
        sentences = tokenizer.tokenize_sentences(text)
        print(f"Sentences ({len(sentences)}):")
        for i, s in enumerate(sentences, 1):
            print(f"  {i}. {s}")
