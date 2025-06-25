import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    OperationPluginSpec,
    OperationResponseModel,
    OperationStatus,
    PluginException,
    GenericFormRecordModel,
    invoke,
    TransformerResponseModel,
)
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
)
from .docket_utilities.docket_utilities import DocketUtilities
from ..models.pdf.pdf_model import EditableForm
from typing import Annotated, Dict
from typing_extensions import Doc
import logging
import json

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class DocketOperation(OperationPluginSpec):

    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: Annotated[int, Doc(" Record ID of the form record.")],
        status: Annotated[str, Doc("The status of the form.")],
        form_record: Annotated[GenericFormRecordModel, Doc("This is the form record.")],
        params: Dict | None,
    ) -> Annotated[
        OperationResponseModel,
        Doc("Reurns the operation response with operation status and message."),
    ]:
        parsed_form_model = Schengentouristvisa(form_record.model_dump())

        docket_util = DocketUtilities()

        mapped_data: EditableForm = docket_util.map_schengen_to_editable_form(
            schengen_visa_data=parsed_form_model
        )

        data_dict: Dict = mapped_data.model_dump()

        transformed_data: TransformerResponseModel = (
            await invoke.template_transform_data(
                transformer="01_SwitzerlandVisaForm",
                form_name="ttkform",
                record=data_dict,
            )
        )
        # Todo: Parse the form_record to the form model - DONE
        # Todo: Generate fillable PDF data model from the Form model - DONE
        # Todo: Convert the pdf data to a dictionary - DONE
        # Todo: Invoke transformer plugin with the template_id: (01_SwitzerlandVisaForm, {form_name}) - DONE
        # Return will be a transformer response model with a filled PDF

        # Todo: Take all the files from the form_record and create a zip of all the files in it, including the filled PDF
        # Todo: Return OperationResponseModel with a link to download the zip file

        pass
