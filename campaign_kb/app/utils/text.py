# PURPOSE: Text normalization and keyword extraction helpers.
# DEPENDENCIES: re, collections
# MODIFICATION NOTES: MVP text utilities for ingest and merge.

import re
from collections import Counter


_STOP_WORDS = {
    "the", "and", "or", "to", "of", "in", "on", "a", "an", "for", "with", "is",
    "are", "was", "were", "be", "as", "by", "at", "from", "that", "this", "it",
    "into", "their", "they", "them", "we", "our", "you", "your", "not", "but",
    "if", "then", "than", "also", "can", "could", "would", "should", "may",
}


def normalize_text(text: str) -> str:
    # PURPOSE: Normalize text for consistent storage and search.
    # DEPENDENCIES: re
    # MODIFICATION NOTES: MVP normalization for whitespace and control chars.
    cleaned = re.sub(r"\\s+", " ", text.replace("\u00a0", " ")).strip()
    return cleaned


def extract_keywords(text: str, max_terms: int = 25) -> list[str]:
    # PURPOSE: Extract simple keyword list from text for merge citations.
    # DEPENDENCIES: collections.Counter, re
    # MODIFICATION NOTES: MVP keyword extraction with stop-word filtering.
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text.lower())
    filtered = [word for word in words if word not in _STOP_WORDS]
    counts = Counter(filtered)
    return [term for term, _count in counts.most_common(max_terms)]
