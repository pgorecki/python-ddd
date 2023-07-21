from seedwork.application import ApplicationModule

catalog_module = ApplicationModule("catalog")
catalog_module.import_from("modules.catalog.application.command")
catalog_module.import_from("modules.catalog.application.query")
catalog_module.import_from("modules.catalog.application.event")
