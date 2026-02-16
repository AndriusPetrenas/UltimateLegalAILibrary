"""
Legal Source Filter Configuration

Maps UI filter keys to metadata query conditions for filtering legal documents
in vector search. Used by the document processor when querying legal source
collections (Legifrance, JUDILIBRE, EUR-Lex, HUDOC, etc.).

The resolve_filters() function translates user-selected filter keys into
structured conditions for the Supabase RPC functions. Each condition specifies
source_api, doc_type, and/or jurisdiction_detail. Documents match if ANY
condition is satisfied (OR across keys), with AND within each condition.
"""

# UI filter key -> metadata query mapping
FILTER_KEY_MAP = {
    # French legislative sources (Legifrance)
    "decrets": {
        "source_api": "legifrance",
        "doc_type": "decret",
    },
    "lois": {
        "source_api": "legifrance",
        "doc_type": "loi",
    },
    "reglements": {
        "source_api": "legifrance",
        "doc_type": "reglement",
    },
    "codes": {
        "source_api": "legifrance",
        "doc_type": "code_article",
    },
    # French judicial courts (JUDILIBRE)
    "cour_de_cassation": {
        "source_api": "judilibre",
        "jurisdiction_detail": "cour_cassation",
    },
    "cours_appel": {
        "source_api": "judilibre",
        "jurisdiction_detail": "cour_appel",
    },
    "tribunaux_judiciaires": {
        "source_api": "judilibre",
        "jurisdiction_detail": "tribunal_judiciaire",
    },
    # French administrative courts (Legifrance JADE/CETA)
    "conseil_etat": {
        "source_api": "legifrance",
        "jurisdiction_detail": "conseil_etat",
    },
    "cours_administratives_appel": {
        "source_api": "legifrance",
        "jurisdiction_detail": "cour_administrative_appel",
    },
    "tribunaux_administratifs": {
        "source_api": "legifrance",
        "jurisdiction_detail": "tribunal_administratif",
    },
    # Constitutional texts
    "constitution_1946": {
        "doc_type": "texte_constitutionnel",
        "text_id": "CONSTITUTION_1946",
    },
    "constitution_1848": {
        "doc_type": "texte_constitutionnel",
        "text_id": "CONSTITUTION_1848",
    },
    "constitution_1958": {
        "doc_type": "texte_constitutionnel",
        "text_id": "CONSTITUTION_1958",
    },
    # BOFIP / CNIL
    "bofip": {
        "source_api": "bofip",
    },
    "cnil": {
        "source_api": "cnil",
    },
    # EU sources
    "reglements_eu": {
        "source_api": "eurlex",
        "doc_type": "reglement_eu",
    },
    "directives_eu": {
        "source_api": "eurlex",
        "doc_type": "directive_eu",
    },
    "cjue": {
        "source_api": "eurlex",
        "jurisdiction_detail": "cjue",
    },
    "cedh_cour": {
        "source_api": "hudoc",
    },
    "tribunal_fonction_publique": {
        "source_api": "eurlex",
        "jurisdiction_detail": "tribunal_fonction_publique",
    },
    "tue": {
        "source_api": "eurlex",
        "jurisdiction_detail": "tue",
    },
    "cedh_traite": {
        "doc_type": "traite",
        "treaty_name": "CEDH",
    },
}

ALL_FILTER_KEYS = list(FILTER_KEY_MAP.keys())
TOTAL_SOURCE_COUNT = len(ALL_FILTER_KEYS)


def resolve_filters(active_keys):
    """Translate a list of active UI filter keys into per-key OR conditions.

    Each UI filter key maps to a condition object with source_api, doc_type,
    and/or jurisdiction_detail. The SQL function uses OR across conditions
    (a document matches if ANY condition matches), with AND within each condition.

    Example:
        resolve_filters(["codes", "cedh_cour"])
        # Returns:
        # [
        #     {"source_api": "legifrance", "doc_type": "code_article"},
        #     {"source_api": "hudoc"}
        # ]

    Args:
        active_keys: List of filter keys selected by the user

    Returns:
        None if all filters active (no filtering needed), or a list of
        condition dicts for the match_documents_*_filtered RPC functions.
    """
    if not active_keys:
        return None

    # If all filters are active, no filtering needed
    if set(active_keys) >= set(ALL_FILTER_KEYS):
        return None

    # Build per-key condition objects
    conditions = []
    for key in active_keys:
        mapping = FILTER_KEY_MAP.get(key, {})
        if not mapping:
            continue
        cond = {}
        if "source_api" in mapping:
            cond["source_api"] = mapping["source_api"]
        if "doc_type" in mapping:
            cond["doc_type"] = mapping["doc_type"]
        if "jurisdiction_detail" in mapping:
            cond["jurisdiction_detail"] = mapping["jurisdiction_detail"]
        if cond:
            conditions.append(cond)

    return conditions if conditions else None
