"""Funnel stages in order and parsing of stage names."""

STAGES = ("Lead", "Contacted", "Intro session", "Onboarded")

_INDEX = {name.lower(): i for i, name in enumerate(STAGES)}


def parse_stage(text: object) -> int | None:
    """Return the stage index for a name, ignoring case and extra spaces, or None if unknown."""
    if text is None:
        return None
    return _INDEX.get(" ".join(str(text).split()).lower())
