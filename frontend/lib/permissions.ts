export type NavisailRole =
  | "chartering_manager"
  | "procurement_commercial"
  | "operations"
  | "plant_supply"
  | "leadership"
  | "it_data_ml"
  | "auditor_governance"
  | "approver"
  | "admin";

export type Permission =
  | "create shipment"
  | "view decisions"
  | "run simulation"
  | "approve recommendation"
  | "execute booking"
  | "view audit"
  | "manage model"
  | "manage data sources";

const permissions: Record<NavisailRole, readonly Permission[]> = {
  chartering_manager: [
    "create shipment",
    "view decisions",
    "run simulation",
    "approve recommendation",
    "execute booking",
  ],
  procurement_commercial: [
    "create shipment",
    "view decisions",
    "run simulation",
    "approve recommendation",
    "execute booking",
  ],
  operations: ["view decisions", "execute booking"],
  plant_supply: ["create shipment", "view decisions", "run simulation"],
  leadership: ["view decisions", "view audit"],
  it_data_ml: ["view decisions", "manage model", "manage data sources"],
  auditor_governance: ["view decisions", "view audit"],
  approver: ["approve recommendation", "view decisions"],
  admin: [
    "create shipment",
    "view decisions",
    "run simulation",
    "approve recommendation",
    "execute booking",
    "view audit",
    "manage model",
    "manage data sources",
  ],
};

export function canAccess(role: NavisailRole, permission: Permission): boolean {
  return permissions[role]?.includes(permission) ?? false;
}
