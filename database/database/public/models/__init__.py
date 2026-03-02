# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKeyConstraint


class Base(DeclarativeBase):
    pass

class Agenda(Base):
    __tablename__ = "agenda"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str]
    phone: Mapped[str]

    __table_args__ = {'schema': 'public'}

