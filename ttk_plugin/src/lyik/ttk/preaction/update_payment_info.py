from typing import Dict, List
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
from lyikpluginmanager.models import LPSRecord, PayUParams, LPSStatus
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    FieldGrpRootAddonsAddonServiceAddonCartRow,
    RootAddonsAddonService,
    RootAddonsAddonServiceInitialization
)
import logging
import base64
import json
from ..models.payment.addon_models import AddonSummaryItem, GroupedAddonSummaryItem
from ..utils.payment import group_addon_summary

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())


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
            full_parsed_record = Schengentouristvisa(**payload.model_dump())
            addon_rows = (
                full_parsed_record.addons.addon_service_initialization.addon_cart_row
                if full_parsed_record.addons.addon_service_initialization
                else []
            )

            txn_ids = {row.txnid for row in addon_rows if row.txnid}
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

            # Define allowed states
            allowed_states = {
                LPSStatus.PAY_FAILURE,
                LPSStatus.PAY_SUCCESS,
                LPSStatus.PAY_IN_PROGRESS,
            }
            seen_combinations: set[tuple[str, str]] = set()
            addon_cart_rows = []

            for lps_record in lps_records:
                if lps_record.state.value not in allowed_states:
                    continue

                for pg_data in lps_record.data:
                    try:
                        payu_params = PayUParams(**pg_data)
                        if not payu_params.udf1:
                            logger.warning(
                                f"Skipping record {lps_record.txn_id}: missing udf1"
                            )
                            continue

                        decoded_udf1 = base64.urlsafe_b64decode(
                            payu_params.udf1
                        ).decode()
                        addon_summary_list: List[AddonSummaryItem] = [
                            AddonSummaryItem(**item)
                            for item in json.loads(decoded_udf1)
                        ]
                        grouped_addon_summary = group_addon_summary(addon_summary_list)

                        for addon_id, summary in grouped_addon_summary.items():
                            unique_key = (addon_id, lps_record.txn_id)
                            if unique_key in seen_combinations:
                                continue

                            addon_table_row = FieldGrpRootAddonsAddonServiceAddonCartRow(
                                addon_id=addon_id,
                                addon_name=summary.addonName,
                                amount=str(summary.totalAddonCost),
                                quantity=str(summary.count),
                                status=lps_record.state.value,
                                refid=None,
                                txnid=lps_record.txn_id,
                                amt_status=None,
                            )
                            addon_cart_rows.append(addon_table_row)
                            seen_combinations.add(unique_key)

                    except Exception as inner_e:
                        logger.warning(
                            f"Error processing LPS record {lps_record.txn_id}: {inner_e}"
                        )
                        continue

            # Assign to the parsed record
            if full_parsed_record.addons.addon_service is None:
                full_parsed_record.addons.addon_service = RootAddonsAddonService()

            full_parsed_record.addons.addon_service.addon_cart_row = addon_cart_rows

            # Clear the initialization table
            full_parsed_record.addons.addon_service_initialization = RootAddonsAddonServiceInitialization()

            # Clear the addon selections
            for group_traveller in full_parsed_record.addons.addon_group:
                for addon_table_row in group_traveller.addonservicegroup.addon_card.addon_on_service:
                    addon_table_row.service_checkbox = None

            # Clear the verifier payment request:
            full_parsed_record.addons.payment_display = None

            return GenericFormRecordModel(**full_parsed_record.model_dump())

        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload  # Safe fallback on error
