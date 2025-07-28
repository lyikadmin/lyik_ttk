from ..models.payment.addon_models import AddonSummaryItem, GroupedAddonSummaryItem
from typing import Dict, List


def group_addon_summary(
    addon_summary_list: List[AddonSummaryItem],
) -> Dict[str, GroupedAddonSummaryItem]:
    grouped_summary: Dict[str, GroupedAddonSummaryItem] = {}
    for item in addon_summary_list:
        addon_id = item.addonId

        if addon_id not in grouped_summary:
            grouped_summary[addon_id] = GroupedAddonSummaryItem(
                addonName=item.addonName,
                count=1,
                singleAddonCost=item.amount,
                totalAddonCost=item.amount,
                travellerIds=[item.travellerId],
            )
        else:
            summary = grouped_summary[addon_id]
            summary.count += 1
            summary.totalAddonCost += item.amount
            summary.travellerIds.append(item.travellerId)

    return grouped_summary


def create_styled_traveller_name_list_string_for_traveller_ids(
    traveller_id_list: List[str],
    traveller_id_name_mapping: Dict[str, str],
) -> str:
    return ",<br>".join(
        traveller_id_name_mapping.get(str(item), str(item))
        for item in traveller_id_list
    )


def create_traveller_id_list_string_for_traveller_ids(
    traveller_id_list: List[str],
) -> str:
    return ",".join(str(item) for item in traveller_id_list)


def get_traveller_ids_from_traveller_id_list_string(
    traveller_id_list_string: str,
) -> List[str]:
    return traveller_id_list_string.split(",")
