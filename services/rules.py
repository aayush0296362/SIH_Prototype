"""LMSCAN rule registry.

The registry intentionally separates *what the law requires* from OCR/AI
extraction. Rules are versioned by effective date so future amendments can be
introduced without rewriting the compliance engine.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Rule:
    rule_id: str
    authority: str
    requirement: str
    evidence_field: Optional[str]
    severity: str
    applicability: str = "always"
    source: str = ""
    effective_from: str = "2020-12-08"
    notes: str = ""


# MVP registry for pre-packaged food. Applicability is deliberately conservative:
# conditional requirements are not marked missing unless their trigger is known.
RULES = [
    Rule("LM-01", "Legal Metrology", "Name/common or generic name of commodity", "product_name", "high",
         source="Legal Metrology (Packaged Commodities) Rules, 2011"),
    Rule("LM-02", "Legal Metrology", "Manufacturer/packer/importer name and address", "manufacturer", "high",
         source="Legal Metrology (Packaged Commodities) Rules, 2011", notes="Current extractor stores the combined manufacturer/address evidence."),
    Rule("LM-03", "Legal Metrology", "Net quantity", "net_quantity", "high",
         source="Legal Metrology (Packaged Commodities) Rules, 2011"),
    Rule("LM-04", "Legal Metrology", "Retail sale price (MRP), inclusive of taxes", "mrp", "high",
         source="Legal Metrology (Packaged Commodities) Rules, 2011"),
    Rule("LM-05", "Legal Metrology", "Consumer care details", "consumer_care", "medium",
         source="Legal Metrology (Packaged Commodities) Rules, 2011"),
    Rule("LM-06", "Legal Metrology", "Month/year of manufacture or packing", "manufacturing_date", "high",
         source="Legal Metrology (Packaged Commodities) Rules, 2011"),
    Rule("LM-07", "Legal Metrology", "Batch/lot/code identification where applicable", "batch_number", "medium",
         source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("LM-08", "Legal Metrology", "Country of origin", "country_of_origin", "high", applicability="imported",
         source="Legal Metrology (Packaged Commodities) Rules, 2011"),
    Rule("LM-09", "Legal Metrology", "Unit sale price", None, "medium", applicability="unit_sale_price",
         source="Legal Metrology (Packaged Commodities) Rules, 2011",
         notes="Applicability/exemptions need package-specific determination; this MVP does not auto-fail it."),

    Rule("FSSAI-01", "FSSAI", "Name of the food", "product_name", "high",
         applicability="food", source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-02", "FSSAI", "List of ingredients", "ingredients", "high",
         applicability="food", source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-03", "FSSAI", "Nutritional information", "nutrition", "medium",
         applicability="food", source="Food Safety and Standards (Labelling and Display) Regulations, 2020",
         notes="Some categories/exemptions exist; category-specific rule selection should be added before strict enforcement."),
    Rule("FSSAI-04", "FSSAI", "Veg/non-veg declaration where applicable", "veg_nonveg", "medium",
         applicability="veg_nonveg", source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-05", "FSSAI", "FSSAI licence number", "fssai_license_number", "high",
         applicability="food", source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-06", "FSSAI", "Lot/code/batch identification", "batch_number", "medium",
         applicability="food", source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-07", "FSSAI", "Date marking / use-by or expiry as applicable", "expiry_date", "high",
         applicability="food", source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-08", "FSSAI", "Allergen declaration when applicable", "allergens", "high", applicability="allergen_trigger",
         source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-09", "FSSAI", "Food additive declaration when applicable", "food_additives", "medium", applicability="additive_trigger",
         source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
    Rule("FSSAI-10", "FSSAI", "Instructions for use / storage where applicable", "instructions", "medium", applicability="instruction_trigger",
         source="Food Safety and Standards (Labelling and Display) Regulations, 2020"),
]


def get_rules() -> list[Rule]:
    return list(RULES)
