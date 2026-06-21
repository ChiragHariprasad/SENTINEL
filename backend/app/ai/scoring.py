WEIGHTS = {
    "security": 0.35,
    "data_access": 0.25,
    "compliance": 0.15,
    "financial": 0.15,
    "contract": 0.10,
}

TIERS = [
    ("RED", 71, 100),
    ("YELLOW", 41, 70),
    ("GREEN", 0, 40),
]


def calculate_weighted_score(scores: dict) -> tuple[float, str]:
    overall = sum(float(scores.get(dim, 0)) * WEIGHTS.get(dim, 0) for dim in WEIGHTS)
    overall = round(min(overall, 100), 2)

    tier = "GREEN"
    for t, low, high in TIERS:
        if low <= overall <= high:
            tier = t
            break

    return overall, tier
