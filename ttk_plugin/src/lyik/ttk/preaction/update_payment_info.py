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
from lyikpluginmanager.models import LPSRecord, PayUParams
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    FieldGrpRootAddonsAddonServiceAddonCartRow,
    RootAddonsAddonService,
)
import logging
import base64
import json
from ..models.payment.addon_models import AddonSummaryItem, GroupedAddonSummaryItem

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
            record_id = full_parsed_record.addons.record_id

            # Fetch LPS records
            lps_records: List[LPSRecord] = await invoke.get_payment_status(
                config=context.config,
                org_id=context.org_id,
                record_id=record_id,
                txn_id=None,
            )
            if not lps_records:
                raise PluginException(f"No records found for record_id: {record_id}")

            # Define allowed states
            allowed_states = {"PAYMENT_INITIATED", "PAYMENT_COMPLETE"}
            seen_combinations: set[tuple[str, str]] = set()
            addon_cart_rows = []

            for lps_record in lps_records:
                if lps_record.state.value not in allowed_states:
                    continue

                for pg_data in lps_record.data:
                    try:
                        payu_params = PayUParams(**pg_data)
                        if not payu_params.udf1:
                            logger.warning(f"Skipping record {lps_record.txn_id}: missing udf1")
                            continue

                        decoded_udf1 = base64.urlsafe_b64decode(payu_params.udf1).decode()
                        addon_summary_list: List[AddonSummaryItem] = [
                            AddonSummaryItem(**item) for item in json.loads(decoded_udf1)
                        ]
                        grouped_addon_summary = group_addon_summary(addon_summary_list)

                        for addon_id, summary in grouped_addon_summary.items():
                            unique_key = (addon_id, lps_record.txn_id)
                            if unique_key in seen_combinations:
                                continue

                            row = FieldGrpRootAddonsAddonServiceAddonCartRow(
                                addon_id=addon_id,
                                addon_name=summary.addonName,
                                amount=str(summary.totalAddonCost),
                                quantity=str(summary.count),
                                status=lps_record.state.value,
                                refid=None,
                                txnid=lps_record.txn_id,
                                amt_status=None,
                            )
                            addon_cart_rows.append(row)
                            seen_combinations.add(unique_key)

                    except Exception as inner_e:
                        logger.warning(f"Error processing LPS record {lps_record.txn_id}: {inner_e}")
                        continue

            # Assign to the parsed record
            if full_parsed_record.addons.addon_service is None:
                full_parsed_record.addons.addon_service = RootAddonsAddonService()

            full_parsed_record.addons.addon_service.addon_cart_row = addon_cart_rows

            return GenericFormRecordModel(**full_parsed_record.model_dump())

        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload  # Safe fallback on error

def group_addon_summary(
    addon_summary_list: List[AddonSummaryItem],
) -> Dict[str, GroupedAddonSummaryItem]:
    grouped_summary = {}

    for item in addon_summary_list:
        addon_id = item.addonId

        if addon_id not in grouped_summary:
            grouped_summary[addon_id] = GroupedAddonSummaryItem(
                addonName=item.addonName,
                count=1,
                singleAddonCost=item.amount,
                totalAddonCost=item.amount,
            )
        else:
            summary = grouped_summary[addon_id]
            summary.count += 1
            summary.totalAddonCost += item.amount

    return grouped_summary
