import frappe
from requests import request
from frappe.integrations.utils import create_request_log


class HubServices:
    def __init__(self):
        self.set_base_url()
    
    def set_base_url(self):
        #TODO: change to live URL
        self.base_url = "https://demo.hubmarket.place/api/method/hub_marketplace/"
        if frappe.db.exists("Hub Seller Setting"):
            hub_seller_settings = frappe.get_cached_doc("Hub Seller Setting")
            if hub_seller_settings.environment == "Pre-Production":
                self.base_url = "https://demo.hubmarket.place/api/method/hub_marketplace/"
    
    def get_categories(self):
        url = self.base_url+"get_seller_categories"
        response = request(method="POST", url=url).json()
        return response.get("message")
    
    def get_category(self, category):
        url = self.base_url+"get_category"
        response = request(method="POST", url=url, data=frappe.as_json({"category": category}), headers={"Content-Type": "application/json"}).json()
        return response.get("message")
    
    def register_user(self, user_data):
        url = self.base_url+"register_seller"
        response = request(method="POST", url=url, data=frappe.as_json(user_data), headers={"Content-Type": "application/json"}).json()
        return response.get("message")
    
    def send_catalog(self, catalog):
        url = self.base_url+"update_catalog"
        hub_seller_setting = frappe.get_cached_doc("Hub Seller Setting")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "token {0}:{1}".format(hub_seller_setting.api_key, hub_seller_setting.get_password("api_secret"))
        }
        integration_request = create_request_log(data=catalog, service_name="Hub Marketplace Catalog", request_headers=headers, url=url)
        response = request(method="POST", url=url, data=catalog, headers=headers)
        integration_request.db_set("output", frappe.as_json(response.json(), indent=4))
        if response.status_code == 200:
            integration_request.db_set("status", "Completed")
            return
        else:
            integration_request.db_set("status", "Failed")
            frappe.throw(frappe.as_json(response.json(), indent=4))

def crete_integration_request(**kwargs):
    return create_request_log(kwargs.get("data"), service_name=kwargs.get("service_name"), kwargs=kwargs)
