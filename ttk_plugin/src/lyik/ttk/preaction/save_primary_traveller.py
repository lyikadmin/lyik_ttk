from typing_extensions import Doc, Annotated
from ..ttk_storage_util.ttk_storage import TTKStorage
import apluggy as pluggy
from lyikpluginmanager.annotation import RequiredVars
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
)
from ..models.forms.new_schengentouristvisa import Schengentouristvisa
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())

COLLECTION_NAME = "primary_travellers"


class SavePrimaryTraveller(PreActionProcessorSpec):
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
        This preaction processor will save the primary traveller into the primary_travellers collection.
        """
        logger.debug(f"Entering preaction with payload: {payload}")
        if not context or not context.config:
            logger.error(
                "No context or config found in context. Passing through SavePrimaryTraveller preaction."
            )
            return payload
        try:
            config = context.config
            conn_url = config.DB_CONN_URL
            if not conn_url:
                logger.error(
                    "Connection URL is missing in the config. Passing through SavePrimaryTraveller preaction."
                )
                return payload
            org_id = context.org_id
            if not org_id:
                logger.error(
                    "No org_id found in the context. Passing through SavePrimaryTraveller preaction."
                )
                return payload
            mongo = TTKStorage(db_conn_url=conn_url)
            record = Schengentouristvisa(**payload.model_dump())
            order_id = record.visa_request_information.visa_request.order_id
            if not order_id:
                logger.error(
                    "order_id missing in the payload. Passing through SavePrimaryTraveller preaction."
                )
                return payload
            result_id = await mongo.save_primary_info(
                collection_name=COLLECTION_NAME,
                org_id=org_id,
                order_id=order_id,
                data=record.model_dump(mode="json"),
            )
            if result_id:
                return GenericFormRecordModel(**record.model_dump(mode="json"))
            else:
                logger.warning("Failed to save Primay Traveller data.")
                return GenericFormRecordModel(**record.model_dump(mode="json"))
        except Exception as e:
            logger.error(
                f"Failed to perform SavePrimaryTraveller pre-action. Error: {str(e)}"
            )
