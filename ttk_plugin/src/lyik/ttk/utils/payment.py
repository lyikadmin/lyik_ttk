from ..models.payment.addon_models import AddonSummaryItem, GroupedAddonSummaryItem
from typing import Dict, List

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
