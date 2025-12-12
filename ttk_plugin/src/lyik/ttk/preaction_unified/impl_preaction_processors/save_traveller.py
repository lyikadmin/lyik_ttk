from typing_extensions import Doc, Annotated
from lyik.ttk.ttk_storage_util.ttk_storage import TTKStorage
import apluggy as pluggy
from lyikpluginmanager.annotation import RequiredVars
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)

from lyik.ttk.models.generated.universal_model import UniversalModel
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

from .._base_preaction import BaseUnifiedPreActionProcessor
from lyik.ttk.utils.form_indicator import FormIndicator



PRIMARY_COLLECTION_NAME = "primary_travellers"
CO_TRAVELLER_COLLECTION_NAME = "co_travellers"
PRIMARY_TRAVELLER = "Primary"
CO_TRAVELLER = "Co-traveller"


class PreactionSavePrimaryTraveller(BaseUnifiedPreActionProcessor):
    async def unified_pre_action_processor_impl(
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
        form_indicator: Annotated[
            FormIndicator,
            Doc("The form indicator for the form"),
        ],
        payload: Annotated[
            GenericFormRecordModel,
            Doc("The payload of form record data."),
        ],
    ) -> Annotated[
        GenericFormRecordModel,
        RequiredVars(["DB_CONN_URL"]),
        Doc("The updated form record data."),
    ]:
        """
        This preaction processor will save the primary traveller into the primary_travellers collection.
        """
        # logger.debug(f"Entering preaction with payload: {payload}")
        if not context or not context.config:
            logger.error(
                "No context or config found in context. Passing through SavePrimaryTraveller preaction."
            )
            return payload
        try:
            record = UniversalModel(**payload.model_dump())
            traveller_type = record.visa_request_information.visa_request.traveller_type
            if not traveller_type:
                logger.warning(
                    "Traveller type is missing in payload. Skipping SavePrimaryTraveller preaction."
                )
                return payload
            if traveller_type == PRIMARY_TRAVELLER:
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

                order_id = record.visa_request_information.visa_request.order_id
                if not order_id:
                    logger.error(
                        "order_id missing in the payload. Passing through SavePrimaryTraveller preaction."
                    )
                    return payload
                result_id = await mongo.save_primary_info(
                    collection_name=PRIMARY_COLLECTION_NAME,
                    org_id=org_id,
                    order_id=order_id,
                    data=record.model_dump(mode="json"),
                )
                if result_id:
                    logger.info("Saved the Primary Traveller data.")
                    return payload
                else:
                    logger.warning("Failed to save Primay Traveller data.")
                    return payload
            else:
                logger.info("Traveller is Co-traveller")
                return payload
        except Exception as e:
            logger.error(
                f"Failed to perform SavePrimaryTraveller pre-action. Error: {str(e)}"
            )
            return payload


class PreactionSaveCoTravellers(BaseUnifiedPreActionProcessor):
    async def unified_pre_action_processor_impl(
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
        form_indicator: Annotated[
            FormIndicator,
            Doc("The form indicator for the form"),
        ],
        payload: Annotated[
            GenericFormRecordModel,
            Doc("The payload of form record data."),
        ],
    ) -> Annotated[
        GenericFormRecordModel,
        RequiredVars(["DB_CONN_URL"]),
        Doc("The updated form record data."),
    ]:
        """
        This preaction processor will save the co-travellers into the co_travellers collection.
        """

        # logger.debug(f"Entering preaction with payload: {payload}")
        if not context or not context.config:
            logger.error(
                "No context or config found in context. Passing through PreactionSaveCoTravellers preaction."
            )
            return payload

        try:
            record = UniversalModel(**payload.model_dump())
            traveller_type = record.visa_request_information.visa_request.traveller_type
            if not traveller_type:
                logger.warning(
                    "Traveller type is missing in payload. Skipping PreactionSaveCoTravellers preaction."
                )
                return payload

            if traveller_type == CO_TRAVELLER:
                config = context.config
                conn_url = config.DB_CONN_URL
                if not conn_url:
                    logger.error(
                        "Connection URL is missing in the config. Passing through PreactionSaveCoTravellers preaction."
                    )
                    return payload
                org_id = context.org_id
                if not org_id:
                    logger.error(
                        "No org_id found in the context. Passing through PreactionSaveCoTravellers preaction."
                    )
                    return payload
                mongo = TTKStorage(db_conn_url=conn_url)

                order_id = record.visa_request_information.visa_request.order_id
                if not order_id:
                    logger.error(
                        "order_id missing in the payload. Passing through PreactionSaveCoTravellers preaction."
                    )
                    return payload

                traveller_id = record.visa_request_information.visa_request.traveller_id

                result_id = await mongo.save_or_update_co_traveller(
                    collection_name=CO_TRAVELLER_COLLECTION_NAME,
                    org_id=org_id,
                    order_id=order_id,
                    traveller_id=traveller_id,
                    traveller_data=record.model_dump(mode="json"),
                )
                if result_id:
                    logger.info("Saved the Co-traveller data.")
                    return payload
                else:
                    logger.warning("Failed to save Co-traveller data.")
                    return payload
            else:
                logger.info("Traveller is the primary traveller.")
                return payload
        except Exception as e:
            logger.error(
                f"Failed to perform PreactionSaveCoTravellers pre-action. Error: {str(e)}"
            )
            return payload
