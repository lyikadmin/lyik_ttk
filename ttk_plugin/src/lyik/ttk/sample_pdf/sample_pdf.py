from typing import List

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    GenericFormRecordModel,
    PluginException,
    invoke,
    OperationPluginSpec,
    OperationResponseModel,
    OperationStatus,
    TransformerResponseModel,
    TemplateDocumentModel,
)
from ..models.forms.schengentouristvisa import Schengentouristvisa
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())


class Sample_PDF(OperationPluginSpec):
    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: int,
        status: str,
        form_record: GenericFormRecordModel,
        params: dict | None,
    ):
        try:
            response: TransformerResponseModel = await invoke.template_generate_pdf(
                config=context.config,
                org_id=context.org_id,
                form_id=context.form_id,
                form_name="funcA",
                template_id="01_SAMPLE",
                record=form_record,
                additional_args={"sample_key": {"Name": "Rahul Choudhury"}},
            )
            template_docs: List[TemplateDocumentModel] = response.response
            doc = template_docs[0]
            with open("Sample_pdf.pdf", "wb") as f:
                f.write(doc.doc_content)
            return OperationResponseModel(
                status=OperationStatus.SUCCESS,
                message="Successfully generated the sample pdf",
            )
        except Exception as e:
            logger.exception(e)
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message="Failed to transform and generate pdf",
            )
