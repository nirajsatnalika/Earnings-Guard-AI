"""Beneish M-Score model — combines the 8 components into the final score.

The Beneish M-Score is a probabilistic model that detects earnings
manipulation. An M-Score above -1.78 indicates a likely manipulator.

Official formula (Beneish 1999):

  M = -4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI
      + 0.115×DEPI - 0.172×SGAI + 4.679×TATA - 0.327×LVGI
"""

from __future__ import annotations

MANIPULATOR_THRESHOLD = -1.78

COEFFICIENTS: dict[str, float] = {
    "DSRI": 0.92,
    "GMI": 0.528,
    "AQI": 0.404,
    "SGI": 0.892,
    "DEPI": 0.115,
    "SGAI": -0.172,
    "TATA": 4.679,
    "LVGI": -0.327,
}

INTERCEPT = -4.84

M_SCORE_FORMULA = (
    "M = -4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI "
    "+ 0.115×DEPI - 0.172×SGAI + 4.679×TATA - 0.327×LVGI"
)


def compute_m_score(component_values: dict[str, float]) -> float | None:
    """Combine the 8 component values into the Beneish M-Score.

    Returns None if any component value is missing.
    """
    total = INTERCEPT
    for name, coef in COEFFICIENTS.items():
        value = component_values.get(name)
        if value is None:
            return None
        total += coef * value
    return total


def interpret_m_score(m_score: float | None) -> str:
    """Generate a plain-language interpretation of the M-Score."""
    if m_score is None:
        return "M-Score could not be computed — one or more components are missing."

    is_manipulator = m_score > MANIPULATOR_THRESHOLD
    if is_manipulator:
        return (
            f"M-Score of {m_score:.4f} is above the manipulator threshold of {MANIPULATOR_THRESHOLD}. "
            "The company shows characteristics associated with earnings manipulation."
        )
    return (
        f"M-Score of {m_score:.4f} is below the manipulator threshold of {MANIPULATOR_THRESHOLD}. "
        "The company does not show strong characteristics of earnings manipulation."
    )
