import apluggy as pluggy
import os
from pydantic import BaseModel, ConfigDict, Field, model_validator
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    DocMeta,
)
from typing import Annotated, List, Union, Tuple, Dict, Any
from typing_extensions import Doc
from lyikpluginmanager import invoke, DBDocumentModel, DocumentModel
from lyikpluginmanager.models.lyik_payment_system_model import (
    PayUParams,
    PaymentInitiationModel,
    LPSRecord,
    PayUParams,
)
from lyikpluginmanager.core.utils import generate_hash_id_from_dict
from ..models.forms.schengentouristvisa import (
    RootAddons,
    ADDONOP,
    Schengentouristvisa,
    FieldGrpRootAddonsAddonServiceAddonCartRow,
    RootAddonsAddonService,
)
from datetime import datetime
import logging
import base64
from ..utils.encode import decode_base64_to_str
from ..utils.message import get_error_message

from ..models.payment.addon_models import AddonSummaryItem
from ..utils.payment import (
    group_addon_summary,
    create_styled_traveller_name_list_string_for_traveller_ids,
    create_traveller_id_list_string_for_traveller_ids,
)
import json

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class AddOnPaymentInitializeVerifier(VerifyHandlerSpec):
    """
    Addon for calculating verifier amount, and returning html to initiate payment.
    """

    @impl
    async def verify_handler(
        self,
        context: ContextModel | None,
        payload: Annotated[
            RootAddons,
            Doc("Payload for addon infopane."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response including the payment html"),
    ]:
        full_form_record = Schengentouristvisa.model_validate(context.record)
        full_form_record.addons.addon_service_initialization
        record_id = full_form_record.addons.record_id

        order_id = full_form_record.visa_request_information.visa_request.order_id
        total_amount = 0
        addon_summary_models: List[AddonSummaryItem] = []

        traveller_id_name_mapping = {}

        if payload.addon_group:
            for group in payload.addon_group:
                card = (
                    group.addonservicegroup.addon_card
                    if group.addonservicegroup
                    else None
                )
                if not card or not card.addon_on_service:
                    continue

                traveller_id = card.traveller_id
                traveller_id_name_mapping.update(
                    {str(traveller_id): str(card.traveller_name_internal)}
                )

                for item in card.addon_on_service:
                    if item.service_checkbox == ADDONOP.DONE and item.amount_internal:
                        total_amount += item.amount_internal
                        addon_summary_models.append(
                            AddonSummaryItem(
                                addonId=item.addon_id,
                                amount=item.amount_internal,
                                orderId=order_id,
                                travellerId=traveller_id,
                                addonName=item.add_ons,
                            )
                        )

        calculated_amount = total_amount
        udf1_data = base64.urlsafe_b64encode(
            json.dumps([entry.model_dump() for entry in addon_summary_models]).encode()
        ).decode()

        # print(f"\n\n The encoded udf1 data is: {udf1_data}")

        # print(f"\n\n The decoded udf1 data is: {decode_base64_to_str(udf1_data)}")

        try:
            first_name = full_form_record.passport.passport_details.first_name
            last_name = full_form_record.passport.passport_details.surname

            if not first_name:
                raise AttributeError("First name not found in payload")
            if not last_name:
                raise AttributeError("Last name not found in payload")

            pg_payu_params: PayUParams = PayUParams(
                first_name=full_form_record.passport.passport_details.first_name,
                last_name=full_form_record.passport.passport_details.surname,
                phone_number=full_form_record.visa_request_information.visa_request.phone_number,
                reason="Addons",
                email=full_form_record.visa_request_information.visa_request.email_id,
                udf1=udf1_data,
                udf2="",
                udf3="",
                udf4="",
                udf5="",
            )
        except AttributeError as ae:
            logger.error(f"Failed to create payu params. {str(ae)}")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                message=get_error_message(
                    error_message_code="LYIK_ERR_MISSING_APPL_NAME_ADDON"
                ),
                response=full_form_record.addons.model_dump(),
            )

        payment_initiation_response: PaymentInitiationModel = (
            await invoke.initiate_payment_and_generate_html(
                config=context.config,
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=str(record_id),
                amount=str(calculated_amount),
                pg_params=pg_payu_params,
            )
        )

        payment_txn_id = payment_initiation_response.txn_id

        # Fetch LPS record using txn_id
        lps_records: List[LPSRecord] = await invoke.get_payment_status(
            config=context.config,
            org_id=context.org_id,
            record_id=None,
            txn_id=payment_txn_id,
        )

        # Process LPS record (expecting only one)
        addon_cart_rows = []
        seen_combinations = set()
        # allowed_states = {"PAYMENT_INITIATED", "PAYMENT_COMPLETE"}

        for lps_record in lps_records:
            # if lps_record.state.value not in allowed_states:
            #     continue

            for pg_data in lps_record.data:
                payu_params = PayUParams(**pg_data)
                if not payu_params.udf1:
                    continue
                decoded_udf1 = base64.urlsafe_b64decode(payu_params.udf1).decode()
                addon_summary_list: List[AddonSummaryItem] = [
                    AddonSummaryItem(**item) for item in json.loads(decoded_udf1)
                ]
                grouped = group_addon_summary(addon_summary_list)
                for addon_id, summary in grouped.items():
                    unique_key = (addon_id, lps_record.txn_id)
                    if unique_key in seen_combinations:
                        continue
                    traveller_id_list_string = ",".join(
                        str(item) for item in summary.travellerIds
                    )

                    traveller_id_list_string = (
                        create_traveller_id_list_string_for_traveller_ids(
                            traveller_id_list=summary.travellerIds
                        )
                    )

                    traveller_name_list_string = (
                        create_styled_traveller_name_list_string_for_traveller_ids(
                            traveller_id_list=summary.travellerIds,
                            traveller_id_name_mapping=traveller_id_name_mapping,
                        )
                    )

                    current_date = str(datetime.now().strftime("%d/%m/%Y"))

                    row = FieldGrpRootAddonsAddonServiceAddonCartRow(
                        addon_id=addon_id,
                        addon_name=summary.addonName,
                        quantity=str(summary.count),
                        amount=str(summary.totalAddonCost),
                        traveller_names=traveller_name_list_string,
                        date=current_date,
                        status=lps_record.state.value,
                        txnid=lps_record.txn_id,
                        refid=None,
                        traveller_ids_internal=traveller_id_list_string,
                        amt_internal=str(summary.totalAddonCost),
                        status_internal=lps_record.state.value,
                    )
                    addon_cart_rows.append(row)
                    seen_combinations.add(unique_key)

        # Populate addon_service_initialization field
        if full_form_record.addons.addon_service_initialization is None:
            full_form_record.addons.addon_service_initialization = (
                RootAddonsAddonService()
            )

        full_form_record.addons.addon_service_initialization.addon_cart_row = (
            addon_cart_rows
        )
        encoded_payment_html = payment_initiation_response.payment_html
        decoded_payment_html = decode_base64_to_str(encoded_payment_html)

        full_form_record.addons.payment_display = decoded_payment_html

        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
            message="Calculated total amount",
            response=full_form_record.addons.model_dump(),
        )
