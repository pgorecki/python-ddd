from seedwork.application import ApplicationModule

bidding_module = ApplicationModule("bidding")
bidding_module.import_from("modules.bidding.application.command")
bidding_module.import_from("modules.bidding.application.query")
bidding_module.import_from("modules.bidding.application.event")
