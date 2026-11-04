from django.apps import AppConfig

from core.rights_declaration import RightsDeclaration

MODULE_NAME = "medical_pricelist"


# Rights, by entity then by action. One entity per pricelist type, plus the general
# read (121200, the base of the block, like tools.registers and report.report).
DJANGO_PERMS = {
    "pricelist": {
        "query": ("medical_pricelist.view_pricelist", 121200),
    },
    "servicesPricelist": {
        "query": ("medical_pricelist.view_servicespricelist", 121201),
        "create": ("medical_pricelist.add_servicespricelist", 121202),
        "update": ("medical_pricelist.change_servicespricelist", 121203),
        "delete": ("medical_pricelist.delete_servicespricelist", 121204),
        "duplicate": ("medical_pricelist.duplicate_servicespricelist", 121205),
    },
    "itemsPricelist": {
        "query": ("medical_pricelist.view_itemspricelist", 121301),
        "create": ("medical_pricelist.add_itemspricelist", 121302),
        "update": ("medical_pricelist.change_itemspricelist", 121303),
        "delete": ("medical_pricelist.delete_itemspricelist", 121304),
        "duplicate": ("medical_pricelist.duplicate_itemspricelist", 121305),
    },
}

_PERM_CFG = {
    "gql_query_pricelists_perms": ("pricelist", "query"),
    "gql_query_pricelists_medical_services_perms": ("servicesPricelist", "query"),
    "gql_mutation_pricelists_medical_services_add_perms": ("servicesPricelist", "create"),
    "gql_mutation_pricelists_medical_services_update_perms": ("servicesPricelist", "update"),
    "gql_mutation_pricelists_medical_services_delete_perms": ("servicesPricelist", "delete"),
    "gql_mutation_pricelists_medical_services_duplicate_perms": ("servicesPricelist", "duplicate"),
    "gql_query_pricelists_medical_items_perms": ("itemsPricelist", "query"),
    "gql_mutation_pricelists_medical_items_add_perms": ("itemsPricelist", "create"),
    "gql_mutation_pricelists_medical_items_update_perms": ("itemsPricelist", "update"),
    "gql_mutation_pricelists_medical_items_delete_perms": ("itemsPricelist", "delete"),
    "gql_mutation_pricelists_medical_items_duplicate_perms": ("itemsPricelist", "duplicate"),
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


DEFAULT_CFG = {
    # 121200: the general "pricelists" read, above the per-type blocks (1212xx medical
    # services, 1213xx medical items). Base-of-block for a general right follows
    # tools.registers (131100) and report.report (131200). Nothing reads it yet.
}


class MedicalPricelistConfig(AppConfig):
    name = MODULE_NAME

    # Rights: constants, no longer overridable. They go neither through DEFAULT_CFG
    # nor through ready(): `ModuleConfiguration.get_or_default` now ignores any
    # `_perms` key stored in the database.
    gql_query_pricelists_perms = RIGHTS.perms("pricelist", "query")
    gql_query_pricelists_medical_items_perms = RIGHTS.perms("itemsPricelist", "query")
    gql_mutation_pricelists_medical_items_add_perms = RIGHTS.perms("itemsPricelist", "create")
    gql_mutation_pricelists_medical_items_update_perms = RIGHTS.perms("itemsPricelist", "update")
    gql_mutation_pricelists_medical_items_delete_perms = RIGHTS.perms("itemsPricelist", "delete")
    gql_mutation_pricelists_medical_items_duplicate_perms = RIGHTS.perms("itemsPricelist", "duplicate")
    gql_query_pricelists_medical_services_perms = RIGHTS.perms("servicesPricelist", "query")
    gql_mutation_pricelists_medical_services_add_perms = RIGHTS.perms("servicesPricelist", "create")
    gql_mutation_pricelists_medical_services_update_perms = RIGHTS.perms("servicesPricelist", "update")
    gql_mutation_pricelists_medical_services_delete_perms = RIGHTS.perms("servicesPricelist", "delete")
    gql_mutation_pricelists_medical_services_duplicate_perms = RIGHTS.perms("servicesPricelist", "duplicate")

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(MedicalPricelistConfig, field):
                setattr(MedicalPricelistConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)
