WEIGHTS = {
    "security": 0.30,
    "compliance": 0.20,
    "operational": 0.15,
    "financial": 0.15,
    "access": 0.20,
}

TIERS = [
    ("CRITICAL", 81, 100),
    ("HIGH", 61, 80),
    ("MEDIUM", 41, 60),
    ("LOW", 21, 40),
    ("MINIMAL", 0, 20),
]

ENTITY_TYPE_WEIGHTS = {
    "VENDOR": {"security": 0.30, "compliance": 0.20, "operational": 0.15, "financial": 0.20, "access": 0.15},
    "USER": {"security": 0.35, "compliance": 0.10, "operational": 0.10, "financial": 0.05, "access": 0.40},
    "SYSTEM": {"security": 0.40, "compliance": 0.20, "operational": 0.15, "financial": 0.05, "access": 0.20},
    "CONTROL": {"security": 0.25, "compliance": 0.40, "operational": 0.15, "financial": 0.05, "access": 0.15},
    "CONFIG": {"security": 0.45, "compliance": 0.25, "operational": 0.15, "financial": 0.05, "access": 0.10},
    "EVIDENCE": {"security": 0.10, "compliance": 0.55, "operational": 0.15, "financial": 0.05, "access": 0.15},
    "EXCEPTION": {"security": 0.30, "compliance": 0.30, "operational": 0.20, "financial": 0.10, "access": 0.10},
    "DOCUMENT": {"security": 0.15, "compliance": 0.35, "operational": 0.20, "financial": 0.20, "access": 0.10},
}


def calculate_weighted_score(scores: dict, entity_type: str = "VENDOR") -> tuple[float, str]:
    weights = ENTITY_TYPE_WEIGHTS.get(entity_type.upper(), WEIGHTS)
    overall = sum(float(scores.get(dim, 0)) * weights.get(dim, 0) for dim in weights)
    overall = round(min(overall, 100), 2)

    tier = "MINIMAL"
    for t, low, high in TIERS:
        if low <= overall <= high:
            tier = t
            break

    return overall, tier
