from lato import ApplicationModule
import importlib

catalog_module = ApplicationModule("catalog")
importlib.import_module("modules.catalog.application.command")
importlib.import_module("modules.catalog.application.query")
