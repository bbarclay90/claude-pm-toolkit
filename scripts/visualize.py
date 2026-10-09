"""Visualization utilities for PM analysis."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs" / "output"


def _save(fig, filename: str | None):
    if filename:
        path = DOCS_DIR / filename
        if filename.endswith(".html"):
            fig.write_html(path)
        else:
            fig.write_image(path)
        print(f"Saved to {path}")
    fig.show()


def bar(df: pd.DataFrame, x: str, y: str, title: str = "", color: str = None, save_as: str = None):
    fig = px.bar(df, x=x, y=y, title=title, color=color)
    _save(fig, save_as)


def line(df: pd.DataFrame, x: str, y: str | list, title: str = "", save_as: str = None):
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    _save(fig, save_as)


def scatter(df: pd.DataFrame, x: str, y: str, size: str = None, color: str = None,
            label: str = None, title: str = "", save_as: str = None):
    fig = px.scatter(df, x=x, y=y, size=size, color=color, text=label, title=title)
    _save(fig, save_as)


def heatmap(df: pd.DataFrame, title: str = "", save_as: str = None):
    """Expects a pivot-table shaped DataFrame (index = rows, columns = cols)."""
    fig = px.imshow(df, text_auto=True, title=title, aspect="auto")
    _save(fig, save_as)


def funnel(stages: list[str], values: list[int | float], title: str = "", save_as: str = None):
    fig = go.Figure(go.Funnel(y=stages, x=values))
    fig.update_layout(title=title)
    _save(fig, save_as)
