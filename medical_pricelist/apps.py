from django.apps import AppConfig

MODULE_NAME = "medical_pricelist"

DEFAULT_CFG = {
    "gql_query_pricelists_perms": []
}


class MedicalPricelistConfig(AppConfig):
    name = MODULE_NAME

    gql_query_pricelists_perms = []

    def _configure_permissions(self, cfg):
        MedicalPricelistConfig.gql_query_pricelists_perms = cfg[
            "gql_query_pricelists_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
