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
    DocumentModel,
)

from lyik.ttk.models.forms.schengentouristvisa import (
    RootCoverLetterInfoGenerateCoverLetter,
)

from lyik.ttk.utils.flatten_record import JSONFlattener
import base64

from lyik.ttk.utils.verifier_util import check_if_verified
from typing import Annotated, List, Dict
from typing_extensions import Doc
from lyik.ttk.utils.message import get_error_message
import logging


logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


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
        Doc("Response after verifying the cover letter."),
    ]:
        """
        This plugin will generate the cover letter docx document using the transformer plugin.
        """

        try:
            if not context or not context.config:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The context or config is missing.",
                )

            json_flattener = JSONFlattener()
            flat_data = json_flattener.flatten(data=context.record)

            transformer_res: TransformerResponseModel = (
                await invoke.template_generate_docx(
                    org_id=context.org_id,
                    config=context.config,
                    record=flat_data,
                    form_id=context.form_id,
                    additional_args={},
                    fetch_from_db_or_path=False,
                    form_name="word_template",
                    template="COVER_LETTER",
                )
            )

            if not transformer_res or not isinstance(
                transformer_res, TransformerResponseModel
            ):
                logger.error("Failed to transform the docx file.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    actor="system",
                    message=get_error_message(
                        error_message_code="LYIK_ERR_SOMETHING_WENT_WRONG"
                    ),
                )

            if transformer_res.status == TRANSFORMER_RESPONSE_STATUS.FAILURE:
                logger.error("Failed to generate the Docx file.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    actor="system",
                    message=get_error_message(
                        error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                    ),
                )

            docs: List[TemplateDocumentModel] = transformer_res.response
            doc = docs[0]

            if doc:
                # document_model = DocumentModel(
                #     doc_name=doc.doc_name,
                #     doc_type=doc.doc_type,
                #     doc_content=doc.doc_content,
                # )

                # document_dict = document_model.model_dump()

                # payload.covering_letter_card.cover_upload = document_dict

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
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                message=pe.message,
                actor="system",
            )
        except Exception as e:
            logger.error(f"Failed verification process. {e}")
            return VerifyHandlerResponseModel(
                id=None,
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
                actor="system",
            )
