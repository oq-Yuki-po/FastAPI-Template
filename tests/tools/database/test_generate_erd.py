from pathlib import Path
from unittest.mock import patch

from app.db.base import Base
from tools.database.generate_erd import generate_erd


def test_generate_erd_uses_declared_sqlalchemy_metadata(tmp_path: Path) -> None:
    output_path = tmp_path / "schema.svg"

    with patch("tools.database.generate_erd.render_er") as render_er:
        generated_path = generate_erd(output_path)

    assert generated_path == output_path
    assert {"authors", "books", "users"} <= set(Base.metadata.tables)
    render_er.assert_called_once_with(Base, str(output_path))
