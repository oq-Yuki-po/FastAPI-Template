from pathlib import Path

from eralchemy2 import render_er

from app import models as _models  # noqa: F401
from app.db.base import Base

OUTPUT_PATHS = (
    Path("docs/database/schema.svg"),
    Path("docs/database/schema.png"),
)


def generate_erd(output_path: Path) -> Path:
    """Render an ER diagram directly from SQLAlchemy's declared metadata."""
    # Importing app.models registers every mapped table on Base.metadata. No engine,
    # database connection, or migration execution is involved in this process.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # ERAlchemy2 does not publish type information, but its documented Python API
    # accepts a SQLAlchemy declarative base and an output path.
    render_er(Base, str(output_path))  # type: ignore[no-untyped-call]
    return output_path


if __name__ == "__main__":
    for output_path in OUTPUT_PATHS:
        generated_path = generate_erd(output_path)
        print(f"Generated ER diagram: {generated_path}")
