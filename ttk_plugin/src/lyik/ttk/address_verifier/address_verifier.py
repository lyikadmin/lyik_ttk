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
from lyik.ttk.models.forms.schengentouristvisa import RootResidentialAddress
import logging
from lyik.ttk.utils.verifier_util import check_if_verified, validate_pincode
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class AddressVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootResidentialAddress,
            Doc("Address payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Address."),
    ]:
        """
        This verifier verifies the Address details.
        Just checks if the pincode is valid when visible.
        """
        payload_dict = payload.model_dump(mode="json")

        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        try:
            same_as_passport = payload.same_as_passport_address
            if same_as_passport and same_as_passport.value == "SAME_AS_PASS_ADDR":
                if payload.residential_address_card_v2:
                    pincode = payload.residential_address_card_v2.pin_code
                    if pincode:
                        try:
                            res = validate_pincode(value=pincode)
                            if res:
                                logger.info("PIN Code is valid.")
                        except Exception as e:
                            raise PluginException(
                                message=str(e),
                                detailed_message="The PIN Code format is invalid.",
                            )
            else:
                if payload.residential_address_card_v1:
                    pincode = payload.residential_address_card_v1.pin_code
                    if pincode:
                        try:
                            res = validate_pincode(value=pincode)
                            if res:
                                logger.info("PIN Code is valid.")
                        except Exception as e:
                            raise PluginException(
                                message=str(e),
                                detailed_message="The PIN Code format is invalid.",
                            )

            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=f"Verified by the {ACTOR}",
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
            )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=pe.message,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        except Exception as e:
            logger.error(f"Unhandled exception occurred. Error: {str(e)}")
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )
