"""Colors and the shared Altair theme used by every Project 1 chart."""
from __future__ import annotations

import altair as alt

CONTEXT: str = "#4ea8de"   # background marks, a clear mid blue
ACCENT: str = "#f26b21"    # the marks the reader should look at, a vivid orange
DARK: str = "#1b2a41"      # titles, reference lines, labels (deep navy)
SUBTITLE: str = "#555555"


def apply_theme(chart: alt.TopLevelMixin) -> alt.TopLevelMixin:
    """Apply the common font sizes, title alignment and no-grid styling.

    Args:
        chart: Any top-level Altair chart (single, layered or concatenated).

    Returns:
        The same chart with view, axis and title configuration applied.
    """
    return (
        chart.configure_view(stroke=None)
        .configure_axis(labelFontSize=12, titleFontSize=13, grid=False)
        .configure_title(
            fontSize=20,
            subtitleFontSize=12,
            anchor="start",
            color=DARK,
            subtitleColor=SUBTITLE,
        )
    )
