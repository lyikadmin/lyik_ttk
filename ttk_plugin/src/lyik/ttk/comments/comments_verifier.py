import apluggy as pluggy
from Crypto.Cipher import AES
import io
import zipfile
import base64
from Crypto.Util.Padding import pad
from lyikpluginmanager import (
    invoke,
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    TransformerResponseModel,
    TRANSFORMER_RESPONSE_STATUS,
    TemplateDocumentModel,
    DocxTemplateModel,
    DocumentModel,
    DocMeta,
    DocQueryGenericModel,
)
from lyik.ttk.utils.utils import get_personas_from_encoded_token
from datetime import datetime
from typing import Annotated, List, Any, Dict
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import (
    RootCommentsPane, RootCommentsPaneCCard, FieldGrpRootCommentsPaneCCardCRow
)
from lyikpluginmanager.annotation import RequiredVars
import logging
from lyik.ttk.utils.verifier_util import check_if_verified, validate_pincode
from lyik.ttk.utils.message import get_error_message
from lyik.ttk.utils.flatten_record import JSONFlattener
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


# VERIFIER_GENERATE_FILLED_GENERIC_TEMPLATES
class CommentsVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootCommentsPane,
            Doc("Address payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response with the card including the new message"),
    ]:
        """
        This cta verifier adds a comment to the comments table.
        """
        payload = RootCommentsPane.model_validate(payload)
        # payload_dict = payload.model_dump(mode="json")

        if not context or not context.config or not context.token:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The context is missing or config is missing in context.",
            )

        try:

            token = context.token
            personas: List[str] = get_personas_from_encoded_token(token)

            user_type = "Unknown"
            if "MKR" in personas:
                user_type = "Maker"
            if "SME" in personas:
                user_type = "SME"

            new_comment = payload.comment_input

            if not new_comment:
                return VerifyHandlerResponseModel(
                    actor=ACTOR,
                    message=f"Verified by the {ACTOR}",
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                )

            # IST is UTC+05:30
            IST = timezone(timedelta(hours=5, minutes=30))
            # Current time in IST
            now_ist = datetime.now(IST)
            # Format like: Wed Sep 17 2025 12:19
            timestamp = now_ist.strftime("%a %b %d %Y %H:%M")
            

            comment_row = FieldGrpRootCommentsPaneCCardCRow(user=user_type, timestamp=timestamp, comments=new_comment)

            if not payload.c_card:
                payload.c_card = RootCommentsPaneCCard()
            
            if not payload.c_card.c_row:
                payload.c_card.c_row = [comment_row]
            else:
                payload.c_card.c_row.append(comment_row)
            
            payload.comment_input = ""


            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=f"Verified by the {ACTOR}",
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                response=payload.model_dump(),
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
