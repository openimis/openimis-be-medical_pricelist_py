from django.apps import AppConfig

MODULE_NAME = "medical_pricelist"

DEFAULT_CFG = {
    "gql_query_pricelists_perms": [],
    "gql_query_pricelists_medical_items_perms": ["121301"],
    "gql_mutation_pricelists_medical_items_add_perms": ["121302"],
    "gql_mutation_pricelists_medical_items_update_perms": ["121303"],
    "gql_mutation_pricelists_medical_items_delete_perms": ["121304"],
    "gql_mutation_pricelists_medical_items_duplicate_perms": ["121305"],
    "gql_query_pricelists_medical_services_perms": ["121201"],
    "gql_mutation_pricelists_medical_services_add_perms": ["121202"],
    "gql_mutation_pricelists_medical_services_update_perms": ["121203"],
    "gql_mutation_pricelists_medical_services_delete_perms": ["121204"],
    "gql_mutation_pricelists_medical_services_duplicate_perms": ["121205"],
}


class MedicalPricelistConfig(AppConfig):
    name = MODULE_NAME

    gql_query_pricelists_perms = []
    gql_query_pricelists_medical_items_perms = []
    gql_mutation_pricelists_medical_items_add_perms = []
    gql_mutation_pricelists_medical_items_update_perms = []
    gql_mutation_pricelists_medical_items_delete_perms = []
    gql_mutation_pricelists_medical_items_duplicate_perms = []
    gql_query_pricelists_medical_services_perms = []
    gql_mutation_pricelists_medical_services_add_perms = []
    gql_mutation_pricelists_medical_services_update_perms = []
    gql_mutation_pricelists_medical_services_delete_perms = []
    gql_mutation_pricelists_medical_services_duplicate_perms = []

    def _configure_permissions(self, cfg):
        MedicalPricelistConfig.gql_query_pricelists_perms = cfg[
            "gql_query_pricelists_perms"
        ]
        MedicalPricelistConfig.gql_query_pricelists_medical_items_perms = cfg[
            "gql_query_pricelists_medical_items_perms"
        ]
        MedicalPricelistConfig.gql_mutation_pricelists_medical_items_add_perms = cfg[
            "gql_mutation_pricelists_medical_items_add_perms"
        ]
        MedicalPricelistConfig.gql_mutation_pricelists_medical_items_update_perms = cfg[
            "gql_mutation_pricelists_medical_items_update_perms"
        ]
        MedicalPricelistConfig.gql_mutation_pricelists_medical_items_delete_perms = cfg[
            "gql_mutation_pricelists_medical_items_delete_perms"
        ]
        MedicalPricelistConfig.gql_mutation_pricelists_medical_items_duplicate_perms = (
            cfg["gql_mutation_pricelists_medical_items_duplicate_perms"]
        )
        MedicalPricelistConfig.gql_query_pricelists_medical_services_perms = cfg[
            "gql_query_pricelists_medical_services_perms"
        ]
        MedicalPricelistConfig.gql_mutation_pricelists_medical_services_add_perms = cfg[
            "gql_mutation_pricelists_medical_services_add_perms"
        ]
        MedicalPricelistConfig.gql_mutation_pricelists_medical_services_update_perms = (
            cfg["gql_mutation_pricelists_medical_services_update_perms"]
        )
        MedicalPricelistConfig.gql_mutation_pricelists_medical_services_delete_perms = (
            cfg["gql_mutation_pricelists_medical_services_delete_perms"]
        )
        MedicalPricelistConfig.gql_mutation_pricelists_medical_services_duplicate_perms = cfg[
            "gql_mutation_pricelists_medical_services_duplicate_perms"
        ]

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
