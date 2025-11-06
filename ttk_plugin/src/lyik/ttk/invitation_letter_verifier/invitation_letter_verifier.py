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
import base64
from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
    RootInvitationInvitationLetterGenerate,
)
from lyik.ttk.utils.document_api_client import DocumentAPIClient
from lyikpluginmanager.annotation import RequiredEnv
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

impl = pluggy.HookimplMarker(getProjectName())

API_INVITATION_LETTER_DOCUMENT = "Invitation Letter"


class InvitationLetterVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootInvitationInvitationLetterGenerate,
            Doc("Invitation letter info pane payload"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredEnv(
            ["TTK_API_BASE_URL", "TTK_DOCUMENT_LIST_API", "TTK_DOCUMENT_LIST_BY_ID_API"]
        ),
        Doc("Response after verifying the invitation letter."),
    ]:
        """
        This plugin will generate the invitation letter docx document using the transformer plugin.
        """
        GET_TEMPLATE_FROM_API = True
        try:
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

            if GET_TEMPLATE_FROM_API:
                token = context.token

                # Step 1: Decode outer token
                outer_payload = self._decode_jwt(token=token)

                # Step 2: Search for 'token'
                ttk_token = self.find_token_field(outer_payload)

                if not ttk_token:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="TTK token is missing.",
                    )

                # Step 3: Get the order_id from the record
                full_form_record = Schengentouristvisa(**context.record)
                order_id = (
                    full_form_record.visa_request_information.visa_request.order_id
                )
                if not order_id:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="Order ID is not present in the record",
                    )

                # Step: 4: Get the base_url and the document api endpoints
                base_url = os.getenv("TTK_API_BASE_URL")
                document_list_api_route = os.getenv("TTK_DOCUMENT_LIST_API")
                document_list_by_id_api_route = os.getenv("TTK_DOCUMENT_LIST_BY_ID_API")
                if (
                    not base_url
                    or not document_list_api_route
                    or not document_list_by_id_api_route
                ):
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="API Details are missing, unable to construct the url.",
                    )

                # Step 5: Initialize document api client
                doc_api_client = DocumentAPIClient(
                    base_url=base_url,
                    ttk_token=ttk_token,
                )

                # Step 6: Call Document List API
                doc_list_response = doc_api_client.get_document_list(
                    endpoint=document_list_api_route,
                    order_id=order_id,
                )

                # Step 7: Extract document list
                response_data = doc_list_response.get("responseData", [])
                if not response_data:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No response data received from document list API.",
                    )

                document_info_list = response_data[0].get("documentInfo", [])
                if not document_info_list:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No document info found in response.",
                    )

                # Step 8: Find Invitation Letter document
                invitation_doc = next(
                    (
                        doc
                        for doc in document_info_list
                        if doc.get("documentName") == API_INVITATION_LETTER_DOCUMENT
                    ),
                    None,
                )
                if not invitation_doc:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="Invitation Letter document not found in the document list.",
                    )

                invitation_doc_id = invitation_doc.get("documentId")

                # Step 9: Fetch Invitation Letter document details by ID
                doc_detail_response = doc_api_client.get_document_by_id(
                    endpoint=document_list_by_id_api_route,
                    order_id=order_id,
                    document_id=invitation_doc_id,
                )

                response_data = doc_detail_response.get("responseData", [])
                if not response_data:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No response data received from document details API.",
                    )

                doc_info = response_data[0].get("documentInfo", [])
                if not doc_info:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="No document info found for the given document ID.",
                    )

                actual_doc_base64 = doc_info[0].get("actualDocument")
                if not actual_doc_base64:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="Actual document data (base64) is missing in API response.",
                    )

                # Step 10: Decode Base64 and save to temp file
                decoded_bytes = base64.b64decode(actual_doc_base64)

                # Detect MIME from bytes
                kind = filetype.guess(decoded_bytes)

                if (
                    not kind
                    or kind.mime
                    != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ):
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message="The downloaded document is not a valid DOCX file.",
                    )

                # Safe name from documentName
                safe_doc_name = (
                    invitation_doc.get("documentName").replace(" ", "_").lower()
                )

                # Save document to a temporary file
                with tempfile.NamedTemporaryFile(
                    delete=False, prefix=f"{safe_doc_name}_", suffix=".docx"
                ) as tmp_file:
                    tmp_file.write(decoded_bytes)
                    temp_path = tmp_file.name

                # Step 11: Invoke the transformer to generate the filled document
                try:
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
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                transformer_res: TransformerResponseModel = (
                    await invoke.template_generate_docx(
                        org_id=context.org_id,
                        config=context.config,
                        record=context.record,
                        form_id=context.form_id,
                        additional_args={},
                        fetch_from_db_or_path=False,
                        form_name="word_template",
                        template=DocxTemplateModel(template="INVITATION_LETTER"),
                    )
                )

            if not transformer_res or not isinstance(
                transformer_res, TransformerResponseModel
            ):
                logger.error("Failed to transform the docx file.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    message=get_error_message(
                        error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                    ),
                )

            if transformer_res.status == TRANSFORMER_RESPONSE_STATUS.FAILURE:
                logger.error("Failed to generate the Docx file.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                    actor="system",
                    message=transformer_res.message,
                )

            docs: List[TemplateDocumentModel] = transformer_res.response
            doc = docs[0]

            if doc:
                # base64 encode the bytes
                encoded_content = base64.b64encode(doc.doc_content).decode("utf-8")

                html_link = f"""
                <div>
                    <p>Click below to download the generated document documents:</p>
                    <a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{encoded_content}"
                    download="{doc.doc_name or 'document.docx'}">
                    Download {doc.doc_name or 'Document'}
                    </a>
                </div>
                """

                parsed_payload = RootInvitationInvitationLetterGenerate(**payload)
                parsed_payload.generation_info_display = html_link

                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    message="",  # verified_successfully
                    actor="system",
                    response=parsed_payload.model_dump(),
                )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                id=None,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=pe.message,
                actor="system",
            )
        except Exception as e:
            logger.error(f"Failed verification process. {e}")
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
            return payload
        except Exception as e:
            logger.error(f"Something went wrong while decoding payload: {e}")

    def find_token_field(self, data: Dict[str, Any]) -> Union[str, None]:
        if isinstance(data, dict):
            provider_info = data.get("provider_info")
            if isinstance(provider_info, dict):
                token = provider_info.get("token")
                if isinstance(token, str):
                    return token

        return None
