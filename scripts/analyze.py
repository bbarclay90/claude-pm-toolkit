"""Excel data analysis utilities."""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs" / "output"


def load(filename: str, sheet: str | int = 0) -> pd.DataFrame:
    """Load an Excel file from the data/ directory."""
    return pd.read_excel(DATA_DIR / filename, sheet_name=sheet)


def summarize(df: pd.DataFrame) -> None:
    """Print shape, column types, null counts, and descriptive stats."""
    print(f"Shape: {df.shape}")
    print(f"\nColumns:\n{df.dtypes}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\nSummary stats:\n{df.describe(include='all')}")


def pivot(df: pd.DataFrame, index: str, columns: str, values: str, aggfunc="sum") -> pd.DataFrame:
    return pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=aggfunc)


def top_n(df: pd.DataFrame, column: str, n: int = 10, ascending: bool = False) -> pd.DataFrame:
    return df.nlargest(n, column) if not ascending else df.nsmallest(n, column)


def save_csv(df: pd.DataFrame, filename: str) -> None:
    path = DOCS_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved to {path}")
