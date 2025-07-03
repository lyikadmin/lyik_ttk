# plugins/consultant/maker_copy_to_panes.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    PreActionProcessorSpec,
    getProjectName,
)
from typing_extensions import Doc

from ..models.forms.new_schengentouristvisa_ import Schengentouristvisa

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
    parts = path.split(".")
    for key in parts[:-1]:
        obj = obj.setdefault(key, {})
    obj[parts[-1]] = value

#  Individual copier steps
def _copy_appointments(data: dict, consul: dict) -> None:
    """Copy consultant_info.appointments → appointment.appointment_scheduled"""

    add_on_option  = (data.get("appointment") or {}).get("add_on_service_option")
    if add_on_option != 'YES':
        return
    
    appointments_consul = consul.get("appointments")
    if not isinstance(appointments_consul, dict):
        return
    
    if any(appointments_consul.get(f) is not None for f in (
        "scheduled_location",
        "scheduled_date",
        "scheduled_hour",
        "scheduled_minute",
        "upload_appointment",
    )):
        _dig_set(data, "appointment.appointment_scheduled", {
            k: appointments_consul[k] for k in (
                "scheduled_location",
                "scheduled_date",
                "scheduled_hour",
                "scheduled_minute",
                "upload_appointment",
            ) if k in appointments_consul
        })

def _copy_itinerary(data: dict, consul: dict) -> None:
    """Copy consultant_info.itinerary_addon.upload_itinerary → itinerary_accomodation.itinerary_card.upload_itinerary"""
    itinerary_addon = consul.get("itinerary_addon")
    if not isinstance(itinerary_addon, dict):
        return

    _dig_set(data, "itinerary_accomodation.itinerary_card.upload_itinerary", itinerary_addon)

def _copy_accommodation(data: dict, consul: dict) -> None:
    """
    Copy consultant_info.dummy_accommodation
        or consultant_info.confirmed_accommodation
    → accomodation.booked_appointment
    and force accommodation_choice.accommodation_option='BOOKED'
    """
    acc = consul.get("confirmed_accommodation") or consul.get("dummy_accommodation")
    if not isinstance(acc, dict):
        return

    booking = acc.get("booking_upload")
    if not booking:
        return

    # force BOOKED
    _dig_set(data, "accomodation.accommodation_choice.accommodation_option", "BOOKED")

    # build the booked_appointment payload
    card: Dict[str, Any] = {}
    card["booking_upload"] = booking
    for fld in ("accommodation_name", "accommodation_address", "accommodation_email", "accommodation_phone"):
        val = acc.get(fld)
        if val:
            card[fld] = val

    _dig_set(data, "accomodation.booked_appointment", card)

def _copy_flight_tickets(data: dict, consul: dict) -> None:
    """Copy consultant_info.{dummy|confirmed}_flight_ticket.flight_tickets → ticketing.flight_tickets"""
    flight = consul.get("confirmed_flight_ticket") or consul.get("dummy_flight_ticket")
    if not isinstance(flight, dict):
        return

    tickets = flight.get("flight_tickets")
    if not tickets:
        return

    _dig_set(data, "ticketing.flight_tickets.flight_tickets", tickets)


def _copy_travel_insurance(data: dict, consul: dict) -> None:
    """Copy consultant_info.travel_insurances.flight_reservation_tickets → travel_insurance.flight_reservation_details.flight_reservation_tickets"""
    ins = consul.get("travel_insurances")
    if not isinstance(ins, dict):
        return

    ticket = ins.get("flight_reservation_tickets")
    if not ticket:
        return

    _dig_set(data, "travel_insurance.flight_reservation_details.flight_reservation_tickets", ticket)

#  Pipeline
_COPIERS: List[Callable[[dict, dict], None]] = [
    _copy_appointments,
    _copy_itinerary,
    _copy_accommodation,
    _copy_flight_tickets,
    _copy_travel_insurance,
]

class MakerCopyToPanes(PreActionProcessorSpec):
    """
    Copies consultant_info (entered by Maker) into the traveller’s own panes.
    """

    @impl
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
