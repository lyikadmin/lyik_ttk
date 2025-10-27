import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing import Annotated, List, Any, Dict
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import (
    RootAdditionalDocumentsPane,
    FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup,
    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptraveller,
    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller,
)
import logging
from lyik.ttk.utils.verifier_util import check_if_verified, validate_pincode
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


# VERIFIER_GENERATE_FILLED_GENERIC_TEMPLATES
class AdditionalDocumentsTravellerVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAdditionalDocumentsPane,
            Doc("Address payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response with the cards and generated template link"),
    ]:
        """
        This verifier generates link to download the zip of templates, and also creates the appropriate cards required to upload the modified files, if it doesn't exist already.
        """
        # payload_dict = payload.model_dump(mode="json")

        if not context or not context.config:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The context is missing or config is missing in context.",
            )

        full_form_record = context.record

        try:
            # Keep a reference to what was originally on the payload
            old_traveller_group = payload.additional_documents_traveller_group or []

            # Fast lookup:
            # key: document_name_display (or equivalent id),
            # value: existing traveller card (so we can preserve file_upload)
            existing_traveller_by_doc_name: Dict[
                str,
                RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller,
            ] = {}

            for traveller_card_wrapper in old_traveller_group:
                traveller_card = (
                    traveller_card_wrapper.additionaldocumentgrouptraveller.additional_documents_card_traveller
                )
                existing_traveller_by_doc_name[traveller_card.document_name_display] = (
                    traveller_card
                )

            # We'll accumulate:
            new_traveller_group: List[
                FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup
            ] = []

            templates_list: List[Any] = []

            # Walk all consultant cards in order
            for (
                consultant_card_wrapper
            ) in payload.additional_documents_consultant_group:
                consultant_card = (
                    consultant_card_wrapper.additionaldocumentgroupconsultant.additional_documents_card_consultant
                )

                document_name = consultant_card.document_name
                document_description = consultant_card.document_description
                template_file = consultant_card.file_upload

                # Track template file for ZIP bundling
                if template_file is not None:
                    templates_list.append(template_file)

                # See if we already had a traveller card for this doc name
                maybe_existing = existing_traveller_by_doc_name.get(document_name)

                if maybe_existing:
                    # Preserve the user's uploaded file, if any
                    preserved_upload = maybe_existing.file_upload
                else:
                    preserved_upload = None

                # Build traveller card wrapper in the expected schema
                new_traveller_group.append(
                    FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup(
                        additionaldocumentgrouptraveller=(
                            RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptraveller(
                                additional_documents_card_traveller=(
                                    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller(
                                        document_name=document_name,
                                        document_description=document_description,
                                        document_name_display=document_name,
                                        document_description_display=document_description,
                                        file_upload=preserved_upload,
                                    )
                                )
                            )
                        )
                    )
                )

            # For now this is a stub.
            templates_link = generate_template_zip(templates_list=templates_list, record=full_form_record)

            # Mutate payload to reflect final state
            payload.template_download_display = templates_link
            payload.additional_documents_traveller_group = new_traveller_group

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

def generate_template_zip(templates_list, record)->str:
    # One by one call the template generation class and pass the record and template path/doc model
        # Once i get back the response, i need to collect all, create a zip file, and save the file, then create a link for it.
    return "Example"