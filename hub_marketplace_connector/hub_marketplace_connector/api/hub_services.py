import frappe
from requests import request


class HubServices:
    def __init__(self):
        self.set_base_url()
    
    def set_base_url(self):
        if frappe.db.exists("Hub Seller Setting"):
            hub_seller_settings = frappe.get_cached_doc("Hub Seller Setting")
            if hub_seller_settings.environment == "Pre-Production":
                self.base_url = "https://sit.mytra.money/api/method/hub_marketplace/"
            else:
                #TODO: Change the URL to the new site created for Hub
                self.base_url = "https://sit.mytra.money/api/method/hub_marketplace/"
        else:
            self.base_url = "https://sit.mytra.money/api/method/hub_marketplace/"
    
    def get_categories(self):
        url = self.base_url+"get_categories"
        response = request(method="POST", url=url).json()
        return response.get("message")
    
    def get_sub_category(self, sub_category):
        url = self.base_url+"get_sub_category"
        response = request(method="POST", url=url, data=frappe.as_json({"sub_category": sub_category}), headers={"Content-Type": "application/json"}).json()
        return response.get("message")
