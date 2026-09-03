"""Small typed CRUD repository shared by API resources."""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from app.models.all import Entity
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT", bound=Entity)


class Repository(Generic[ModelT]):  # noqa: UP046
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        return self.session.scalars(select(self.model).offset(offset).limit(limit)).all()

    def get(self, entity_id: UUID) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def create(self, values: dict[str, Any]) -> ModelT:
        entity = self.model(**values)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, entity: ModelT, values: dict[str, Any]) -> ModelT:
        for key, value in values.items():
            setattr(entity, key, value)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.execute(delete(self.model).where(self.model.id == entity.id))
        self.session.commit()
