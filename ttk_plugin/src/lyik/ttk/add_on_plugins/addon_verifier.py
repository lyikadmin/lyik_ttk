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
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import tempfile
import base64
import mimetypes
import textwrap

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
        record_id = context.record.get("_id")
        full_form_record = Schengentouristvisa.model_validate(context.record)

        order_id = full_form_record.visa_request_information.visa_request.order_id
        total_amount = 0
        addon_summary: List[dict] = []

        if payload.addon_group:
            for group in payload.addon_group:
                card = (
                    group.addonservicegroup.addon_card
                    if group.addonservicegroup
                    else None
                )
                if not card or not card.addon_on_service:
                    continue

                traveller_id = card.traveler_name  # Used in udf1

                for item in card.addon_on_service:
                    if item.service_checkbox == ADDONOP.DONE and item.amount_internal:
                        total_amount += item.amount_internal
                        addon_summary.append(
                            {
                                "orderId": order_id,
                                "travellerId": traveller_id,
                                "addonId": item.addon_id,
                                "amount": item.amount_internal,
                            }
                        )

        calculated_amount = total_amount
        udf1_data = base64.urlsafe_b64encode(
            json.dumps(addon_summary).encode()
        ).decode()

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
                record_id=record_id,
                amount=calculated_amount,
                pg_params=pg_payu_params,
            )
        )

        payment_txn_id = payment_initiation_response.txn_id
        encoded_payment_html = payment_initiation_response.payment_html
        decoded_payment_html = decode_base64_to_str(encoded_payment_html)

        full_form_record.addons.payment_display = decoded_payment_html

        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
            message="Calculated total amount",
            response=full_form_record.addons.model_dump(),
        )


import base64
import json


def encode_dict_to_base64(data: dict) -> str:
    json_str = json.dumps(data)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_base64_to_str(b64_str: str) -> str:
    decoded_bytes = base64.urlsafe_b64decode(b64_str.encode())
    return decoded_bytes.decode()
