from typing import Dict, List, Optional, Any, Union
from pydantic import Field, BaseModel
from typing_extensions import Doc, Annotated
import jwt

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
from lyikpluginmanager.annotation import RequiredEnv
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    FieldGrpRootAddonsAddonServiceAddonCartRow,
    RootAddonsAddonService,
    RootAddonsAddonServiceInitialization,
    RootAddons,
)
import httpx

import logging
import base64
import json
from ..models.payment.addon_models import AddonSummaryItem
import os
from ..utils.payment import (
    create_styled_traveller_name_list_string_for_traveller_ids,
    get_traveller_ids_from_traveller_id_list_string,
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())

LPS_STATUS_USER_STATUS_MAP = {
    LPSStatus.PAY_SUCCESS.value: "Success",  # "Success | Completed"
    LPSStatus.PAY_IN_PROGRESS.value: "Success",  # "Success | In Progress"
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
        RequiredEnv(["TTK_API_BASE_URL", "TTK_PAYMENT_UPDATE_ROUTE"]),
        Doc("The updated form record data."),
    ]:
        """
        This preaction processor will append maker_id into the _owner list of the record.
        """
        try:
            token = context.token

            _addons_updated_flag = False

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
                full_parsed_record.addons.addon_service_initialization = (
                    RootAddonsAddonServiceInitialization()
                )

            # Update the traveller names in 'Your Transactions' Card if changed.
            try:
                # Create mapping for each traveller id to updated traveller name
                traveller_id_name_mapping: dict = {}

                for traveller_addon_card in full_parsed_record.addons.addon_group:
                    traveller_name_internal = (
                        traveller_addon_card.addonservicegroup.addon_card.traveller_name_internal
                        if traveller_addon_card.addonservicegroup.addon_card.traveller_name_internal
                        else traveller_addon_card.addonservicegroup.addon_card.traveller_id
                    )

                    traveller_id = (
                        traveller_addon_card.addonservicegroup.addon_card.traveller_id
                    )
                    traveller_id_name_mapping.update(
                        {traveller_id: traveller_name_internal}
                    )

                for (
                    payment_transaction_row
                ) in full_parsed_record.addons.addon_service.addon_cart_row:
                    traveller_ids_for_payment_row_list = get_traveller_ids_from_traveller_id_list_string(
                        traveller_id_list_string=payment_transaction_row.traveller_ids_internal
                    )
                    traveller_name_display_list_string = (
                        create_styled_traveller_name_list_string_for_traveller_ids(
                            traveller_id_list=traveller_ids_for_payment_row_list,
                            traveller_id_name_mapping=traveller_id_name_mapping,
                        )
                    )

                    payment_transaction_row.traveller_names = (
                        traveller_name_display_list_string
                    )

            except Exception as e:
                logger.error(f"Could not update traveller names {e}")

            addon_rows = (
                full_parsed_record.addons.addon_service_initialization.addon_cart_row
                if full_parsed_record.addons.addon_service_initialization
                and full_parsed_record.addons.addon_service_initialization.addon_cart_row
                else []
            )
            logger.debug(f"Fetched {len(addon_rows)} addon_rows from initialization")

            if not addon_rows:
                # If there are no addon initialization rows, we can return early as the
                # further processes are all on updating the your transactions table, which is not required anymore.
                return GenericFormRecordModel(**full_parsed_record.model_dump())

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

                    # Setting a flag to denote when a payment redirect flow is successful.
                    # This can be used later to determine if the checkbox values must be cleared out or not.
                    # In a successful payment redirect flow, the status we get back is 'LPSStatus.PAY_IN_PROGRESS'
                    if updated_row.status_internal == LPSStatus.PAY_IN_PROGRESS.value:
                        _successful_payment_flag = True
                    else:
                        _successful_payment_flag = False

                    # Mark the flag to indicate that the addons are updated.
                    _addons_updated_flag = True
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

            # Only clearing out the checkboxes and payment card after successful payment flow
            if _addons_updated_flag and _successful_payment_flag:

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

            if _addons_updated_flag and not _successful_payment_flag:
                # Need the logic to update the payment button to say "retry" if possible.
                if "Pay Now" in full_parsed_record.addons.payment_display:
                    full_parsed_record.addons.payment_display = (
                        full_parsed_record.addons.payment_display.replace(
                            "Pay Now", "Retry Payment"
                        )
                    )

            try:
                if _addons_updated_flag:
                    api_res = await self.update_ttk_payment(
                        token=token, lps_records=lps_records
                    )
            except Exception as e:
                logger.error(f"Failed to update ttk payment with API call. {str(e)}")

            return GenericFormRecordModel(**full_parsed_record.model_dump())

        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload  # Safe fallback on error

    def _decode_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, algorithms=["HS256"], options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Something went wrong while decoding payload: {e}",
            )

    def find_token_field(self, data: Dict[str, Any]) -> Union[str, None]:
        if isinstance(data, dict):
            provider_info = data.get("provider_info")
            if isinstance(provider_info, dict):
                token = provider_info.get("token")
                if isinstance(token, str):
                    return token

        return None

    async def update_ttk_payment(self, token: str, lps_records: List[LPSRecord]):
        api_prefix = os.getenv("TTK_API_BASE_URL")
        api_route = os.getenv("TTK_PAYMENT_UPDATE_ROUTE")  # api/v2/paymentUpdate
        PAYMENT_UPDATE_API_URL = api_prefix + api_route

        outer_payload = self._decode_jwt(token=token)

        # Step 2: Extract inner token
        inner_token = self.find_token_field(outer_payload)
        if not inner_token:
            logger.error("Inner token not found in the decoded payload.")
            inner_token = "example_token"

        # Map internal statuses to external API statuses
        LPS_STATUS_API_STATUS_MAP = {
            LPSStatus.PAY_SUCCESS.value: "Successful",
            LPSStatus.PAY_IN_PROGRESS.value: "Successful",
            LPSStatus.PAY_FAILURE.value: "Failure",
            LPSStatus.PAY_REJECTED.value: "Rejected",
        }

        for lps_record in lps_records:
            try:
                status: LPSStatus = lps_record.state
                if status.value not in LPS_STATUS_API_STATUS_MAP:
                    continue  # Skip if status is not relevant for the API

                # Decode udf1 data
                payu_params: PayUParams = PayUParams(**lps_record.data[0])
                udf1_encoded_data = payu_params.udf1
                decoded_str = base64.b64decode(udf1_encoded_data).decode("utf-8")
                addon_items_data = json.loads(decoded_str)
                addon_items: List[AddonSummaryItem] = [
                    AddonSummaryItem(**item) for item in addon_items_data
                ]

                # Group by traveller
                traveller_map = {}
                for item in addon_items:
                    traveller_services: list = traveller_map.setdefault(
                        item.travellerId, []
                    )
                    traveller_services.append(
                        {"serviceId": item.addonId, "amount": str(item.amount)}
                    )

                body = {
                    "orderNo": addon_items[0].orderId if addon_items else "",
                    "transactionNo": lps_record.txn_id,
                    "paymentStatus": LPS_STATUS_API_STATUS_MAP[status.value],
                    "traveller": [
                        {"travellerId": traveller_id, "service": services}
                        for traveller_id, services in traveller_map.items()
                    ],
                }

                logger.debug(
                    f"TTK Payment Update Payload:\n{json.dumps(body, indent=2)}"
                )

                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        PAYMENT_UPDATE_API_URL,
                        content=json.dumps(body),
                        headers={
                            "Authorization": f"Bearer {inner_token}",
                            "Content-Type": "application/json",
                        },
                    )

                    try:
                        response_json = response.json()
                    except Exception as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        continue

                    if response_json.get("status") != "success":
                        logger.error(
                            f"Payment update failed for txn_id {lps_record.txn_id}. Response: {response_json}"
                        )
                    else:
                        logger.info(
                            f"Successfully updated payment for txn_id {lps_record.txn_id}"
                        )

            except Exception as e:
                logger.error(
                    f"Error updating payment for txn_id {lps_record.txn_id}: {e}"
                )
