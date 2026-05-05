"""
Counterfactual Generator — Creates demographic variations of input data.

Supports four dimensions:
  - Gender: pronoun/name swaps (male ↔ female)
  - Caste/Name: high-caste ↔ low-caste Indian name swaps
  - Language: English ↔ Hindi/Tamil text markers
  - Region: North ↔ South Indian location swaps
"""
import pandas as pd
import numpy as np
import re
import itertools
from copy import deepcopy


# ── Name dictionaries ──────────────────────────────────────────────────

MALE_NAMES = [
    "Raj", "Arjun", "Vikram", "Rahul", "Amit", "Suresh", "Ramesh",
    "Anil", "Deepak", "Mohan", "Sanjay", "Rohit", "Ajay", "Kiran",
    "Manoj", "Nitin", "Pankaj", "Sachin", "Vivek", "Ashok",
]

FEMALE_NAMES = [
    "Priya", "Anita", "Sunita", "Kavita", "Neha", "Pooja", "Ritu",
    "Meera", "Lakshmi", "Geeta", "Sonal", "Anjali", "Divya", "Sneha",
    "Nisha", "Rani", "Sapna", "Swati", "Rekha", "Jyoti",
]

HIGH_CASTE_SURNAMES = [
    "Sharma", "Iyer", "Nair", "Reddy", "Rao", "Gupta", "Joshi",
    "Pandey", "Trivedi", "Mukherjee", "Chatterjee", "Bhat", "Kaul",
    "Deshpande", "Kulkarni",
]

LOW_CASTE_SURNAMES = [
    "Paswan", "Chamar", "Valmiki", "Dhobi", "Khatik", "Musahar",
    "Jatav", "Raidas", "Madiga", "Paraiah", "Mahar", "Mang",
    "Hela", "Dom", "Bhangi",
]

NORTH_LOCATIONS = [
    "Delhi", "Mumbai", "Lucknow", "Jaipur", "Chandigarh", "Patna",
    "Bhopal", "Ahmedabad", "Kolkata", "Varanasi", "Agra", "Kanpur",
]

SOUTH_LOCATIONS = [
    "Chennai", "Bangalore", "Hyderabad", "Kochi", "Coimbatore",
    "Thiruvananthapuram", "Madurai", "Visakhapatnam", "Mysore",
    "Mangalore", "Tirupati", "Vijayawada",
]

GENDER_PRONOUN_MAP = {
    "he": "she", "she": "he",
    "him": "her", "her": "him",
    "his": "hers", "hers": "his",
    "himself": "herself", "herself": "himself",
    "mr": "ms", "ms": "mr",
    "mr.": "ms.", "ms.": "mr.",
    "male": "female", "female": "male",
    "man": "woman", "woman": "man",
    "boy": "girl", "girl": "boy",
    "father": "mother", "mother": "father",
    "husband": "wife", "wife": "husband",
    "son": "daughter", "daughter": "son",
    "brother": "sister", "sister": "brother",
}


def _swap_gender_text(text: str) -> str:
    """Swap gender-specific words in text."""
    if not isinstance(text, str):
        return text
    words = text.split()
    swapped = []
    for word in words:
        lower = word.lower()
        if lower in GENDER_PRONOUN_MAP:
            replacement = GENDER_PRONOUN_MAP[lower]
            # Preserve original casing
            if word[0].isupper():
                replacement = replacement.capitalize()
            swapped.append(replacement)
        else:
            swapped.append(word)
    return " ".join(swapped)


def _swap_gender_name(name: str) -> str:
    """Swap a name to opposite gender."""
    if not isinstance(name, str):
        return name
    parts = name.strip().split()
    first_name = parts[0] if parts else name

    if first_name in MALE_NAMES:
        idx = MALE_NAMES.index(first_name)
        parts[0] = FEMALE_NAMES[idx % len(FEMALE_NAMES)]
    elif first_name in FEMALE_NAMES:
        idx = FEMALE_NAMES.index(first_name)
        parts[0] = MALE_NAMES[idx % len(MALE_NAMES)]
    else:
        # Unknown name — randomly assign opposite
        rng = np.random.RandomState(hash(first_name) % 2**31)
        parts[0] = rng.choice(FEMALE_NAMES) if rng.random() > 0.5 else rng.choice(MALE_NAMES)

    return " ".join(parts)


def _swap_caste_surname(name: str) -> str:
    """Swap surname between high-caste and low-caste."""
    if not isinstance(name, str):
        return name
    parts = name.strip().split()
    if len(parts) < 2:
        # Add a surname
        rng = np.random.RandomState(hash(name) % 2**31)
        return name + " " + rng.choice(LOW_CASTE_SURNAMES)

    surname = parts[-1]
    if surname in HIGH_CASTE_SURNAMES:
        idx = HIGH_CASTE_SURNAMES.index(surname)
        parts[-1] = LOW_CASTE_SURNAMES[idx % len(LOW_CASTE_SURNAMES)]
    elif surname in LOW_CASTE_SURNAMES:
        idx = LOW_CASTE_SURNAMES.index(surname)
        parts[-1] = HIGH_CASTE_SURNAMES[idx % len(HIGH_CASTE_SURNAMES)]
    else:
        rng = np.random.RandomState(hash(surname) % 2**31)
        parts[-1] = rng.choice(LOW_CASTE_SURNAMES)

    return " ".join(parts)


def _swap_region(text: str) -> str:
    """Swap North ↔ South Indian location references."""
    if not isinstance(text, str):
        return text
    for i, loc in enumerate(NORTH_LOCATIONS):
        if loc.lower() in text.lower():
            replacement = SOUTH_LOCATIONS[i % len(SOUTH_LOCATIONS)]
            text = re.sub(re.escape(loc), replacement, text, flags=re.IGNORECASE)
            break
    for i, loc in enumerate(SOUTH_LOCATIONS):
        if loc.lower() in text.lower():
            replacement = NORTH_LOCATIONS[i % len(NORTH_LOCATIONS)]
            text = re.sub(re.escape(loc), replacement, text, flags=re.IGNORECASE)
            break
    return text


def _swap_gender_value(value: str) -> str:
    """Swap a gender column value (Male/Female/M/F)."""
    if not isinstance(value, str):
        return value
    v = value.strip().lower()
    mapping = {"male": "Female", "female": "Male", "m": "F", "f": "M"}
    return mapping.get(v, value)


def _detect_text_columns(df: pd.DataFrame) -> list[str]:
    """Find columns likely to contain text/names."""
    text_cols = []
    for col in df.columns:
        if df[col].dtype == object:
            text_cols.append(col)
    return text_cols


def _detect_name_column(df: pd.DataFrame) -> str | None:
    """Find the most likely name column."""
    for col in df.columns:
        if any(kw in col.lower() for kw in ["name", "applicant", "person", "candidate"]):
            return col
    return None


def _detect_gender_column(df: pd.DataFrame) -> str | None:
    """Find the most likely gender column."""
    for col in df.columns:
        if any(kw in col.lower() for kw in ["gender", "sex"]):
            return col
    return None


def _detect_region_column(df: pd.DataFrame) -> str | None:
    """Find the most likely region/location column."""
    for col in df.columns:
        if any(kw in col.lower() for kw in ["region", "location", "city", "state", "area", "place"]):
            return col
    return None


def generate_counterfactuals(
    df: pd.DataFrame,
    dimensions: dict,
    strategy: str = "systematic",
) -> pd.DataFrame:
    """
    Generate counterfactual variations of the input dataset.

    Args:
        df: Original DataFrame
        dimensions: Dict of booleans, e.g. {"gender": True, "caste": True, ...}
        strategy: "systematic" (one at a time), "random", or "exhaustive"

    Returns:
        DataFrame with columns:
            original_index, dimension, original_<col>, counterfactual_<col>, ...
            plus all original data columns
    """
    results = []
    active_dims = [k for k, v in dimensions.items() if v]

    name_col = _detect_name_column(df)
    gender_col = _detect_gender_column(df)
    region_col = _detect_region_column(df)
    text_cols = _detect_text_columns(df)

    for idx, row in df.iterrows():
        original_data = row.to_dict()

        if strategy == "systematic":
            # Vary one dimension at a time
            for dim in active_dims:
                cf = _create_counterfactual(
                    original_data, dim, name_col, gender_col, region_col, text_cols
                )
                if cf:
                    cf["original_index"] = idx
                    cf["dimension"] = dim
                    results.append(cf)

        elif strategy == "exhaustive":
            # All combinations of active dimensions
            for r in range(1, len(active_dims) + 1):
                for combo in itertools.combinations(active_dims, r):
                    cf_data = deepcopy(original_data)
                    dims_applied = []
                    for dim in combo:
                        cf_single = _create_counterfactual(
                            cf_data, dim, name_col, gender_col, region_col, text_cols
                        )
                        if cf_single:
                            cf_data = cf_single
                            dims_applied.append(dim)
                    if dims_applied:
                        cf_data["original_index"] = idx
                        cf_data["dimension"] = "+".join(dims_applied)
                        results.append(cf_data)

        elif strategy == "random":
            # Random subset of dimensions
            rng = np.random.RandomState(idx)
            num_dims = rng.randint(1, len(active_dims) + 1)
            chosen = rng.choice(active_dims, size=min(num_dims, len(active_dims)), replace=False)
            cf_data = deepcopy(original_data)
            dims_applied = []
            for dim in chosen:
                cf_single = _create_counterfactual(
                    cf_data, dim, name_col, gender_col, region_col, text_cols
                )
                if cf_single:
                    cf_data = cf_single
                    dims_applied.append(dim)
            if dims_applied:
                cf_data["original_index"] = idx
                cf_data["dimension"] = "+".join(dims_applied)
                results.append(cf_data)

    if not results:
        return pd.DataFrame()

    cf_df = pd.DataFrame(results)
    return cf_df


def _create_counterfactual(
    data: dict,
    dimension: str,
    name_col: str | None,
    gender_col: str | None,
    region_col: str | None,
    text_cols: list[str],
) -> dict | None:
    """Create a single counterfactual variant for one dimension."""
    cf = deepcopy(data)

    if dimension == "gender":
        changed = False
        if gender_col and gender_col in cf:
            cf[gender_col] = _swap_gender_value(str(cf[gender_col]))
            changed = True
        if name_col and name_col in cf:
            cf[name_col] = _swap_gender_name(str(cf[name_col]))
            changed = True
        # Swap pronouns in text columns
        for col in text_cols:
            if col != name_col and col != gender_col and col in cf:
                new_val = _swap_gender_text(str(cf[col]))
                if new_val != str(cf[col]):
                    cf[col] = new_val
                    changed = True
        return cf if changed else None

    elif dimension == "caste":
        if name_col and name_col in cf:
            cf[name_col] = _swap_caste_surname(str(cf[name_col]))
            return cf
        return None

    elif dimension == "language":
        # For MVP: add a language indicator marker
        # In production, this would use translation APIs
        for col in text_cols:
            if col in cf and col != name_col:
                cf[col] = str(cf[col]) + " [HI]"  # Mark as Hindi context
                return cf
        return None

    elif dimension == "region":
        if region_col and region_col in cf:
            cf[region_col] = _swap_region(str(cf[region_col]))
            return cf
        # Try text columns
        for col in text_cols:
            if col in cf:
                swapped = _swap_region(str(cf[col]))
                if swapped != str(cf[col]):
                    cf[col] = swapped
                    return cf
        return None

    return None


def preview_counterfactuals(
    df: pd.DataFrame,
    dimensions: dict,
    strategy: str = "systematic",
    max_preview: int = 10,
) -> list[dict]:
    """
    Generate a small preview of counterfactual pairs.
    Returns list of {original: {...}, counterfactual: {...}, dimension: str}
    """
    preview_df = df.head(min(5, len(df)))
    cf_df = generate_counterfactuals(preview_df, dimensions, strategy)

    if cf_df.empty:
        return []

    previews = []
    for _, cf_row in cf_df.head(max_preview).iterrows():
        orig_idx = int(cf_row.get("original_index", 0))
        orig_row = df.iloc[orig_idx].to_dict() if orig_idx < len(df) else {}
        previews.append({
            "original": {k: str(v) for k, v in orig_row.items()},
            "counterfactual": {
                k: str(v) for k, v in cf_row.to_dict().items()
                if k not in ("original_index", "dimension")
            },
            "dimension": cf_row.get("dimension", "unknown"),
        })

    return previews
