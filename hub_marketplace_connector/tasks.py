import frappe
from hub_marketplace_connector.hub_marketplace_connector.api.hub_services import HubServices

def hourly():
    update_catalog()

def daily():
    send_catalog_to_hub()

def update_catalog():
    hub_seller_settings = frappe.get_cached_doc("Hub Seller Setting")
    if hub_seller_settings.enabled:
        hub_seller_catalog = frappe.get_doc("Hub Seller Catalog")
        hub_seller_catalog.create_catalog()

def send_catalog_to_hub():
    catalog = frappe.db.get_value("Hub Seller Catalog", fieldname="catalog")
    try:
        HubServices().send_catalog(catalog)
    except Exception:
        frappe.log_error("Hub Catalog")

