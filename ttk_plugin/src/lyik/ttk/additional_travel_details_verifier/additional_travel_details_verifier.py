import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
)
from lyikpluginmanager.annotation import RequiredVars
from typing import Annotated
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import (
    RootAdditionalDetails,
    SPONSORTYPE1,
    SPONSORTYPE2,
    SPONSORTYPE3,
    SPONSORTYPE4,
    PAYMENTMETHOD6,
    EXPENSECOVERAGE5,
)
from lyik.ttk.utils.message import get_error_message
import logging
from lyik.ttk.utils.verifier_util import (
    check_if_verified,
    validate_email,
    validate_pincode,
    validate_phone,
    validate_aadhaar_number,
)
import re

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class AdditionalTravelDetailsVerifier(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAdditionalDetails, Doc("Payload for Additional Travel Details.")
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredVars(["DEFAULT_COUNTRY_CODE"]),
        Doc("Response after validating Previous Visas details."),
    ]:
        """
        This plugin verifies the additional travel details of the user.
        Args:
            payload (RootAdditionalDetails): This is the additional travel details payload.
        Returns:
            VerifyHandlerResponseModel: VerifyHandlerResponseModel with the verification status.

        """
        try:
            if payload is None:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The payload is missing. Ensure the payload is properly available.",
                )

            if not any(
                [
                    payload.sponsorship_options_1,
                    payload.sponsorship_options_2,
                    payload.sponsorship_options_3,
                    payload.sponsorship_options_4,
                ]
            ):
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    message="Please select at least one type of your sponsor.",
                )

            # Rule 1: If sponsorship_options_1 is selected, at least one means_of_support_myself must be selected
            if (
                payload.sponsorship_options_1
                and payload.sponsorship_options_1 == SPONSORTYPE1.SELF.value
            ):
                # if not payload.means_of_support_myself:
                #     return VerifyHandlerResponseModel(
                #         status=VERIFY_RESPONSE_STATUS.FAILURE,
                #         actor="system",
                #         message="Please select at least one Means of Support under 'Myself'.",
                #     )

                myself_fields = [
                    (
                        payload.means_of_support_myself.support_means_cash
                        if payload.means_of_support_myself
                        else None
                    ),
                    (
                        payload.means_of_support_myself.support_means_travellers_cheque
                        if payload.means_of_support_myself
                        else None
                    ),
                    (
                        payload.means_of_support_myself.support_means_credit_card
                        if payload.means_of_support_myself
                        else None
                    ),
                    (
                        payload.means_of_support_myself.support_means_prepaid_accommodation
                        if payload.means_of_support_myself
                        else None
                    ),
                    (
                        payload.means_of_support_myself.support_means_prepaid_transport
                        if payload.means_of_support_myself
                        else None
                    ),
                    (
                        payload.means_of_support_myself.support_means_other
                        if payload.means_of_support_myself
                        else None
                    ),
                ]
                if not any(myself_fields):
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        actor="system",
                        message="Please select at least one Means of Support under 'Myself'.",
                    )

            # Rule 2: If any of sponsorship_options_2/3/4 is selected, at least one means_of_support_sponser must be selected
            if any(
                [
                    payload.sponsorship_options_2
                    and payload.sponsorship_options_2 == SPONSORTYPE2.SPONSOR.value,
                    payload.sponsorship_options_3
                    and payload.sponsorship_options_3 == SPONSORTYPE3.INVITER.value,
                    payload.sponsorship_options_4
                    and payload.sponsorship_options_4 == SPONSORTYPE4.OTHER.value,
                ]
            ):
                # if not payload.means_of_support_sponser:
                #     return VerifyHandlerResponseModel(
                #         status=VERIFY_RESPONSE_STATUS.FAILURE,
                #         actor="system",
                #         message="Please select at least one Means of Support under 'Sponsor(s)'.",
                #     )
                sponsor_fields = [
                    (
                        payload.means_of_support_sponser.coverage_expense_cash
                        if payload.means_of_support_sponser
                        else None
                    ),
                    (
                        payload.means_of_support_sponser.coverage_accommodation_provided
                        if payload.means_of_support_sponser
                        else None
                    ),
                    (
                        payload.means_of_support_sponser.coverage_all_covered
                        if payload.means_of_support_sponser
                        else None
                    ),
                    (
                        payload.means_of_support_sponser.coverage_prepaid_transport
                        if payload.means_of_support_sponser
                        else None
                    ),
                    (
                        payload.means_of_support_sponser.coverage_other
                        if payload.means_of_support_sponser
                        else None
                    ),
                ]
                if not any(sponsor_fields):
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        actor="system",
                        message="Please select at least one Means of Support under 'Sponsor(s)'.",
                    )

            error_paths = {}

            if payload.sponsorship_options_4 == SPONSORTYPE4.OTHER.value:
                if not payload.others_specify:
                    error_paths["additional_details.others_specify"] = (
                        "Please Enter Mandatory Field."
                    )

            if (
                payload.means_of_support_myself
                and payload.means_of_support_myself.support_means_other
                == PAYMENTMETHOD6.OTHER.value
            ):
                if not payload.means_of_support_myself.others_specify_1:
                    error_paths[
                        "additional_details.means_of_support_myself.others_specify_1"
                    ] = "Please Enter Mandatory Field."

            if (
                payload.means_of_support_sponser
                and payload.means_of_support_sponser.coverage_other
                == EXPENSECOVERAGE5.OTHER.value
            ):
                if not payload.means_of_support_sponser.others_specify_2:
                    error_paths[
                        "additional_details.means_of_support_sponser.others_specify_2"
                    ] = "Please Enter Mandatory Field."

            if error_paths:
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    message=get_error_message(
                        error_message_code="LYIK_ERR_MISSING_MANDATORY_FIELDS"
                    ),
                    path_messages=error_paths,
                    actor="system",
                )

            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                actor="system",
                message="Verified successfully by the system.",
                # response=payload.model_dump(),
            )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=pe.message,
            )
        except Exception as e:
            logger.error(
                f"Something went wrong in Additional Travel Details verification: {e}"
            )
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
            )
