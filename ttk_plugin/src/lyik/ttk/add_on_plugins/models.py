from pydantic import BaseModel


class AddonSummaryItem(BaseModel):
    orderId: str
    travellerId: str
    addonId: str
    addonName: str
    amount: int
