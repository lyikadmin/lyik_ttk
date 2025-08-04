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
from ..models.forms.new_schengentouristvisa import (
    RootAdditionalDetails,
    SPONSORTYPE4,
    PAYMENTMETHOD6,
    EXPENSECOVERAGE5,
)
import logging
from ..utils.verifier_util import (
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
                    message="Internal configuration error. Please contact support.",
                    detailed_message="The payload is missing. Ensure the payload is properly available.",
                )

            error_paths = {}

            if payload.sponsorship_options_4 == SPONSORTYPE4.OTHER.value:
                if not payload.others_specify:
                    error_paths["additional_details.others_specify"] = (
                        "Please Enter Mandatory Field."
                    )

            if (
                payload.means_of_support_myself.support_means_other
                == PAYMENTMETHOD6.OTHER.value
            ):
                if not payload.means_of_support_myself.others_specify_1:
                    error_paths[
                        "additional_details.means_of_support_myself.others_specify_1"
                    ] = "Please Enter Mandatory Field."

            if (
                payload.means_of_support_sponser.coverage_other
                == EXPENSECOVERAGE5.OTHER.value
            ):
                if not payload.means_of_support_sponser.others_specify_2:
                    error_paths[
                        "additional_details.means_of_support_sponser.others_specify_2"
                    ] = "Please Enter Mandatory Field."

            if error_paths:
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    message="Please Enter Mandatory Fields.",
                    path_messages=error_paths,
                    actor="system",
                )

            # default_country_code = context.config.DEFAULT_COUNTRY_CODE

            # if not default_country_code:
            #     raise PluginException(
            #         message="Internal configuration error. Please contact support.",
            #         detailed_message="The DEFAULT_COUNTRY_CODE is missing in config.",
            #     )

            # payload_dict = payload.model_dump(mode="json")

            # ret = check_if_verified(payload=payload_dict)
            # if ret:
            #     return ret

            # national_id = payload.national_id
            # application_details = payload.app_details
            # family_eu = payload.family_eu

            # if national_id:
            #     aadhaar_number = national_id.aadhaar_number

            #     if aadhaar_number:
            #         try:
            #             valid_Aadhaar = validate_aadhaar_number(value=aadhaar_number)
            #             if valid_Aadhaar:
            #                 logger.info("Verified Aadhaar Number.")
            #         except Exception as e:
            #             raise PluginException(
            #                 message=str(e),
            #                 detailed_message="The user has entered an invalid Aadhaar number.",
            #             )

            # if (
            #     application_details
            #     and application_details.application_on_behalf.value == "YES"
            # ):
            #     # Check all required fields are filled
            #     missing_fields = []
            #     for field_name, value in application_details.model_dump().items():
            #         if not value:
            #             missing_fields.append(field_name)

            #     if missing_fields:
            #         logger.error(
            #             f"Missing or invalid fields in application details: {missing_fields}"
            #         )
            #         return VerifyHandlerResponseModel(
            #             status=VERIFY_RESPONSE_STATUS.FAILURE,
            #             actor="system",
            #             message="Please ensure all the details are filled if you are submitting the visa on behalf of the other person.",
            #         )

            #     # Check if the entered email is valid or not.
            #     try:
            #         valid_email = validate_email(
            #             value=application_details.email_address
            #         )
            #         if valid_email:
            #             logger.info("Email is validated.")
            #     except Exception as e:
            #         raise PluginException(
            #             message=str(e),
            #             detailed_message="The user has entered an invalid email address.",
            #         )

            #     # Check if the entered PIN Code is valid or not.
            #     try:
            #         pincode = validate_pincode(value=application_details.pin_code)
            #         if pincode:
            #             logger.info("Pincode Validated.")
            #     except Exception as e:
            #         raise PluginException(
            #             message=str(e),
            #             detailed_message="The user has entered an invalid pin code.",
            #         )

            #     # Check if the entered phone number is valid or not.
            #     try:
            #         valid_phone_number = validate_phone(
            #             value=application_details.telephone_mobile_number,
            #             country_code=default_country_code,
            #         )
            #         # payload.app_details.telephone_mobile_number = valid_phone_number
            #         if valid_phone_number:
            #             logger.info("Phone number is validated.")
            #     except Exception as e:
            #         raise PluginException(
            #             message=str(e),
            #             detailed_message="The user has entered an invalid phone number.",
            #         )

            # if family_eu and family_eu.is_family_member.value == "YES":
            #     # Check all required fields are filled
            #     missing_fields = []
            #     for field_name, value in family_eu.model_dump().items():
            #         if not value:
            #             missing_fields.append(field_name)

            #     if missing_fields:
            #         logger.error(
            #             f"Missing or invalid fields in Family Member of EU, EEA, Swiss, or UK National: {missing_fields}"
            #         )
            #         return VerifyHandlerResponseModel(
            #             status=VERIFY_RESPONSE_STATUS.FAILURE,
            #             actor="system",
            #             message="Please ensure all the details are filled if you have Family Member of EU, EEA, Swiss, or UK National.",
            #         )

            # logger.info("Additional Travel Details verified successfully.")
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
                message="Something went wrong while verification. Please contact support.",
            )
