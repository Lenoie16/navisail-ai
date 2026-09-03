"""Reusable CRUD route factory for reference and operational resources."""

from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.crud import CrudService


def crud_router(
    *,
    path: str,
    tag: str,
    service: Any,
    create_schema: type[Any],
    update_schema: type[Any],
    read_schema: type[Any],
) -> APIRouter:
    """Build conventional list/create/read/update/delete endpoints."""
    router = APIRouter(prefix=f"/{path}", tags=[tag])

    def repo(db: Session = Depends(get_db)) -> CrudService[Any]:  # noqa: B008
        return cast(CrudService[Any], service(db))

    @router.get("", response_model=list[read_schema])  # type: ignore[valid-type]
    def list_items(
        db_repo: CrudService[Any] = Depends(repo),  # noqa: B008
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> Any:
        return db_repo.list(limit=limit, offset=offset)

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_item(
        payload: create_schema,  # type: ignore[valid-type]
        db_repo: CrudService[Any] = Depends(repo),  # noqa: B008
    ) -> Any:
        try:
            return db_repo.create(payload.model_dump())  # type: ignore[attr-defined]
        except IntegrityError as exc:
            db_repo.session.rollback()
            raise HTTPException(
                status_code=409, detail="Resource violates a uniqueness or FK constraint"
            ) from exc

    @router.get("/{item_id}", response_model=read_schema)
    def get_item(item_id: UUID, db_repo: CrudService[Any] = Depends(repo)) -> Any:  # noqa: B008
        item = db_repo.get(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        return item

    @router.patch("/{item_id}", response_model=read_schema)
    def update_item(
        item_id: UUID,
        payload: update_schema,  # type: ignore[valid-type]
        db_repo: CrudService[Any] = Depends(repo),  # noqa: B008
    ) -> Any:
        item = db_repo.get(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        try:
            return db_repo.update(item, payload.model_dump(exclude_unset=True))  # type: ignore[attr-defined]
        except IntegrityError as exc:
            db_repo.session.rollback()
            raise HTTPException(
                status_code=409, detail="Resource violates a uniqueness or FK constraint"
            ) from exc

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: UUID, db_repo: CrudService[Any] = Depends(repo)) -> None:  # noqa: B008
        item = db_repo.get(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        try:
            db_repo.delete(item)
        except IntegrityError as exc:
            db_repo.session.rollback()
            raise HTTPException(
                status_code=409, detail="Resource is still referenced by another entity"
            ) from exc

    return router
