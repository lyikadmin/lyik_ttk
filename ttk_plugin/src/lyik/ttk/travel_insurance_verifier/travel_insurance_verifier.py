import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing import Annotated
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import RootTravelInsurance, INSURANCEOPTION
import logging
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class TravelInsuranceVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootTravelInsurance,
            Doc("Travel Insurance payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Travel Insurance."),
    ]:
        """
        This verifier validates the data of the Travel Insurance section.
        """
        skip_travel_insurance = None
        if payload and payload.insurance_options_card and payload.insurance_options_card.insurance_options:
            if payload.insurance_options_card.insurance_options.value == INSURANCEOPTION.TTK_ASSITANCE.value:
                skip_travel_insurance = INSURANCEOPTION.TTK_ASSITANCE

        salary_slip_file = None
        if (
            payload
            and payload.flight_reservation_details
            and payload.flight_reservation_details.flight_reservation_tickets
        ):
            salary_slip_file = (
                payload.flight_reservation_details.flight_reservation_tickets
            )

        if not (skip_travel_insurance or salary_slip_file):
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message("LYIK_ERR_NO_TRAVEL_INSURANCE"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        return VerifyHandlerResponseModel(
            actor=ACTOR,
            message=f"Verified by {ACTOR}",
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
        )
