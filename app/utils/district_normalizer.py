import re
from typing import Optional, Tuple
from app import db
from app.models.district import District

# Canonical mappings and common aliases for Tamil Nadu districts
DISTRICT_ALIASES = {
    # Kanyakumari variations
    "kanniyakumari": "Kanyakumari",
    "kanyakumari": "Kanyakumari",
    "kanyakumari district": "Kanyakumari",
    "kanniyakumari district": "Kanyakumari",

    # The Nilgiris variations
    "nilgiris": "The Nilgiris",
    "the nilgiris": "The Nilgiris",
    "the nilgiris district": "The Nilgiris",
    "nilgiri": "The Nilgiris",
    "ooty": "The Nilgiris",

    # Kancheepuram variations
    "kanchipuram": "Kancheepuram",
    "kancheepuram": "Kancheepuram",
    "kancheepuram district": "Kancheepuram",

    # Viluppuram variations
    "villupuram": "Viluppuram",
    "viluppuram": "Viluppuram",
    "viluppuram district": "Viluppuram",

    # Tiruchirappalli variations
    "trichy": "Tiruchirappalli",
    "tiruchirappalli": "Tiruchirappalli",
    "tiruchirapalli": "Tiruchirappalli",
    "tiruchirappalli district": "Tiruchirappalli",

    # Thoothukudi variations
    "tuticorin": "Thoothukudi",
    "thoothukudi": "Thoothukudi",
    "thoothukudi district": "Thoothukudi",

    # Tiruvarur variations
    "thiruvarur": "Tiruvarur",
    "tiruvarur": "Tiruvarur",
    "tiruvarur district": "Tiruvarur",

    # Tirupathur variations
    "tirupattur": "Tirupathur",
    "tirupathur": "Tirupathur",
    "tirupathur district": "Tirupathur",

    # Tirunelveli variations
    "nellai": "Tirunelveli",
    "tirunelveli": "Tirunelveli",
    "tirunelveli district": "Tirunelveli",

    # Pudukkottai variations
    "pudukottai": "Pudukkottai",
    "pudukkottai": "Pudukkottai",
    "pudukkottai district": "Pudukkottai",

    # Thiruvallur variations
    "thiruvallur": "Tiruvallur",
    "tiruvallur": "Tiruvallur",
    "thiruvallur district": "Tiruvallur",
    "tiruvallur district": "Tiruvallur",

    # Thanjavur variations
    "thanjavur": "Thanjavur",
    "tanjore": "Thanjavur",
    "thanjavur district": "Thanjavur",

    # Sivaganga variations
    "sivagangai": "Sivaganga",
    "sivaganga": "Sivaganga",
    "sivaganga district": "Sivaganga",
}


def normalize_district_name(input_str: Optional[str]) -> Optional[str]:
    """
    Normalizes any Tamil Nadu district name string to its canonical spelling.
    Strips 'District' suffixes, normalizes whitespace and casing, and maps known aliases.
    """
    if not input_str:
        return None

    cleaned = input_str.strip()
    if not cleaned or cleaned.lower() in ('all', 'any'):
        return None

    # Remove trailing 'district' or 'dt'
    lower = cleaned.lower()
    lower = re.sub(r'\s+district$', '', lower)
    lower = re.sub(r'\s+dt\.?$', '', lower)
    lower = lower.strip()

    # Check alias map first
    if lower in DISTRICT_ALIASES:
        return DISTRICT_ALIASES[lower]

    return cleaned.title()


def resolve_district_entity(name_or_id: any) -> Optional[District]:
    """
    Resolves a District model instance from either an integer ID or a district name/alias string.
    """
    if not name_or_id:
        return None

    # 1. Numeric ID check
    if isinstance(name_or_id, int):
        return db.session.get(District, name_or_id)

    str_val = str(name_or_id).strip()
    if str_val.isdigit():
        dist = db.session.get(District, int(str_val))
        if dist:
            return dist

    # 2. Normalized name check
    canonical_name = normalize_district_name(str_val)
    if not canonical_name:
        return None

    dist = District.query.filter(District.name.ilike(canonical_name)).first()
    if dist:
        return dist

    # 3. Fuzzy search fallback in District table
    return District.query.filter(District.name.ilike(f"%{canonical_name}%")).first()
