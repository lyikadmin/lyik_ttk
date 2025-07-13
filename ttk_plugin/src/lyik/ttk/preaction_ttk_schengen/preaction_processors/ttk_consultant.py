# plugins/consultant/maker_copy_to_panes.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    getProjectName,
)
from typing_extensions import Doc
from ._base_preaction import BasePreActionProcessor

from ...models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    ACCOMMODATIONARRANGEMENT,
    RootConsultantInfoConfirmedAccommodation,
    RootConsultantInfoDummyAccommodation,
    RootConsultantInfoConfirmedFlightTicket,
    RootConsultantInfoDummyFlightTicket,
)

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())


#  Generic dotted-path accessors
def _dig_get(obj: dict, path: str) -> Any:
    for key in path.split("."):
        if not isinstance(obj, dict) or key not in obj:
            return None
        obj = obj[key]
    return obj


def _dig_set(obj: dict, path: str, value: Any) -> None:
    """
    Walks obj[path] = value, creating any intermediate dicts.
    If an intermediate key exists but is not a dict (e.g. None),
    it is replaced with a new dict so we never call .setdefault() on None.
    """
    parts = path.split(".")
    for key in parts[:-1]:
        cur = obj.get(key)
        if not isinstance(cur, dict):
            # replace None or any other non-dict
            cur = {}
            obj[key] = cur
        obj = cur
    obj[parts[-1]] = value


#  Individual copier steps
def _copy_appointments(data: dict, consul: dict) -> None:
    """Copy consultant_info.appointments → appointment.appointment_scheduled"""

    add_on_option = (data.get("appointment") or {}).get("add_on_service_option")
    if add_on_option != "YES":
        return

    appointments_consul = consul.get("appointments")
    if not isinstance(appointments_consul, dict):
        return

    if any(
        appointments_consul.get(f) is not None
        for f in (
            "scheduled_location",
            "scheduled_date",
            "scheduled_hour",
            "scheduled_minute",
            "upload_appointment",
        )
    ):
        _dig_set(
            data,
            "appointment.appointment_scheduled",
            {
                k: appointments_consul[k]
                for k in (
                    "scheduled_location",
                    "scheduled_date",
                    "scheduled_hour",
                    "scheduled_minute",
                    "upload_appointment",
                )
                if k in appointments_consul
            },
        )
        # add a lock_appointment value to be true
    # in _copy_appointments, right after you set appointment.appointment_scheduled:
    _dig_set(data, "appointment.lock_appointment", "Lock")


def _copy_itinerary(data: dict, consul: dict) -> None:
    """Copy consultant_info.itinerary_addon.upload_itinerary → itinerary_accomodation.itinerary_card.upload_itinerary"""
    itinerary_addon = consul.get("itinerary_addon")
    if not isinstance(itinerary_addon, dict):
        return

    upload_itinerary = itinerary_addon.get("upload_itinerary")
    if not upload_itinerary:
        return

    _dig_set(
        data, "itinerary_accomodation.itinerary_card.upload_itinerary", upload_itinerary
    )
    # lock_itinerary will be true
    # in _copy_itinerary, right after you set itinerary_accomodation.itinerary_card.upload_itinerary:
    _dig_set(data, "itinerary_accomodation.lock_itinerary", "Lock")


def _copy_accommodation(data: dict, consul: dict) -> None:
    """
    Copy either confirmed_accommodation or dummy_accommodation into
    accomodation.booked_appointment—but only if the consultant actually
    provided at least one field.  Any field they left as None is dropped.
    """
    # 1) grab the raw dicts (or empty if missing)
    confirmed_raw = consul.get("confirmed_accommodation") or {}
    dummy_raw = consul.get("dummy_accommodation") or {}

    # 2) parse + prune Nones via Pydantic
    try:
        confirmed = RootConsultantInfoConfirmedAccommodation(
            **confirmed_raw
        ).model_dump(exclude_none=True)
    except Exception:
        confirmed = {}
    try:
        dummy = RootConsultantInfoDummyAccommodation(**dummy_raw).model_dump(
            exclude_none=True
        )
    except Exception:
        dummy = {}

    # 3) pick the first non-empty
    acc = confirmed or dummy
    if not acc:
        return  # neither had any real data

    # 4) build your card straight from acc (it already has only the set fields)
    card = acc

    # 5) mark the choice as BOOKED
    _dig_set(
        data,
        "accomodation.accommodation_choice.accommodation_option",
        ACCOMMODATIONARRANGEMENT.BOOKED,
    )

    # 6) plug it into booked_appointment
    _dig_set(data, "accomodation.booked_appointment", card)
    # lock_itinerary will be true
    # in _copy_accommodation, right after you set accomodation.booked_appointment:
    _dig_set(data, "accomodation.lock_accommodation", "Lock")


def _copy_flight_tickets(data: dict, consul: dict) -> None:
    """
    Copy consultant_info.confirmed_flight_ticket or dummy_flight_ticket
    → ticketing.flight_tickets.flight_tickets,
    but only if the consultant actually provided something.
    """

    # 1) pull both raw dicts (or empty if missing)
    raw_conf = consul.get("confirmed_flight_ticket") or {}
    raw_dummy = consul.get("dummy_flight_ticket") or {}

    # 2) parse + prune None-fields via Pydantic
    try:
        conf = RootConsultantInfoConfirmedFlightTicket(**raw_conf).model_dump(
            exclude_none=True
        )
    except Exception:
        conf = {}
    try:
        dummy = RootConsultantInfoDummyFlightTicket(**raw_dummy).model_dump(
            exclude_none=True
        )
    except Exception:
        dummy = {}

    # 3) pick whichever has real data
    flight = conf or dummy
    if not flight:
        return  # neither had any non-None field

    # 4) grab the actual upload (Pydantic has already stripped out None)
    tickets = flight.get("flight_tickets")
    if tickets is None:
        return  # just in case

    # 5) copy into your pane
    _dig_set(data, "ticketing.flight_tickets.flight_tickets", tickets)
    # lock_ticket to be true
    # in _copy_flight_tickets, right after you set ticketing.flight_tickets.flight_tickets:
    _dig_set(data, "ticketing.lock_ticket", "Lock")


def _copy_travel_insurance(data: dict, consul: dict) -> None:
    """Copy consultant_info.travel_insurances.flight_reservation_tickets → travel_insurance.flight_reservation_details.flight_reservation_tickets"""
    ins = consul.get("travel_insurances")
    if not isinstance(ins, dict):
        return logger.warning("Insurance Card itself empty")

    ticket = ins.get("flight_reservation_tickets")
    if ticket is None:
        return logger.warning("Cant find the file")

    _dig_set(
        data,
        "travel_insurance.flight_reservation_details.flight_reservation_tickets",
        ticket,
    )
    _dig_set(data, "travel_insurance.lock_travel_insurance", "Lock")


#  Pipeline
_COPIERS: List[Callable[[dict, dict], None]] = [
    _copy_appointments,
    _copy_itinerary,
    _copy_accommodation,
    _copy_flight_tickets,
    _copy_travel_insurance,
]


class PreactionMakerCopyToPanes(BasePreActionProcessor):
    """
    Copies consultant_info (entered by Maker) into the traveller’s own panes.
    """

    async def pre_action_processor(
        self,
        context: ContextModel,
        action: str,
        current_state: Optional[str],
        new_state: Optional[str],
        payload: GenericFormRecordModel,
    ) -> GenericFormRecordModel:

        # 1) try parsing into your Pydantic model (safe fallback on error)
        try:
            form = Schengentouristvisa(**payload.model_dump())
            data: dict = form.model_dump()
        except Exception as e:
            logger.error("maker_copy_to_panes: parse error %s", e)
            data = payload.model_dump()
            return GenericFormRecordModel.model_validate(data)

        # 2) pull out consultant_info
        consul = _dig_get(data, "consultant_info")
        if not isinstance(consul, dict):
            return GenericFormRecordModel.model_validate(data)

        # 3) run each copier in turn
        for copier in _COPIERS:
            try:
                copier(data, consul)
            except Exception as e:
                logger.warning("copier %s failed: %s", copier.__name__, e)

        # 4) re-validate and return
        return GenericFormRecordModel.model_validate(data)
