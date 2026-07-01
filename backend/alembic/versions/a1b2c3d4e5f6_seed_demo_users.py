"""seed demo users

Демо-пользователи (student/teacher/admin) с фиксированными UUID, совпадающими
с _DEMO_USERS в app/api/v1/auth.py. Без них documents.uploaded_by (FK → users.id)
нарушается при загрузке под demo-логином. Идемпотентно (ON CONFLICT DO NOTHING).

Revision ID: a1b2c3d4e5f6
Revises: 95efa6218fcb
Create Date: 2026-07-01 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "95efa6218fcb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (id, full_name, role, group_name)
_DEMO_USERS = [
    ("00000000-0000-0000-0000-000000000001", "Вадим Рыбаченок", "student", "БПИ2403"),
    ("00000000-0000-0000-0000-000000000002", "Мосева Марина Сергеевна", "teacher", None),
    ("00000000-0000-0000-0000-000000000003", "Администратор", "admin", None),
]


def upgrade() -> None:
    for user_id, full_name, role, group_name in _DEMO_USERS:
        op.execute(_insert_sql(user_id, full_name, role, group_name))


def downgrade() -> None:
    ids = ", ".join(f"'{u[0]}'" for u in _DEMO_USERS)
    op.execute(f"DELETE FROM users WHERE id IN ({ids})")


def _insert_sql(user_id: str, full_name: str, role: str, group_name: str | None) -> str:
    grp = "NULL" if group_name is None else f"'{group_name}'"
    return (
        "INSERT INTO users (id, full_name, role, group_name) "
        f"VALUES ('{user_id}', '{full_name}', '{role}', {grp}) "
        "ON CONFLICT (id) DO NOTHING"
    )
