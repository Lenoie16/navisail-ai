"""Authentication, role and permission policy for API handlers."""

from enum import StrEnum
from fastapi import Depends, Header, HTTPException, Request
from app.core.config import settings


class Permission(StrEnum):
    CREATE_SHIPMENT = "create shipment"
    VIEW_DECISIONS = "view decisions"
    RUN_SIMULATION = "run simulation"
    APPROVE_RECOMMENDATION = "approve recommendation"
    EXECUTE_BOOKING = "execute booking"
    VIEW_AUDIT = "view audit"
    MANAGE_MODEL = "manage model"
    MANAGE_DATA_SOURCES = "manage data sources"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "chartering_manager": frozenset({Permission.CREATE_SHIPMENT, Permission.VIEW_DECISIONS, Permission.RUN_SIMULATION, Permission.APPROVE_RECOMMENDATION, Permission.EXECUTE_BOOKING}),
    "procurement_commercial": frozenset({Permission.CREATE_SHIPMENT, Permission.VIEW_DECISIONS, Permission.RUN_SIMULATION, Permission.APPROVE_RECOMMENDATION, Permission.EXECUTE_BOOKING}),
    "operations": frozenset({Permission.VIEW_DECISIONS, Permission.EXECUTE_BOOKING}),
    "plant_supply": frozenset({Permission.CREATE_SHIPMENT, Permission.VIEW_DECISIONS, Permission.RUN_SIMULATION}),
    "leadership": frozenset({Permission.VIEW_DECISIONS, Permission.VIEW_AUDIT}),
    "it_data_ml": frozenset({Permission.VIEW_DECISIONS, Permission.MANAGE_MODEL, Permission.MANAGE_DATA_SOURCES}),
    "auditor_governance": frozenset({Permission.VIEW_DECISIONS, Permission.VIEW_AUDIT}),
    "approver": frozenset({Permission.APPROVE_RECOMMENDATION, Permission.VIEW_DECISIONS}),
    "admin": frozenset(Permission),
}


def normalize_role(role: str) -> str:
    return role.strip().lower().replace("/", "_").replace("-", "_").replace(" ", "_")


def has_permission(role: str, permission: Permission | str) -> bool:
    try:
        required = Permission(permission)
    except ValueError:
        return False
    return required in ROLE_PERMISSIONS.get(normalize_role(role), frozenset())


async def get_principal(
    request: Request,
    x_navisail_user: str | None = Header(default=None),
    x_navisail_role: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> tuple[str, str]:
    if settings.auth_token and authorization != f"Bearer {settings.auth_token}":
        raise HTTPException(status_code=401, detail="valid bearer authentication is required")
    if settings.auth_required and (not x_navisail_user or not x_navisail_role):
        raise HTTPException(status_code=401, detail="X-Navisail-User and X-Navisail-Role are required")
    return x_navisail_user or "current-user", normalize_role(x_navisail_role or "admin" if settings.demo_mode else "viewer")


def require_permission(permission: Permission):
    async def dependency(principal: tuple[str, str] = Depends(get_principal)) -> tuple[str, str]:
        user, role = principal
        if not has_permission(role, permission):
            from app.audit.service import AuditEvent, audit_service

            audit_service.record(
                AuditEvent(
                    actor=user,
                    action="authorization_denied",
                    entity_type="permission",
                    entity_id=permission.value,
                    details={"role": role},
                )
            )
            raise HTTPException(status_code=403, detail=f"permission denied: {permission.value}")
        return user, role

    return dependency
