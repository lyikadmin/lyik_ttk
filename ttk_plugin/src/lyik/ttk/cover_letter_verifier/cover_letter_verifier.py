import apluggy as pluggy
from lyikpluginmanager import (
    invoke,
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
    TransformerResponseModel,
    TRANSFORMER_RESPONSE_STATUS,
    TemplateDocumentModel,
    DocxTemplateModel,
)

from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
    RootCoverLetterInfoGenerateCoverLetter,
)
from lyikpluginmanager.annotation import RequiredEnv

from lyik.ttk.utils.document_api_client import DocumentAPIClient
from typing import Annotated, List, Dict, Any, Union
from typing_extensions import Doc
from lyik.ttk.utils.message import get_error_message
import os
import jwt
import base64
import tempfile
import filetype
import logging

logger = logging.getLogger(__name__)

# Hook marker
impl = pluggy.HookimplMarker(getProjectName())

API_COVER_LETTER_DOCUMENT = "Cover Letter"

# -----------------------------------------------------------------------------
# Logging configuration helpers
# -----------------------------------------------------------------------------
# Enable verbose/trace-level logs when this env var is true-ish.
_VERBOSE_LOG_ENV = os.getenv("DOCUMENT_GEN_API_VERBOSE_LOGS", "true").lower()
VERBOSE_LOG_ENABLED = _VERBOSE_LOG_ENV in ("1", "true", "yes", "on")


def _debug_log(message: str, *args, **kwargs) -> None:
    """Log debug messages only when verbose logging is enabled."""
    if VERBOSE_LOG_ENABLED:
        logger.debug(message, *args, **kwargs)


def _log_exception(message: str, exc: Exception) -> None:
    """
    Log exceptions:
    - With full traceback and type when verbose logging is enabled.
    - As a simple error line otherwise.
    """
    if VERBOSE_LOG_ENABLED:
        logger.exception(
            "%s | type=%s, repr=%r",
            message,
            type(exc).__name__,
            exc,
        )
    else:
        logger.error("%s: %s", message, exc)


class CoverLetterVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootCoverLetterInfoGenerateCoverLetter,
            Doc("Cover letter info pane payload"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredEnv(
            ["TTK_API_BASE_URL", "TTK_DOCUMENT_LIST_API", "TTK_DOCUMENT_LIST_BY_ID_API"]
        ),
        Doc("Response after verifying the cover letter."),
    ]:
        """
        This plugin will generate the cover letter docx document using the transformer plugin.
        """
        GET_TEMPLATE_FROM_API = True
        _debug_log(
            "CoverLetterVerifier.verify_handler invoked | "
            "verbose=%s, org_id=%s, form_id=%s, has_token=%s, has_record=%s",
            VERBOSE_LOG_ENABLED,
            getattr(context, "org_id", None),
            getattr(context, "form_id", None),
            bool(getattr(context, "token", None)),
            bool(getattr(context, "record", None)),
        )

        try:
            # -----------------------------------------------------------------
            # Basic context validations
            # -----------------------------------------------------------------
            if not context or not context.config:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The context or config is missing.",
                )
            if not context.token:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Token is missing in context.",
                )
            if not context.record:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Record is missing in context.",
                )

            # -----------------------------------------------------------------
            # Path 1: Get template from TTK Document API
            # -----------------------------------------------------------------
            if GET_TEMPLATE_FROM_API:
                token = context.token
                _debug_log("Decoding outer JWT token")

                # Step 1: Decode outer token
                outer_payload = self._decode_jwt(token=token)
                _debug_log("Outer JWT decoded, type=%s", type(outer_payload).__name__)

                # Step 2: Search for 'token' field (TTK token)
                ttk_token = self.find_token_field(outer_payload)
                _debug_log("TTK token found: %s", bool(ttk_token))

                if not ttk_token:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="TTK token is missing.",
                    )

                # Step 3: Get the order_id from the record
                _debug_log("Parsing Schengentouristvisa record for order_id")
                full_form_record = Schengentouristvisa(**context.record)
                order_id = (
                    full_form_record.visa_request_information.visa_request.order_id
                )
                _debug_log("Extracted order_id=%s", order_id)

                if not order_id:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="Order ID is not present in the record",
                    )

                # Step 4: Get the base_url and the document API endpoints
                base_url = os.getenv("TTK_API_BASE_URL")
                document_list_api_route = os.getenv("TTK_DOCUMENT_LIST_API")
                document_list_by_id_api_route = os.getenv("TTK_DOCUMENT_LIST_BY_ID_API")

                _debug_log(
                    "Environment for TTK APIs | base_url_set=%s, list_api_set=%s, list_by_id_api_set=%s",
                    bool(base_url),
                    bool(document_list_api_route),
                    bool(document_list_by_id_api_route),
                )

                if (
                    not base_url
                    or not document_list_api_route
                    or not document_list_by_id_api_route
                ):
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="API details are missing, unable to construct the URL.",
                    )

                # Step 5: Initialize document API client
                _debug_log("Initializing DocumentAPIClient with base_url=%s", base_url)
                doc_api_client = DocumentAPIClient(
                    base_url=base_url,
                    ttk_token=ttk_token,
                )

                # Step 6: Call Document List API
                _debug_log(
                    "Calling get_document_list | endpoint=%s, order_id=%s",
                    document_list_api_route,
                    order_id,
                )
                doc_list_response = doc_api_client.get_document_list(
                    endpoint=document_list_api_route,
                    order_id=order_id,
                )
                _debug_log(
                    "Document list API response received | keys=%s",
                    list(doc_list_response.keys()),
                )

                # Step 7: Extract document list
                response_data = doc_list_response.get("responseData", [])
                _debug_log(
                    "Document list responseData length=%s",
                    len(response_data) if isinstance(response_data, list) else None,
                )

                if not response_data:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No response data received from document list API.",
                    )

                document_info_list = response_data[0].get("documentInfo", [])
                _debug_log(
                    "documentInfo length=%s",
                    (
                        len(document_info_list)
                        if isinstance(document_info_list, list)
                        else None
                    ),
                )

                if not document_info_list:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No document info found in response.",
                    )

                # Step 8: Find Cover Letter document
                _debug_log(
                    "Searching for Cover Letter document | target_name=%s",
                    API_COVER_LETTER_DOCUMENT,
                )
                cover_doc = next(
                    (
                        doc
                        for doc in document_info_list
                        if doc.get("documentName") == API_COVER_LETTER_DOCUMENT
                    ),
                    None,
                )
                _debug_log("Cover Letter document found=%s", bool(cover_doc))

                if not cover_doc:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="Cover Letter document not found in the document list.",
                    )

                cover_doc_id = cover_doc.get("documentId")
                _debug_log("Cover Letter documentId=%s", cover_doc_id)

                # Step 9: Fetch Cover Letter document details by ID
                _debug_log(
                    "Calling get_document_by_id | endpoint=%s, order_id=%s, document_id=%s",
                    document_list_by_id_api_route,
                    order_id,
                    cover_doc_id,
                )
                doc_detail_response = doc_api_client.get_document_by_id(
                    endpoint=document_list_by_id_api_route,
                    order_id=order_id,
                    document_id=cover_doc_id,
                )
                _debug_log(
                    "Document details API response received | keys=%s",
                    list(doc_detail_response.keys()),
                )

                response_data = doc_detail_response.get("responseData", [])
                _debug_log(
                    "Document details responseData length=%s",
                    len(response_data) if isinstance(response_data, list) else None,
                )

                if not response_data:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No response data received from document details API.",
                    )

                doc_info = response_data[0].get("documentInfo", [])
                _debug_log(
                    "Document details documentInfo length=%s",
                    len(doc_info) if isinstance(doc_info, list) else None,
                )

                if not doc_info:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No document info found for the given document ID.",
                    )

                actual_doc_base64 = doc_info[0].get("actualDocument")
                _debug_log(
                    "Actual document base64 present=%s",
                    bool(actual_doc_base64),
                )

                if not actual_doc_base64:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="Actual document data (base64) is missing in API response.",
                    )

                # Step 10: Decode Base64 and save to temp file
                _debug_log("Decoding base64 document content")
                decoded_bytes = base64.b64decode(actual_doc_base64)

                # Detect MIME from bytes
                kind = filetype.guess(decoded_bytes)
                _debug_log(
                    "Detected file type | kind=%s, extension=%s",
                    kind,
                    getattr(kind, "extension", None),
                )

                if not kind or kind.extension != "docx":
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="The downloaded document is not a valid DOCX file.",
                    )

                # Safe name from documentName
                safe_doc_name = cover_doc.get("documentName").replace(" ", "_").lower()
                _debug_log("Safe temp filename prefix=%s_", safe_doc_name)

                # Save document to a temporary file
                with tempfile.NamedTemporaryFile(
                    delete=False, prefix=f"{safe_doc_name}_", suffix=".docx"
                ) as tmp_file:
                    tmp_file.write(decoded_bytes)
                    temp_path = tmp_file.name

                _debug_log("Temporary DOCX file written at path=%s", temp_path)

                # Step 11: Invoke the transformer to generate the filled document
                try:
                    _debug_log(
                        "Invoking template_generate_docx with template path=%s",
                        temp_path,
                    )
                    transformer_res: TransformerResponseModel = (
                        await invoke.template_generate_docx(
                            org_id=context.org_id,
                            config=context.config,
                            record=context.record,
                            form_id=context.form_id,
                            additional_args={},
                            fetch_from_db_or_path=True,
                            form_name="",
                            template=DocxTemplateModel(template=temp_path),
                        )
                    )
                    _debug_log(
                        "template_generate_docx returned | type=%s, status=%s",
                        type(transformer_res).__name__,
                        getattr(transformer_res, "status", None),
                    )
                finally:
                    if os.path.exists(temp_path):
                        _debug_log("Removing temporary DOCX file at path=%s", temp_path)
                        os.remove(temp_path)

            # -----------------------------------------------------------------
            # Path 2: Use existing template from DB/path
            # -----------------------------------------------------------------
            else:
                _debug_log(
                    "GET_TEMPLATE_FROM_API is False, invoking template_generate_docx "
                    "with fetch_from_db_or_path=False"
                )
                transformer_res: TransformerResponseModel = (
                    await invoke.template_generate_docx(
                        org_id=context.org_id,
                        config=context.config,
                        record=context.record,
                        form_id=context.form_id,
                        additional_args={},
                        fetch_from_db_or_path=False,
                        form_name="word_template",
                        template=DocxTemplateModel(template="COVER_LETTER"),
                    )
                )
                _debug_log(
                    "template_generate_docx returned | type=%s, status=%s",
                    type(transformer_res).__name__,
                    getattr(transformer_res, "status", None),
                )

            # -----------------------------------------------------------------
            # Validate transformer response
            # -----------------------------------------------------------------
            if not transformer_res or not isinstance(
                transformer_res, TransformerResponseModel
            ):
                logger.error("Failed to transform the DOCX file: invalid response.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    message=get_error_message(
                        error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                    ),
                )

            if transformer_res.status == TRANSFORMER_RESPONSE_STATUS.FAILURE:
                logger.error(
                    "Failed to generate the DOCX file. Transformer status=FAILURE, message=%s",
                    transformer_res.message,
                )
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    message=transformer_res.message,
                )

            docs: List[TemplateDocumentModel] = transformer_res.response
            _debug_log(
                "Transformer response contains %s documents",
                len(docs) if isinstance(docs, list) else None,
            )
            doc = docs[0] if docs else None

            if doc:
                _debug_log(
                    "Preparing HTML download link for document | doc_name=%s, content_length=%s",
                    getattr(doc, "doc_name", None),
                    len(doc.doc_content) if getattr(doc, "doc_content", None) else None,
                )
                # base64 encode the bytes
                encoded_content = base64.b64encode(doc.doc_content).decode("utf-8")

                html_link = f"""
                <div>
                    <p>Click below to download the generated document file:</p>
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{encoded_content}"
                    download="{doc.doc_name or 'document.docx'}">
                    Download {doc.doc_name or 'Document'}
                    </a>
                </div>
                """

                parsed_payload = RootCoverLetterInfoGenerateCoverLetter(**payload)
                parsed_payload.generation_info_display = html_link

                _debug_log("Returning DATA_ONLY VerifyHandlerResponseModel")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    message="",  # verified_successfully
                    actor="system",
                    response=parsed_payload.model_dump(),
                )

            # If we reached here with no doc, treat as failure
            logger.error("Transformer response did not contain any document.")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=get_error_message(
                    error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                ),
            )

        except PluginException as pe:
            # Plugin-level controlled exception
            _debug_log(
                "PluginException caught in verify_handler | message=%s, detailed_message=%s",
                pe.message,
                getattr(pe, "detailed_message", None),
            )
            logger.error(getattr(pe, "detailed_message", pe.message))
            return VerifyHandlerResponseModel(
                id=None,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=pe.message,
                actor="system",
            )
        except Exception as e:
            # Any unexpected error – this is where the mysterious "0" is likely coming from.
            _log_exception("Failed verification process", e)
            return VerifyHandlerResponseModel(
                id=None,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=get_error_message(
                    error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                ),
                actor="system",
            )

    def _decode_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, algorithms=["HS256"], options={"verify_signature": False}
            )
            _debug_log(
                "_decode_jwt succeeded | payload_type=%s, keys=%s",
                type(payload).__name__,
                list(payload.keys()) if isinstance(payload, dict) else None,
            )
            return payload
        except Exception as e:
            _log_exception("Something went wrong while decoding JWT payload", e)
            # Propagate the error up, so we don't silently continue with None
            raise

    def find_token_field(self, data: Dict[str, Any]) -> Union[str, None]:
        _debug_log(
            "find_token_field called | data_type=%s",
            type(data).__name__,
        )
        if isinstance(data, dict):
            provider_info = data.get("provider_info")
            _debug_log(
                "find_token_field: provider_info_type=%s",
                type(provider_info).__name__ if provider_info is not None else None,
            )
            if isinstance(provider_info, dict):
                token = provider_info.get("token")
                _debug_log(
                    "find_token_field: token_present=%s, token_type=%s",
                    bool(token),
                    type(token).__name__ if token is not None else None,
                )
                if isinstance(token, str):
                    return token

        _debug_log("find_token_field: no token field found, returning None")
        return None
