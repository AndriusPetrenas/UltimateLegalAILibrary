"""
Metadata Extraction Module for QueryLex

Extracts structured metadata from legal documents using LLM.
Used during document upload to enable metadata-based filtering.

Cost: ~$0.002-0.01 per document (depending on size)
Impact: Enables precise filtering, improves relevance
"""

import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime


# Metadata Extraction Prompts
METADATA_SYSTEM_PROMPT = """You are a legal document analyst. Extract structured metadata from the given document excerpt.

Extract the following fields if present:
1. document_type: Type of document (contract, regulation, case_law, statute, memo, brief, policy, agreement, amendment, etc.)
2. jurisdiction: Legal jurisdiction (e.g., "EU", "US", "UK", "France", "Germany", "International", "California", etc.)
3. date: Most relevant date in ISO format YYYY-MM-DD (document date, effective date, or judgment date)
4. parties: List of main parties involved (companies, individuals, government bodies)
5. practice_area: Legal practice area (antitrust, data_protection, corporate, employment, intellectual_property, tax, environmental, securities, etc.)
6. key_provisions: List of key legal provisions mentioned (e.g., "Article 101 TFEU", "Section 7 Clayton Act", "GDPR Article 6")

Output ONLY valid JSON with these fields. Use null for fields that cannot be determined."""

METADATA_USER_PROMPT_TEMPLATE = """Extract metadata from this legal document excerpt:

Filename: {filename}

--- DOCUMENT EXCERPT ---
{content}
--- END EXCERPT ---

Output only valid JSON with the metadata fields."""


# Document type patterns for fallback detection
DOCUMENT_TYPE_PATTERNS = {
    'contract': [r'\b(agreement|contract|terms|covenant)\b', r'\b(parties?|undersigned)\b.*\b(agree|enter)\b'],
    'regulation': [r'\b(regulation|directive|rule)\b.*\b(no\.?|number)\s*\d+', r'\b(eu|ec|commission)\s+(regulation|directive)\b'],
    'case_law': [r'\b(case|judgment|ruling|decision)\b.*\b(c-\d+|no\.?\s*\d+)', r'\b(court|tribunal|chamber)\b.*\b(held|ruled|decided)\b'],
    'statute': [r'\b(act|code|statute)\b.*\b(section|§)\s*\d+', r'\b(enacted|effective)\b'],
    'memo': [r'\b(memorandum|memo)\b', r'\b(to|from|re|subject)\s*:'],
    'brief': [r'\b(brief|motion|petition)\b', r'\b(plaintiff|defendant|appellant|respondent)\b'],
    'policy': [r'\b(policy|guideline|guidance)\b', r'\b(compliance|procedure)\b'],
}

# Jurisdiction patterns
JURISDICTION_PATTERNS = {
    'EU': [r'\b(european union|eu|tfeu|teu|ec directive|european commission)\b'],
    'US': [r'\b(united states|u\.?s\.?|federal|american)\b', r'\b(circuit|district court)\b'],
    'UK': [r'\b(united kingdom|uk|british|england|wales|scotland)\b'],
    'France': [r'\b(france|french|cour de cassation|tribunal)\b'],
    'Germany': [r'\b(germany|german|bundesgerichtshof|bgb)\b'],
    'International': [r'\b(international|wto|un|treaty|convention)\b'],
}

# Practice area patterns
PRACTICE_AREA_PATTERNS = {
    'antitrust': [r'\b(antitrust|competition|cartel|merger|monopol|dominant position)\b', r'\b(article\s*10[12]|sherman|clayton)\b'],
    'data_protection': [r'\b(gdpr|data protection|privacy|personal data|processing)\b'],
    'corporate': [r'\b(corporate|governance|shareholder|board|director)\b'],
    'employment': [r'\b(employment|labor|worker|employee|termination|dismissal)\b'],
    'intellectual_property': [r'\b(patent|trademark|copyright|ip|intellectual property)\b'],
    'tax': [r'\b(tax|taxation|fiscal|vat|duty)\b'],
    'environmental': [r'\b(environmental|pollution|emission|climate|sustainability)\b'],
    'securities': [r'\b(securities|stock|share|listing|prospectus)\b'],
}


class MetadataExtractor:
    """
    LLM-based metadata extractor for legal documents.

    Extracts structured metadata for filtering and organization.
    """

    def __init__(
        self,
        enabled: bool = True,
        extract_fields: Optional[Dict[str, bool]] = None
    ):
        """
        Initialize metadata extractor.

        Args:
            enabled: Whether extraction is enabled
            extract_fields: Dict of field_name -> enabled (e.g., {'jurisdiction': True})
        """
        self.enabled = enabled
        self.extract_fields = extract_fields or {
            'document_type': True,
            'jurisdiction': True,
            'date': False,
            'parties': False,
            'practice_area': True,
            'key_provisions': False,
        }
        self._client = None
        self.stats = {
            "documents_processed": 0,
            "llm_extractions": 0,
            "fallback_extractions": 0,
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

    def extract(
        self,
        content: str,
        filename: str = "Unknown",
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Extract metadata from document content.

        Args:
            content: Document text content
            filename: Original filename
            use_llm: Whether to use LLM (falls back to heuristics if False)

        Returns:
            Dict of extracted metadata
        """
        import time
        start_time = time.time()

        self.stats["documents_processed"] += 1

        if not self.enabled:
            return self._empty_metadata()

        # Truncate content for LLM
        excerpt = content[:3000] if len(content) > 3000 else content

        metadata = None

        # Try LLM extraction first
        if use_llm:
            try:
                metadata = self._extract_with_llm(excerpt, filename)
                self.stats["llm_extractions"] += 1
            except Exception as e:
                print(f"[MetadataExtractor] LLM extraction failed: {e}")

        # Fall back to heuristics if LLM failed or disabled
        if metadata is None:
            metadata = self._extract_with_heuristics(excerpt, filename)
            self.stats["fallback_extractions"] += 1

        # Filter to only enabled fields
        filtered = {}
        for field, enabled in self.extract_fields.items():
            if enabled and field in metadata:
                filtered[field] = metadata[field]

        elapsed_ms = int((time.time() - start_time) * 1000)
        self.stats["total_time_ms"] += elapsed_ms

        method = f"with {self.client.model}" if use_llm and self._client else "using heuristics"
        print(f"[MetadataExtractor] Extracted metadata {method} ({elapsed_ms}ms): {list(filtered.keys())}")

        return filtered

    def _extract_with_llm(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract metadata using LLM."""
        prompt = METADATA_USER_PROMPT_TEMPLATE.format(
            filename=filename,
            content=content
        )

        response = self.client.complete(
            prompt=prompt,
            system_prompt=METADATA_SYSTEM_PROMPT,
            max_tokens=400,
            temperature=0.1  # Low temperature for consistent extraction
        )

        # Parse JSON response
        return self._parse_llm_response(response)

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into metadata dict."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                metadata = json.loads(json_match.group())
                return self._normalize_metadata(metadata)
        except json.JSONDecodeError:
            pass

        return self._empty_metadata()

    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate metadata fields."""
        normalized = {}

        # Document type - normalize to lowercase
        if metadata.get('document_type'):
            doc_type = str(metadata['document_type']).lower().replace(' ', '_')
            normalized['document_type'] = doc_type

        # Jurisdiction - normalize
        if metadata.get('jurisdiction'):
            jurisdiction = str(metadata['jurisdiction'])
            # Map common variations
            jurisdiction_map = {
                'european union': 'EU',
                'united states': 'US',
                'united kingdom': 'UK',
            }
            normalized['jurisdiction'] = jurisdiction_map.get(jurisdiction.lower(), jurisdiction)

        # Date - validate ISO format
        if metadata.get('date'):
            date_str = str(metadata['date'])
            try:
                # Try to parse and reformat
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    normalized['date'] = date_str[:10]
            except:
                pass

        # Parties - ensure list
        if metadata.get('parties'):
            parties = metadata['parties']
            if isinstance(parties, list):
                normalized['parties'] = [str(p) for p in parties[:10]]  # Limit
            elif isinstance(parties, str):
                normalized['parties'] = [parties]

        # Practice area - normalize
        if metadata.get('practice_area'):
            practice = str(metadata['practice_area']).lower().replace(' ', '_')
            normalized['practice_area'] = practice

        # Key provisions - ensure list
        if metadata.get('key_provisions'):
            provisions = metadata['key_provisions']
            if isinstance(provisions, list):
                normalized['key_provisions'] = [str(p) for p in provisions[:10]]
            elif isinstance(provisions, str):
                normalized['key_provisions'] = [provisions]

        return normalized

    def _extract_with_heuristics(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract metadata using pattern matching (fallback)."""
        content_lower = content.lower()
        metadata = {}

        # Document type
        for doc_type, patterns in DOCUMENT_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    metadata['document_type'] = doc_type
                    break
            if 'document_type' in metadata:
                break

        # Jurisdiction
        for jurisdiction, patterns in JURISDICTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    metadata['jurisdiction'] = jurisdiction
                    break
            if 'jurisdiction' in metadata:
                break

        # Practice area
        for practice, patterns in PRACTICE_AREA_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    metadata['practice_area'] = practice
                    break
            if 'practice_area' in metadata:
                break

        # Date - look for common date patterns
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # ISO format
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    # Try to parse and format
                    groups = match.groups()
                    if len(groups) == 3 and groups[0].isdigit() and groups[2].isdigit():
                        metadata['date'] = f"{groups[0]}-{groups[1]}-{groups[2]}"
                    break
                except:
                    pass

        return metadata

    def _empty_metadata(self) -> Dict[str, Any]:
        """Return empty metadata structure."""
        return {}

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        if self._client:
            stats["llm_stats"] = self.client.get_stats()
        return stats


def extract_document_metadata(
    content: str,
    filename: str = "Unknown",
    enabled: bool = True,
    extract_fields: Optional[Dict[str, bool]] = None,
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to extract metadata from a document.

    Args:
        content: Document text
        filename: Original filename
        enabled: Whether extraction is enabled
        extract_fields: Which fields to extract
        use_llm: Whether to use LLM

    Returns:
        Dict of extracted metadata
    """
    extractor = MetadataExtractor(enabled=enabled, extract_fields=extract_fields)
    return extractor.extract(content, filename, use_llm)


# For testing
if __name__ == "__main__":
    print("Testing Metadata Extractor...")

    test_docs = [
        {
            "filename": "eu_merger_regulation.pdf",
            "content": """COUNCIL REGULATION (EC) No 139/2004 of 20 January 2004
            on the control of concentrations between undertakings (the EC Merger Regulation)

            THE COUNCIL OF THE EUROPEAN UNION,

            Having regard to the Treaty establishing the European Community, and in particular
            Articles 83 and 308 thereof,

            Article 1 - Scope
            1. This Regulation shall apply to all concentrations with a Community dimension
            as defined in this Article.

            Article 2 - Appraisal of concentrations
            1. Concentrations within the scope of this Regulation shall be appraised in
            accordance with the objectives of this Regulation and the following provisions
            with a view to establishing whether or not they are compatible with the common market."""
        },
        {
            "filename": "data_processing_agreement.pdf",
            "content": """DATA PROCESSING AGREEMENT

            This Data Processing Agreement ("Agreement") is entered into as of January 15, 2024
            by and between:

            Company A ("Data Controller")
            and
            Company B ("Data Processor")

            Whereas the Controller wishes to engage the Processor to process Personal Data
            in accordance with the General Data Protection Regulation (GDPR) and applicable
            data protection laws.

            Article 6 of the GDPR provides the lawful bases for processing personal data."""
        },
    ]

    try:
        extractor = MetadataExtractor(
            enabled=True,
            extract_fields={
                'document_type': True,
                'jurisdiction': True,
                'date': True,
                'parties': True,
                'practice_area': True,
            }
        )

        for doc in test_docs:
            print(f"\n{'='*60}")
            print(f"Filename: {doc['filename']}")

            metadata = extractor.extract(doc['content'], doc['filename'])

            print(f"Extracted metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")

        print(f"\n{'='*60}")
        print(f"Stats: {extractor.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
