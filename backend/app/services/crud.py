"""Application CRUD services: orchestration only, no domain calculations."""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from app.models.all import Entity
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT", bound=Entity)


class CrudService(Generic[ModelT]):  # noqa: UP046
    def __init__(self, session: Session, repository: Any) -> None:
        self.session = session
        self.repository = repository(session)

    def list(self, limit: int, offset: int) -> Sequence[ModelT]:
        return self.repository.list(limit=limit, offset=offset)  # type: ignore[no-any-return]

    def get(self, entity_id: UUID) -> ModelT | None:
        return self.repository.get(entity_id)  # type: ignore[no-any-return]

    def create(self, values: dict[str, Any]) -> ModelT:
        return self.repository.create(values)  # type: ignore[no-any-return]

    def update(self, entity: ModelT, values: dict[str, Any]) -> ModelT:
        return self.repository.update(entity, values)  # type: ignore[no-any-return]

    def delete(self, entity: ModelT) -> None:
        self.repository.delete(entity)
