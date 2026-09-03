"""Deterministic reference data for local demos and repeatable tests."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.all import Berth, Commodity, Origin, Plant, Port

REFERENCE_IDS = {
    "commodity_iron_ore": UUID("00000000-0000-0000-0000-000000000101"),
    "plant_rotterdam": UUID("00000000-0000-0000-0000-000000000201"),
    "origin_brazil": UUID("00000000-0000-0000-0000-000000000301"),
    "port_rotterdam": UUID("00000000-0000-0000-0000-000000000401"),
    "port_tubarão": UUID("00000000-0000-0000-0000-000000000402"),
    "berth_rotterdam_1": UUID("00000000-0000-0000-0000-000000000501"),
}


def seed_reference_data(session: Session) -> None:
    """Insert the canonical reference set; safe to call repeatedly."""
    session.merge(
        Commodity(
            id=REFERENCE_IDS["commodity_iron_ore"],
            name="Iron ore",
            code="IRON_ORE",
            hazardous=False,
        )
    )
    session.merge(
        Plant(
            id=REFERENCE_IDS["plant_rotterdam"],
            name="Rotterdam Steel Plant",
            code="PLANT_RTM",
            location="POINT (4.4777 51.9244)",
        )
    )
    session.merge(
        Origin(
            id=REFERENCE_IDS["origin_brazil"],
            name="Brazil",
            country_code="BR",
            location="POINT (-43.1729 -22.9068)",
        )
    )
    session.merge(
        Port(
            id=REFERENCE_IDS["port_rotterdam"],
            name="Port of Rotterdam",
            unlocode="NLRTM",
            country_code="NL",
            location="POINT (4.4777 51.9244)",
        )
    )
    session.merge(
        Port(
            id=REFERENCE_IDS["port_tubarão"],
            name="Tubarão",
            unlocode="BRTUB",
            country_code="BR",
            location="POINT (-40.2350 -20.2886)",
        )
    )
    session.merge(
        Berth(
            id=REFERENCE_IDS["berth_rotterdam_1"],
            port_id=REFERENCE_IDS["port_rotterdam"],
            name="Iron Ore Terminal 1",
            code="RTM-IO-1",
            max_draft_m=22,
        )
    )
    session.commit()
