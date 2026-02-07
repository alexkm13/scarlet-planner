"""
Department code to name mapping and search aliases.
Used for resolving queries like "math" -> MA, "computer science" -> CS.
"""

# Flattened code -> name for search text enhancement
# Based on Boston University department abbreviations
DEPT_CODE_TO_NAME: dict[str, str] = {
    "AA": "African American Black Diaspora Studies",
    "AH": "History of Art Architecture",
    "AI": "Asian Studies",
    "AM": "American New England Studies",
    "AN": "Anthropology",
    "AR": "Archaeology",
    "AS": "Astronomy",
    "BB": "Biochemistry Molecular Biology",
    "BI": "Biology",
    "CH": "Chemistry",
    "CI": "Cinema Media Studies",
    "CL": "Classical Studies",
    "CS": "Computer Science",
    "EC": "Economics",
    "EE": "Earth Environment",
    "EN": "English",
    "HI": "History",
    "MA": "Mathematics Statistics",
    "ME": "Middle East North Africa Studies",
    "MU": "Music",
    "NE": "Neuroscience",
    "PH": "Philosophy",
    "PO": "Political Science",
    "PS": "Psychological Brain Sciences",
    "PY": "Physics",
    "RN": "Religion",
    "SO": "Sociology",
    "WR": "Writing",
    "WS": "Women Gender Sexuality Studies",
    "LF": "French",
    "LG": "German",
    "LI": "Italian",
    "LS": "Spanish",
    "LR": "Russian",
    "LY": "Arabic",
    "LC": "Chinese",
    "LJ": "Japanese",
    "LK": "Korean",
    "AC": "Accounting",
    "BA": "Business Administration",
    "BE": "Biomedical Engineering",
    "BF": "Bioinformatics",
    "DS": "Data Science",
    "FT": "Film Television",
    "JO": "Journalism",
}

# Aliases: lowercase search term -> list of department codes
# Include both codes (AH, CS, MA) and full/partial names
DEPT_ALIASES: dict[str, list[str]] = {
    # Common shorthand
    "math": ["MA"],
    "mathematics": ["MA"],
    "stats": ["MA"],
    "statistics": ["MA"],
    "computer": ["CS"],
    "computer science": ["CS"],
    "physics": ["PY"],
    "chemistry": ["CH"],
    "biology": ["BI"],
    "economics": ["EC"],
    "econ": ["EC"],
    "psychology": ["PS"],
    "psych": ["PS"],
    "philosophy": ["PH"],
    "history": ["HI"],
    "english": ["EN"],
    "sociology": ["SO"],
    "anthropology": ["AN"],
    "political": ["PO"],
    "polisci": ["PO"],
    "political science": ["PO"],
    "music": ["MU"],
    "writing": ["WR"],
    "accounting": ["AC"],
    "finance": ["FE"],
}

# Add each code (AH, CS, MA, etc.) and its full name as aliases
for code, name in DEPT_CODE_TO_NAME.items():
    code_key = code.lower()
    if code_key not in DEPT_ALIASES:
        DEPT_ALIASES[code_key] = [code]
    elif code not in DEPT_ALIASES[code_key]:
        DEPT_ALIASES[code_key] = [code] + [c for c in DEPT_ALIASES[code_key] if c != code]
    # Full department name (normalized: lowercase, no & or punctuation)
    name_norm = " ".join(name.replace("&", " ").replace(",", " ").split()).lower()
    if name_norm and name_norm not in DEPT_ALIASES:
        DEPT_ALIASES[name_norm] = [code]
    elif name_norm and code not in DEPT_ALIASES.get(name_norm, []):
        DEPT_ALIASES.setdefault(name_norm, []).insert(0, code)


def get_department_name(code: str) -> str:
    """Return full department name for a code, or the code if unknown."""
    return DEPT_CODE_TO_NAME.get(code.upper(), code)


def resolve_department_query(query: str) -> tuple[list[str], str] | None:
    """
    If the query (or a part of it) is a department alias, return (subject_codes, remaining_query).
    Matches: exact code (AH, CS), exact alias (math, computer science), full name, or name prefix.
    E.g. "math" -> (["MA"], ""), "History of Art" -> (["AH"], ""), "MA" -> (["MA"], "").
    Returns None if no department alias found.
    """
    q = query.strip()
    if not q:
        return None
    q_lower = q.lower()
    # Exact alias or code
    if q_lower in DEPT_ALIASES:
        return (DEPT_ALIASES[q_lower], "")
    if q.upper() in DEPT_CODE_TO_NAME:
        return ([q.upper()], "")
    # Query is prefix of a multi-word department name (e.g. "history of art" matches "history of art architecture")
    # Do NOT match when alias is a short code (ec, cs) - "EC201" and "CS411" are course codes, not dept-only
    best_match: tuple[str, list[str]] | None = None
    for alias_key, codes in DEPT_ALIASES.items():
        if alias_key.startswith(q_lower):
            # Query is prefix of alias - e.g. "history of art" matches "history of art architecture"
            if best_match is None or len(alias_key) > len(best_match[0]):
                best_match = (alias_key, codes)
        elif " " in alias_key and q_lower.startswith(alias_key):
            # Alias is multi-word and query extends it (uncommon)
            if best_match is None or len(alias_key) > len(best_match[0]):
                best_match = (alias_key, codes)
    if best_match:
        return (best_match[1], "")
    # Check first word/token
    parts = q.split()
    if parts:
        first = parts[0].lower()
        if first in DEPT_ALIASES:
            remaining = " ".join(parts[1:]).strip()
            return (DEPT_ALIASES[first], remaining)
        if parts[0].upper() in DEPT_CODE_TO_NAME:
            remaining = " ".join(parts[1:]).strip()
            return ([parts[0].upper()], remaining)
    return None
