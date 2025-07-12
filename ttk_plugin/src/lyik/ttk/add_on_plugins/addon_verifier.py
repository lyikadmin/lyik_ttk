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
)
from lyikpluginmanager.core.utils import generate_hash_id_from_dict
from ..models.forms.new_schengentouristvisa import (
    RootAddons,
    ADDONOP,
    Schengentouristvisa,
)
import logging
import base64
from ..utils.encode import decode_base64_to_str

from ..models.payment.addon_models import AddonSummaryItem
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

        record_id = full_form_record.addons.record_id

        order_id = full_form_record.visa_request_information.visa_request.order_id
        total_amount = 0
        addon_summary_models: List[AddonSummaryItem] = []

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

                for item in card.addon_on_service:
                    if item.service_checkbox == ADDONOP.DONE and item.amount_internal:
                        total_amount += item.amount_internal
                        addon_summary_models.append(
                            AddonSummaryItem(
                                addonId=item.addon_id,
                                amount=item.amount_internal,
                                orderId=order_id,
                                travellerId=traveller_id,
                                addonName=item.add_ons
                            )
                        )

        calculated_amount = total_amount
        udf1_data = base64.urlsafe_b64encode(
            json.dumps([entry.model_dump() for entry in addon_summary_models]).encode()
        ).decode()

        # print(f"\n\n The encoded udf1 data is: {udf1_data}")

        # print(f"\n\n The decoded udf1 data is: {decode_base64_to_str(udf1_data)}")

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
        encoded_payment_html = payment_initiation_response.payment_html
        decoded_payment_html = decode_base64_to_str(encoded_payment_html)

        full_form_record.addons.payment_display = decoded_payment_html

        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
            message="Calculated total amount",
            response=full_form_record.addons.model_dump(),
        )
