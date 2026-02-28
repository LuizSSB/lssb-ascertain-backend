"""seed_data

Revision ID: c991c8dd3f02
Revises:
Create Date: 2026-02-28 12:39:04.291088

"""

import json
from pathlib import Path
from typing import Iterable, List, Sequence, Type, Union

from alembic import op
from sqlalchemy import delete
from sqlmodel import SQLModel

from app.models.sql.patient import SQLPatient
from app.models.sql.patient_note import SQLPatientNote

# revision identifiers, used by Alembic.
revision: str = "c991c8dd3f02"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
tables = (SQLPatient, SQLPatientNote)


def _seed_path_for(model: Type[SQLModel]) -> Path:
    """Return the path to a JSON seed file for a given SQLModel table type."""

    base = Path(__file__).parent.parent
    return base / "data" / "seed" / f"{model.__tablename__}.json"


def _load_records(model: Type[SQLModel]) -> List[SQLModel]:
    path = _seed_path_for(model)
    if not path.exists():
        return []
    with path.open("r") as f:
        data = json.load(f)
    return [model.model_validate(item) for item in data]


def _ids_from_file(path: Path) -> Iterable[str]:
    with path.open("r") as f:
        data = json.load(f)
    return [item["id"] for item in data if "id" in item]


def upgrade() -> None:
    """Seed the database.

    For each known SQLModel class we look for a JSON file containing an
    array of dictionaries that can be parsed into that type.  If the file is
    present we execute a bulk insert through the bind obtained from Alembic.
    """

    bind = op.get_bind()
    for model in tables:
        # ensure the table exists before attempting to insert
        SQLModel.metadata.create_all(bind=bind, tables=[model.__table__])

        records = _load_records(model)
        if not records:
            continue
        bind.execute(model.__table__.insert(), [r.model_dump(exclude_none=True) for r in records])


def downgrade() -> None:
    """Remove seeded rows from the database.

    Deletes any rows whose primary key matches an `id` value listed in the
    corresponding seed JSON file.  No action is taken if the file is absent.
    """

    bind = op.get_bind()
    for model in tables:
        path = _seed_path_for(model)
        if not path.exists():
            continue
        ids = list(_ids_from_file(path))
        if not ids:
            continue
        bind.execute(delete(model.__table__).where(model.__table__.c.id.in_(ids)))
