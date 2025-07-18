from typing_extensions import Doc, Annotated
from ..ttk_storage_util.ttk_storage import TTKStorage
import apluggy as pluggy
from lyikpluginmanager.annotation import RequiredEnv, RequiredVars
from lyikpluginmanager import (
    PreActionProcessorSpec,
    getProjectName,
    ContextModel,
    GenericFormRecordModel,
)
from typing import List, Dict, Any
from ..utils.add_on_loader_util import AddonLoader
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    RootAddons,
    FieldGrpRootAddonsAddonGroup,
    RootAddonsAddonGroupAddonservicegroup,
    RootAddonsAddonGroupAddonservicegroupAddonCard,
    FieldGrpRootAddonsAddonGroupAddonservicegroupAddonCardAddonOnService,
)
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())

PRIMARY_TRAVELLER = "Primary"
CO_TRAVELLER_COLLECTION_NAME = "co_travellers"


class PreactionAddonServices(PreActionProcessorSpec):
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
            Doc("The payload of form record data."),
        ],
    ) -> Annotated[
        GenericFormRecordModel,
        RequiredVars(["DB_CONN_URL"]),
        RequiredEnv(["CRED_FILES_MOUNT_PATH", "ADDON_FILE"]),
        Doc("The updated form record data."),
    ]:
        try:
            parsed_form_rec = Schengentouristvisa(**payload.model_dump())

            # record_id = context.record_id

            # parsed_form_rec.addons.record_id = record_id

            # Extract traveller type and validate
            traveller_type = (
                parsed_form_rec.visa_request_information.visa_request.traveller_type
            )
            if not traveller_type:
                logger.warning(
                    "Traveller type is missing in payload. Skipping PreactionAddonServices preaction."
                )
                return payload

            # Continue only for primary traveller
            if traveller_type == PRIMARY_TRAVELLER:
                # Validate context and config
                if not context or not context.config:
                    logger.error("The context or config is missing.")
                    return payload
                config = context.config

                conn_url = config.DB_CONN_URL
                if not conn_url:
                    logger.error("DB_CONN_URL is missing in the config.")
                    return payload

                # Validate org_id and order_id
                org_id = context.org_id
                if not org_id:
                    logger.error("org_id is missing in the context.")
                    return payload

                order_id = (
                    parsed_form_rec.visa_request_information.visa_request.order_id
                )
                if not order_id:
                    logger.error("order_id is missing in the payload.")
                    return payload

                addon_group_list: List[FieldGrpRootAddonsAddonGroup] = []

                addon_on_service: List[
                    FieldGrpRootAddonsAddonGroupAddonservicegroupAddonCardAddonOnService
                ] = []

                # Try extracting existing add-on data from parsed form
                addon_card = (
                    parsed_form_rec.addons
                    and parsed_form_rec.addons.addon_group
                    and parsed_form_rec.addons.addon_group[0].addonservicegroup
                    and parsed_form_rec.addons.addon_group[
                        0
                    ].addonservicegroup.addon_card
                )

                if (
                    addon_card
                    and addon_card.addon_on_service
                    and addon_card.addon_on_service[0].addon_id
                ):
                    # Reuse existing addon_on_service list
                    addon_on_service = addon_card.addon_on_service
                    logger.info("Using existing add-on service list from form.")
                else:
                    # Fallback: load add-ons from file
                    file_path = os.path.join(
                        os.getenv("CRED_FILES_MOUNT_PATH"),
                        os.getenv("ADDON_FILE"),
                    )
                    addon_loader = AddonLoader(file_path=file_path)
                    data: List[Dict] = addon_loader.load_addons()
                    if data:
                        addon_on_service = [
                            FieldGrpRootAddonsAddonGroupAddonservicegroupAddonCardAddonOnService(
                                addon_id=str(addon["id"]),
                                add_ons=addon["addon_name"],
                                amount_display=f"₹ {addon['charges']}",
                                amount_internal=int(addon["charges"]),
                            )
                            for addon in data
                        ]
                        logger.info("Loaded add-on services from file.")
                    else:
                        logger.error("No data found for the addon items.")
                        return payload

                # Create the addon for the primary traveller
                primary_traveller_name = (
                    parsed_form_rec.passport.passport_details.first_name
                    if parsed_form_rec.passport
                    and parsed_form_rec.passport.passport_details
                    else "Traveller 1"
                )
                # Add HTML style to traveller name
                primary_traveller_name = self._stylize_traveller_name(
                    name=primary_traveller_name
                )

                primary_addon_group = self._create_addon_group(
                    traveller_id=parsed_form_rec.visa_request_information.visa_request.traveller_id,
                    traveller_name=primary_traveller_name,
                    addon_on_service=addon_on_service,
                )

                addon_group_list.append(primary_addon_group)

                # Initialize storage and fetch all co-travellers
                ttk_storage = TTKStorage(db_conn_url=conn_url)
                fetched_data: Dict[str, Dict[str, Any]] = (
                    await ttk_storage.get_all_co_travellers(
                        collection_name=CO_TRAVELLER_COLLECTION_NAME,
                        org_id=org_id,
                        order_id=order_id,
                    )
                )
                if fetched_data:
                    # Process each co-traveller and construct their addon group
                    for index, (traveller_id, traveller_data) in enumerate(
                        fetched_data.items(), start=2
                    ):
                        co_traveller = Schengentouristvisa(**traveller_data)

                        # Fallback to "Traveller {index}" if name missing
                        traveller_name = (
                            co_traveller.passport.passport_details.first_name
                            if co_traveller.passport
                            and co_traveller.passport.passport_details
                            else f"Traveller {index}"
                        )

                        traveller_name = self._stylize_traveller_name(
                            name=traveller_name
                        )

                        addon_group = self._create_addon_group(
                            traveller_id=traveller_id,
                            traveller_name=traveller_name,
                            addon_on_service=addon_on_service,
                        )

                        addon_group_list.append(addon_group)

                # Update parsed form with built addon group list
                # parsed_form_rec.addons.record_id = str(record_id)
                if not parsed_form_rec.addons:
                    parsed_form_rec.addons = RootAddons()
                parsed_form_rec.addons.addon_group = addon_group_list
                logger.info("Successfully populated addon services for travellers.")

                # Return the updated payload
                return GenericFormRecordModel(**parsed_form_rec.model_dump())

            else:
                logger.info(
                    "Traveller is a Co-traveller. Skipping addon service logic."
                )
                return payload
        except Exception as e:
            logger.error(
                f"Exception raised while processing PreactionAddonServices. {str(e)}"
            )
            return payload

    def _create_addon_group(
        self,
        traveller_id: str,
        traveller_name: str,
        addon_on_service: List[
            FieldGrpRootAddonsAddonGroupAddonservicegroupAddonCardAddonOnService
        ],
    ) -> FieldGrpRootAddonsAddonGroup:
        addon_group = FieldGrpRootAddonsAddonGroup(
            addonservicegroup=RootAddonsAddonGroupAddonservicegroup(
                addon_card=RootAddonsAddonGroupAddonservicegroupAddonCard(
                    traveller_id=traveller_id,
                    traveler_name=traveller_name,
                    addon_on_service=addon_on_service,
                )
            )
        )
        return addon_group

    def _stylize_traveller_name(self, name: str) -> str:
        return f'<div style="display: flex; justify-content: center;"><span style="font-size: 20px; font-weight: bold; color: #3BB9EB;">{name}</span></div>'
