import math

def _round_price(price: float) -> float:
    """
    Rounds price according to IDX (Indonesia Stock Exchange) tick size rules.
    - >= 5000: tick size 25
    - 2000 - 4990: tick size 10
    - 500 - 1995: tick size 5
    - < 500: tick size 1
    """
    if price >= 5000:
        return round(price / 25) * 25
    elif price >= 2000:
        return round(price / 10) * 10
    elif price >= 500:
        return round(price / 5) * 5
    else:
        return round(price)

def calibrated_probability_from_score(score: float) -> float:
    """
    Converts a 0-100 score into a calibrated win probability percentage.
    Uses a non-linear mapping.
    """
    if score >= 90:
        return 72.0 + (score - 90) * 0.3  # Max ~75%
    elif score >= 80:
        return 65.0 + (score - 80) * 0.7  # 65-72%
    elif score >= 70:
        return 55.0 + (score - 70) * 1.0  # 55-65%
    elif score >= 60:
        return 45.0 + (score - 60) * 1.0  # 45-55%
    else:
        return max(10.0, score * 0.75)

def clamp(value: float, lower: float = -1.0, upper: float = 1.0) -> float:
    """Helper function to clamp values."""
    return max(lower, min(upper, value))
