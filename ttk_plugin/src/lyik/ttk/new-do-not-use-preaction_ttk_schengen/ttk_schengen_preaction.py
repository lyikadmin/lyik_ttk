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


from .preaction_processors._base_preaction import BasePreActionProcessor

# preaction processors
from .preaction_processors.append_maker_id import PreactionAppendMakerId
from .preaction_processors.copy_passport_details import PreactionCopyPassportAddress
from .preaction_processors.descriptive_state import PreactionFormStatusDisplay
from .preaction_processors.normalize_country_codes import PreactionNormalizeCountryCodes
from .preaction_processors.order_status_update import PreactionOrderStatusUpdate
from .preaction_processors.pct_completion import PreactionPctCompletion
# from .preaction_processors.save_primary_traveller import PreactionSavePrimaryTraveller
from .preaction_processors.ttk_consultant import PreactionMakerCopyToPanes


class TTK_Schengen_Preaction(PreActionProcessorSpec):
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
        processors_ordered_list = [
            PreactionAppendMakerId,
            PreactionCopyPassportAddress,
            PreactionFormStatusDisplay,
            PreactionNormalizeCountryCodes,
            PreactionOrderStatusUpdate,
            PreactionPctCompletion,
            PreactionSavePrimaryTraveller,
            PreactionMakerCopyToPanes,
        ]
        try:
            for processor_cls in processors_ordered_list:
                processor: BasePreActionProcessor = processor_cls()
                payload = await processor.pre_action_processor(
                    context=context,
                    action=action,
                    current_state=current_state,
                    new_state=new_state,
                    payload=payload,
                )
        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload  # Important:  Return original payload on error to prevent data loss.
