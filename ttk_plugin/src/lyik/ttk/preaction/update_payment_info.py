from typing import Dict, List, Optional
from pydantic import Field, BaseModel
from typing_extensions import Doc, Annotated

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
    PluginException,
    invoke,
)
from lyikpluginmanager.models import (
    LPSRecord,
    PayUParams,
    LPSStatus,
    GatewayResponseModel,
)
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    FieldGrpRootAddonsAddonServiceAddonCartRow,
    RootAddonsAddonService,
    RootAddonsAddonServiceInitialization,
    RootAddons
)
import logging
import base64
import json
from ..models.payment.addon_models import AddonSummaryItem, GroupedAddonSummaryItem
from ..utils.payment import group_addon_summary

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())

LPS_STATUS_USER_STATUS_MAP = {
    LPSStatus.PAY_SUCCESS.value: "Success | Completed",
    LPSStatus.PAY_IN_PROGRESS.value: "Success | In Progress",
    LPSStatus.PAY_INITIATED.value: "Payment Pending",
    LPSStatus.PAY_FAILURE.value: "Failure",
    LPSStatus.PAY_REJECTED.value: "Rejected",
}


class UpdatePaymentInfo(PreActionProcessorSpec):
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
        This preaction processor will append maker_id into the _owner list of the record.
        """
        try:

            # Define allowed states for rows in addon cart.
            allowed_states = {
                LPSStatus.PAY_FAILURE,
                LPSStatus.PAY_SUCCESS,
                LPSStatus.PAY_IN_PROGRESS,
            }
            logger.debug(f"Allowed LPS states: {allowed_states}")

            full_parsed_record = Schengentouristvisa(**payload.model_dump())

            if not full_parsed_record.addons:
                full_parsed_record.addons = RootAddons()

            if not full_parsed_record.addons.addon_service:
                 full_parsed_record.addons.addon_service = RootAddonsAddonService()

            if not full_parsed_record.addons.addon_service_initialization:
                 full_parsed_record.addons.addon_service_initialization = RootAddonsAddonServiceInitialization()

            addon_rows = (
                full_parsed_record.addons.addon_service_initialization.addon_cart_row
                if full_parsed_record.addons.addon_service_initialization
                else []
            )
            logger.debug(f"Fetched {len(addon_rows)} addon_rows from initialization")

            txn_ids = {row.txnid for row in addon_rows if row.txnid}
            logger.debug(f"Extracted txn_ids from initialization rows: {txn_ids}")

            lps_records: List[LPSRecord] = []

            for txn_id in txn_ids:
                lps = await invoke.get_payment_status(
                    config=context.config,
                    org_id=context.org_id,
                    record_id=None,
                    txn_id=txn_id,
                )
                lps_records.extend(lps)

            if not lps_records:
                raise PluginException(f"No records found for txn_ids: {txn_ids}")

            lps_record_map: dict[str, dict[str, Optional[str]]] = {}

            for lps_record in lps_records:
                if lps_record.state.value not in allowed_states:
                    continue

                ref_id = None
                try:
                    if lps_record.data and isinstance(lps_record.data, list):
                        last_data_entry: dict = lps_record.data[-1]
                        last_gateway_response: GatewayResponseModel = (
                            GatewayResponseModel(**last_data_entry)
                        )
                        ref_id = last_gateway_response.ref_id
                except Exception as ref_err:
                    logger.error(
                        f"Error extracting ref_id for txn_id {lps_record.txn_id}: {ref_err}"
                    )

                lps_record_map[lps_record.txn_id] = {
                    "status": lps_record.state.value,
                    "refid": ref_id,
                }

            # Filter LPS records to allowed states
            lps_map: dict[str, str] = {
                lps_record.txn_id: lps_record.state.value
                for lps_record in lps_records
                if lps_record.state.value in allowed_states
            }
            logger.debug(f"Filtered LPS map (txn_id -> status): {lps_map}")

            # Prepare final addon_cart_rows based on addon initialization rows
            addon_cart_rows: List[FieldGrpRootAddonsAddonServiceAddonCartRow] = []
            for row in addon_rows:
                if row.txnid in lps_record_map:
                    row_dict = row.model_dump()

                    # Get the status value
                    lps_status_string: str = lps_record_map[row.txnid]["status"]

                    # Ensure amount starts with rupee symbol
                    amount_rupee_string: str = row_dict.get("amount", "")
                    if not amount_rupee_string.startswith("₹ "):
                        amount_rupee_string = "₹ " + amount_rupee_string

                    # Update row_dict with status and formatted amount
                    row_dict.update(
                        {
                            "status": LPS_STATUS_USER_STATUS_MAP[lps_status_string],
                            "status_internal": lps_status_string,
                            "amount": amount_rupee_string,
                        }
                    )
                    try:
                        if lps_record_map[row.txnid]["refid"]:
                            row_dict["refid"] = lps_record_map[row.txnid]["refid"]
                    except Exception as e:
                        logger.error(
                            f"Could not assign refid for txn_id {row.txnid}: {e}"
                        )
                    updated_row = FieldGrpRootAddonsAddonServiceAddonCartRow(**row_dict)
                    addon_cart_rows.append(updated_row)
                else:
                    logger.debug(
                        f"Skipping txn_id {row.txnid} - not in filtered LPS map"
                    )

            logger.debug(f"Total addon_cart_rows prepared: {len(addon_cart_rows)}")

            # Assign to the parsed record
            if full_parsed_record.addons.addon_service is None:
                full_parsed_record.addons.addon_service = RootAddonsAddonService()

            # Append the new addon_cart_rows to addon cart
            if full_parsed_record.addons.addon_service.addon_cart_row is None:
                full_parsed_record.addons.addon_service.addon_cart_row = []
            full_parsed_record.addons.addon_service.addon_cart_row.extend(
                addon_cart_rows
            )
            logger.debug(
                f"Appended {len(addon_cart_rows)} rows to addon_service.addon_cart_row"
            )

            # Clear the initialization table
            full_parsed_record.addons.addon_service_initialization = (
                RootAddonsAddonServiceInitialization()
            )
            logger.debug("Cleared addon_service_initialization")

            # Clear the addon selections
            for group_traveller in full_parsed_record.addons.addon_group:
                for (
                    addon_table_row
                ) in group_traveller.addonservicegroup.addon_card.addon_on_service:
                    addon_table_row.service_checkbox = None
            logger.debug("Cleared addon_group.service_checkbox")

            # Clear the verifier payment request:
            full_parsed_record.addons.payment_display = None
            logger.debug("Cleared payment_display")

            return GenericFormRecordModel(**full_parsed_record.model_dump())

        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload  # Safe fallback on error
