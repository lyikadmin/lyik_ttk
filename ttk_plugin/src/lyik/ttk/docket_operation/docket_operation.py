import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    OperationPluginSpec,
    OperationResponseModel,
    OperationStatus,
    PluginException,
)
from typing import Annotated
from typing_extensions import Doc
import logging

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class DocketOperation(OperationPluginSpec):

    @impl
    async def process_operation(
        self, context: ContextModel, record_id, status, form_record, params
    ):
        # Todo: Parse form_record to Form model
        # Todo: Generate fillable PDF data model from the Form model
        # Todo: Convert the pdf data to a json object
        # Todo: Invoke transformer plugin with the template_id: (01_SwitzerlandVisaForm, {form_name})
        # Return will be a transformer response model with a filled PDF

        # Todo: Take all the files from the form_record and create a zip of all the files in it, including the filled PDF
        # Todo: Return OperationResponseModel with a link to download the zip file

        pass
