from hub_marketplace_connector.api.hub_services import HubServices

def set_bootinfo(bootinfo):
    bootinfo["hub_categories_response"] = HubServices().get_categories()
    bootinfo["hub_categories"] = sorted([h.get("name") for h in bootinfo["hub_categories_response"]])
