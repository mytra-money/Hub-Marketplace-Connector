# Copyright (c) 2024, pwctech technologies private limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HubSellerCatalog(Document):
	def create_catalog(self):
		catalog = {
			"seller": {},
			"items": []
		}
		hub_items = frappe.get_all("Hub Item", filters={"published": 1})
		for item in hub_items:
			hub_item = frappe.get_doc("Hub Item", item.name)
			item_data = hub_item.get_item_data()
			if item_data:
				catalog["items"].append(item_data)
		hub_seller_settings = frappe.get_doc("Hub Seller Setting")
		catalog["seller"] = hub_seller_settings.get_seller_data()
		self.catalog = frappe.as_json(catalog, indent=4)
		self.save()
