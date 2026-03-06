"""seed_data

Revision ID: c991c8dd3f02
Revises:
Create Date: 2026-02-28 12:39:04.291088

"""

import json
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Type, Union, cast

from alembic import op
from sqlalchemy import Table, TableClause, delete
from sqlmodel import SQLModel

from app.models.app_settings import AppSettings
from app.models.sql.patient import SQLPatient
from app.models.sql.patient_note import SQLPatientNote
from app.models.sql.user import SQLUser

# revision identifiers, used by Alembic.
revision: str = "c991c8dd3f02"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
tables = (SQLUser, SQLPatient, SQLPatientNote)


def _get_table_name(model: Type[SQLModel]) -> TableClause:
    return cast(Any, model).__tablename__


def _get_table(model: Type[SQLModel]) -> Table:
    return cast(Table, cast(Any, model).__table__)


def _seed_path_for(model: Type[SQLModel]) -> Path:
    """Return the path to a JSON seed file for a given SQLModel table type."""

    base = Path(__file__).parent.parent
    return base / "data" / "seed" / f"{_get_table_name(model)}.json"


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
    if AppSettings.EnvTraits.HAS_SEED_DATA not in AppSettings.default().env_traits:
        return

    bind = op.get_bind()
    for model in tables:
        # ensure the table exists before attempting to insert
        SQLModel.metadata.create_all(bind=bind, tables=[_get_table(model)])

        records = _load_records(model)
        if not records:
            continue
        bind.execute(_get_table(model).insert(), [r.model_dump(exclude_none=True) for r in records])


def downgrade() -> None:
    if AppSettings.EnvTraits.HAS_SEED_DATA not in AppSettings.default().env_traits:
        return

    bind = op.get_bind()
    for model in tables:
        path = _seed_path_for(model)
        if not path.exists():
            continue
        if not (ids := list(_ids_from_file(path))):
            continue
        bind.execute(delete(_get_table(model)).where(_get_table(model).c.id.in_(ids)))
