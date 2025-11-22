from typing_extensions import Doc, Annotated
from typing import List, Type

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
    PluginException,
)
from lyikpluginmanager.annotation import RequiredVars
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())

# Unified Base preaction processor
from ._base_preaction import BaseUnifiedPreActionProcessor
from lyik.ttk.utils.form_indicator import FormIndicator, get_form_indicator

# PREACTION PROCESSORS
# 1 - Semi - Universal. Only for 
from .impl_preaction_processors.client_action_guard import ClientActionGuard

# 2 - For all, but Specific. Need to add the expected infopanes.
from .impl_preaction_processors.pct_completion import PctCompletion

# 3 - Universal
from .impl_preaction_processors.normalize_country_codes import NormalizeCountryCodes

# 4 - Semi - Universal for some. Only for Forms with Appointment Section. (Maybe universal with Appointment Model required)
from .impl_preaction_processors.invoke_appointment_api import InvokeAppointmentAPI

# 5 - Universal
from .impl_preaction_processors.normalize_fields import NormalizeFields

# from .impl_preaction_processors.append_maker_id import AppendMakerId  # 6
# 7 - Universal, but should be generalised a bit more if district is required later.
from .impl_preaction_processors.copy_passport_details import CopyPassportAddress

# 8 - Universal
from .impl_preaction_processors.save_traveller import PreactionSavePrimaryTraveller

# 9 - Universal
from .impl_preaction_processors.save_traveller import PreactionSaveCoTravellers


FORM_WITH_APPOINTMENT_PREACTION_LIST = [
    ClientActionGuard,
    PctCompletion,
    NormalizeCountryCodes,
    InvokeAppointmentAPI,
    NormalizeFields,
    # AppendMakerId,
    CopyPassportAddress,
    PreactionSavePrimaryTraveller,
    PreactionSaveCoTravellers,
]

FORM_WITHOUT_APPOINTMENT_PREACTION_LIST = [
    ClientActionGuard,
    PctCompletion,
    NormalizeCountryCodes,
    # InvokeAppointmentAPI, # - No Appointment Section
    NormalizeFields,
    # AppendMakerId,
    CopyPassportAddress,
    PreactionSavePrimaryTraveller,
    PreactionSaveCoTravellers,
]

BASIC_FORM_PREACTION_LIST = [
    PctCompletion,
    NormalizeCountryCodes,
    NormalizeFields,
    PreactionSavePrimaryTraveller,
    PreactionSaveCoTravellers,
]

PreactionCls = Type[BaseUnifiedPreActionProcessor]


def _get_processors_for_form_indicator(
    form_indicator: FormIndicator,
) -> List[PreactionCls]:
    if form_indicator in (FormIndicator.SCHENGEN, FormIndicator.SAUDI_ARABIA):
        return FORM_WITH_APPOINTMENT_PREACTION_LIST
    elif form_indicator in (
        FormIndicator.SINGAPORE,
        FormIndicator.UAE,
        FormIndicator.INDONESIA,
    ):
        return FORM_WITHOUT_APPOINTMENT_PREACTION_LIST
    return BASIC_FORM_PREACTION_LIST


class Central_Preaction(PreActionProcessorSpec):
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
        RequiredVars(["DB_CONN_URL"]),
        Doc("The updated form record data."),
    ]:
        """
        This preaction processor will do all preaction processing required for TTK forms.
        """
        # Parse to the form model
        form_indicator = get_form_indicator(form_rec=payload)

        payload_original = GenericFormRecordModel.model_validate(payload.model_dump())

        processors_ordered_list = _get_processors_for_form_indicator(
            form_indicator=form_indicator
        )
        try:
            for processor_cls in processors_ordered_list:
                processor: BaseUnifiedPreActionProcessor = processor_cls()
                payload = await processor.unified_pre_action_processor_impl(
                    context=context,
                    action=action,
                    current_state=current_state,
                    new_state=new_state,
                    form_indicator=form_indicator,
                    payload=payload,
                )
        except PluginException as pe:
            logger.warning("Preaction hard-stop: %s", str(pe))
            raise  # bubble up explicit plugin exception
        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload_original  # Return original payload on error to prevent data loss.

        return payload
