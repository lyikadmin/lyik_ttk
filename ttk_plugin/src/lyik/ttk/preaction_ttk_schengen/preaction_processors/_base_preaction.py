from abc import ABC, abstractmethod
from typing_extensions import Annotated, Doc
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)


class BasePreActionProcessor(ABC):
    @abstractmethod
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, Doc("The action like 'save' or 'submit'")],
        current_state: Annotated[str | None, Doc("Current saved state of the record")],
        new_state: Annotated[str | None, Doc("New incoming state of the record")],
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
