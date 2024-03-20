from lato import ApplicationModule
import importlib


bidding_module = ApplicationModule("bidding")
importlib.import_module("modules.bidding.application.command")
importlib.import_module("modules.bidding.application.query")
importlib.import_module("modules.bidding.application.event")
