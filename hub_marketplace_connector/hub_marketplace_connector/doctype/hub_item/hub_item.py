# Copyright (c) 2024, pwctech technologies private limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from hub_marketplace_connector.hub_marketplace_connector.api.hub_services import HubServices

class HubItem(Document):
	def validate(self):
		self.validate_hub_seller_settings()
		self.validate_duplicate_hub_item()
		self.is_item_template()
		self.validate_item_price()
		self.validate_country_of_origin()
		self.validate_warehouse()
		self.validate_variants()
		self.validate_update_time()
	
	def validate_hub_seller_settings(self):
		if not frappe.db.exists("Hub Seller Setting"):
			message = _("Hub Seller Settings is required to publish Hub Items")
			frappe.throw(message, title=_("Missing Hub Seller Settings"))

	def validate_duplicate_hub_item(self):
		existing_hub_item = frappe.db.exists("Hub Item", {"item_code": self.item_code})
		if existing_hub_item and existing_hub_item != self.name:
			message = _("Hub Item already exists against Item {0}").format(frappe.bold(self.item_code))
			frappe.throw(message, title=_("Already Published"))
	
	def is_item_template(self):
		has_variants = frappe.db.get_value("Item", self.item_code, "has_variants")
		if has_variants:
			message = _("Template Item cannot be added. Please add the variants")
			frappe.throw(message, title=_("Template Item not Allowed"))
	
	def validate_item_price(self):
		price_list = frappe.db.get_value("Hub Seller Setting", fieldname="price_list")
		if not frappe.db.exists("Item Price",{"price_list": price_list, "item_code": self.item_code}):
			message = _("Item price not set for {0} in {1}").format(frappe.bold(self.item_code), frappe.bold(price_list))
			template_item_code = frappe.db.get_value("Item", self.item_code, "variant_of")
			if template_item_code:
				if not frappe.db.exists("Item Price",{"price_list": price_list, "item_code": template_item_code}):
					frappe.throw(message, title=_("Set Item Price"))
			else:
				frappe.throw(message, title=_("Set Item Price"))
	
	def validate_country_of_origin(self):
		if self.category != "Food & Beverages":
			if not frappe.db.get_value("Item", self.item_code, "country_of_origin"):
				message = _("Please set country of origin for {0}").format(frappe.bold(self.item_code))
				frappe.throw(message, title=_("Set Country of Origin"))
	
	def validate_warehouse(self):
		hub_seller_settings = frappe.get_cached_doc("Hub Seller Setting")
		for w in self.mapped_warehouse:
			if not any(w.warehouse == s.warehouse for s in hub_seller_settings.warehouse_details):
				message = _("Warehouse {0} is not set in Hub Seller Settings").format(frappe.bold(w.warehouse))
				frappe.throw(message, title=_("Incorrect Warehouse Selected"))
	
	def validate_variants(self):
		sub_category_doc = self.get_sub_category()
		if self.variant_of and self.enable_variants:
			if len(sub_category_doc.get("additional_attributes", [])):
				message = _("Please set the Item Attributes and select the respective Hub Attribute in Item Variants Table")
				if not len(self.item_variants):
					frappe.throw(message, title=_("Select Item Variants"))
				else:
					if not all(i.hub_attribute for i in self.item_variants):
						frappe.throw(message, title=_("Select Item Variants"))
				for i in self.item_variants:
					if not any(a.hub_attribute == i.hub_attribute for a in self.additional_specifications):
						message = _("Please set Hub Variant {0} and its value in Additional Specifications Table").format(i.hub_attribute)
						frappe.throw(message, title=_("Set Item Variant"))
	
	def validate_update_time(self):
		self.last_updated_at = None
		if not self.last_updated_at:
			self.last_updated_at = self.modified
		else:
			if self.last_updated_at < self.modified:
				self.last_updated_at = self.modified
	
	@frappe.whitelist()
	def copy_hub_item_attributes(self):
		sub_category_doc = self.get_sub_category()
		if len(sub_category_doc.get("statutory_attributes", [])):
			for s in sub_category_doc.get("statutory_attributes"):
				if s.mandatory:
					if len(self.specifications) and any(s.hub_attribute == s.attribute_name for s in self.specifications):
						continue
					else:
						row = self.append("specifications")
						row.hub_attribute = s.attribute_name
	
	@frappe.whitelist()
	def set_warehouse(self):
		if frappe.db.exists("Hub Seller Setting"):
			hub_seller_settings = frappe.get_cached_doc("Hub Seller Setting")
			for w in hub_seller_settings.warehouse_details:
				row = self.append("mapped_warehouse")
				row.warehouse = w.warehouse
	
	@frappe.whitelist()
	def set_variant_details(self):
		sub_category_doc = self.get_sub_category()
		if self.variant_of and len(sub_category_doc.get("additional_attributes", [])):
			attributes = frappe.get_list("Item Variant Attribute", filters={"parent": self.variant_of}, fields=["attribute"])
			self.item_variants = []
			for a in attributes:
				row = self.append("item_variants")
				row.attribute = a.attribute
	
	@frappe.whitelist()
	def get_sub_category(self):
		return HubServices().get_sub_category(self.sub_category)
