from datetime import datetime
import apluggy as pluggy
import os
from lyikpluginmanager import (
    getProjectName,
    TrustedPluginSpec,
    ContextModel,
    TrustedResponseModel,
    TRUSTED_RESPONSE_STATUS,
    PluginException,
)

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Tuple, Optional, List, Annotated, Dict, Any
import logging
from typing_extensions import Doc
from lyik.datatypes import VISA
from lyik.ttk.utils.datatype_utils import props_dict

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class VisaCard(BaseModel):
    visa_image: VISA
    model_config = ConfigDict(extra="allow")


class VisaOCR(TrustedPluginSpec):
    @impl
    async def trusted(
        self,
        context: ContextModel,
        payload: Annotated[VisaCard, Doc("Visa Field containing the image")],
    ) -> Annotated[
        TrustedResponseModel,
        Doc("TrustedResponseModel will be returned with OCR data for VISA"),
    ]:
        try:
            if context is None:
                raise PluginException("context must be provided")
            if context.config is None:
                raise PluginException("config must be provided in the context")

            visa_ocr_fields = props_dict(payload.visa_image)

            return TrustedResponseModel(
                status=TRUSTED_RESPONSE_STATUS.SUCCESS, response=visa_ocr_fields, message="Successfully OCR Visa"
            )
        except Exception as e:
            logger.exception(e)
            return TrustedResponseModel(
                status=TRUSTED_RESPONSE_STATUS.FAILURE,
                response={},
                message="Trusted API failed to get the details",
            )