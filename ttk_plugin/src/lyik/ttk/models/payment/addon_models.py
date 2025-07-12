from pydantic import BaseModel


class AddonSummaryItem(BaseModel):
    orderId: str
    travellerId: str
    addonId: str
    addonName: str
    amount: int

class GroupedAddonSummaryItem(BaseModel):
    addonName: str
    count: int
    singleAddonCost: int
    totalAddonCost: int