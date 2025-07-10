from pydantic import BaseModel


class AddonSummaryItem(BaseModel):
    orderId: str
    travellerId: str
    addonId: str
    amount: int
