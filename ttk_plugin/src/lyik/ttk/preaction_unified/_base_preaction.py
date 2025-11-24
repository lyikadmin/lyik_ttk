from abc import ABC, abstractmethod
from typing_extensions import Annotated, Doc
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)
from lyik.ttk.utils.form_indicator import FormIndicator


class BaseUnifiedPreActionProcessor(ABC):
    @abstractmethod
    async def unified_pre_action_processor_impl(
        self,
        context: ContextModel,
        action: Annotated[str, Doc("The action like 'save' or 'submit'")],
        current_state: Annotated[str | None, Doc("Current saved state of the record")],
        new_state: Annotated[str | None, Doc("New incoming state of the record")],
        form_indicator: Annotated[FormIndicator | None, Doc("Form Indicator")],
        payload: Annotated[
            GenericFormRecordModel, Doc("Form record payload to process")
        ],
    ) -> Annotated[
        GenericFormRecordModel, Doc("The updated payload after processing.")
    ]:
        """
        Abstract method to be implemented by all preaction processors.
        """
        pass
