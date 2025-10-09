from typing_extensions import Doc, Annotated

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
)
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())

# Unified Base preaction processor
from ._base_preaction import BaseUnifiedPreActionProcessor
from lyik.ttk.models.forms.schengentouristvisa import Schengentouristvisa

# preaction processors
from .impl_preaction_processors.client_action_guard import ClientActionGuard                #1
from .impl_preaction_processors.pct_completion import PctCompletion                         #2
from .impl_preaction_processors.normalize_country_codes import NormalizeCountryCodes        #3
from .impl_preaction_processors.invoke_appointment_api import InvokeAppointmentAPI          #4
from .impl_preaction_processors.normalize_fields import NormalizeFields                     #5
from .impl_preaction_processors.append_maker_id import AppendMakerId                        #6
from .impl_preaction_processors.copy_passport_details import CopyPassportAddress            #7
from .impl_preaction_processors.save_traveller import PreactionSavePrimaryTraveller         #8
from .impl_preaction_processors.save_traveller import PreactionSaveCoTravellers             #9

SCHENGEN_FORM_INDICATOR = "SCHENGEN"
class Schengen_Preactions(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[
            str,
            Doc("The action of the processor like: 'save' and 'submit'"),
        ],
        current_state: Annotated[
            str | None,
            Doc(
                "Current state of the record like: 'save', 'submit', 'approved'"
                "This state will be the already saved state of the record"
            ),
        ],
        new_state: Annotated[
            str | None,
            Doc(
                "New state of the record like: 'save', 'submit', 'approved'"
                "This state will be the new state which will be sent in the request"
            ),
        ],
        payload: Annotated[
            GenericFormRecordModel,
            Doc(
                "The payload of form record data to be pre processed to append maker_id in owner's list."
            ),
        ],
    ) -> Annotated[
        GenericFormRecordModel,
        Doc("The updated form record data."),
    ]:
        """
        This preaction processor will do all preaction processing required for TTK Schengen form.
        """
        # Parse to the form model
        try:
            form = Schengentouristvisa(**payload.model_dump())
        except Exception as exc:
            logger.error("Cannot parse model for preactions, skipping schengen preactions – %s", exc)
            return payload
        try:
            if not form.scratch_pad.form_indicator == SCHENGEN_FORM_INDICATOR:
                return payload  
        except Exception as exc:
            logger.error("Could not access the form indicator, skipping schengen preactions – %s", exc)
            return payload 
        
        processors_ordered_list = [
            ClientActionGuard,
            PctCompletion,
            NormalizeCountryCodes,
            InvokeAppointmentAPI,
            NormalizeFields,
            AppendMakerId,
            CopyPassportAddress,
            PreactionSavePrimaryTraveller,
            PreactionSaveCoTravellers
        ]
        try:
            for processor_cls in processors_ordered_list:
                processor: BaseUnifiedPreActionProcessor = processor_cls()
                payload = await processor.unified_pre_action_processor_impl(
                    context=context,
                    action=action,
                    current_state=current_state,
                    new_state=new_state,
                    payload=payload,
                )
        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload  # Important:  Return original payload on error to prevent data loss.
