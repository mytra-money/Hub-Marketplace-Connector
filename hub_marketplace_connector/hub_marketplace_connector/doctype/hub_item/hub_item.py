# Copyright (c) 2024, pwctech technologies private limited and contributors
# For license information, please see license.txt

import frappe
import copy
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, getdate, get_url
from frappe.utils.nestedset import get_root_of
from hub_marketplace_connector.api.hub_services import HubServices
from erpnext.stock.utils import get_stock_balance

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
		self.validate_return_policy()
	
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
	
	def validate_return_policy(self):
		if flt(self.return_within) <=1200:
			frappe.throw("Return policy should have a resonable return window for defective products. Please select a resonable return time in Return Within")

	@frappe.whitelist()
	def copy_hub_item_attributes(self):
		sub_category_doc = self.get_sub_category()
		if len(sub_category_doc.get("statutory_attributes", [])):
			for s in sub_category_doc.get("statutory_attributes"):
				if s.get("mandatory"):
					if len(self.specifications) and any(specification.hub_attribute == s.get("attribute_name") for specification in self.specifications):
						continue
					else:
						row = self.append("specifications")
						row.hub_attribute = s.get("attribute_name")
	
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
		return HubServices().get_category(self.sub_category)

	def get_item_data(self):
		item_data = {
			"seller_item_code": self.item_code,
			"item_name": self.item_name,
			"category": self.category,
			"sub_category": self.sub_category,
			"food_type": self.food_type,
			"returnable": self.returnable,
			"return_within": self.return_within,
			"cancellable": self.cancellable,
			"available_on_cod": self.available_on_cod,
			"short_description": self.short_description,
			"long_description": self.long_description,
			"warehouse_detail": [],
			"specifications": [],
			"additional_specifications": []
		}
		for warehouse in self.mapped_warehouse:
			if not frappe.db.get_value("Hub Seller Setting", fieldname="allow_items_not_in_stock"):
				balance = flt(get_stock_balance(self.item_code, warehouse.warehouse), precision=0)
				if balance <= 0:
					return None
				else:
					item_data["warehouse_detail"].append({"warehouse_id": warehouse.warehouse, "available_quantity": balance, "maximum_quantity": 99})
			else:
				item_data["warehouse_detail"].append({"warehouse_id": warehouse.warehouse, "available_quantity": 99, "maximum_quantity": 99})
		
		maximum_price, offered_price = get_price(self.item_code)
		item_data["maximum_price"] = maximum_price
		item_data["offered_price"] = offered_price
		
		if self.cancellable:
			item_data["cancel_within"] = self.cancel_within
		if self.returnable:
			item_data["pickup_on_return"] = self.pickup_on_return
		
		if self.image:
			item_data["image"] = get_url(frappe.db.get_value("File", filters={"attached_to_name": self.name, "attached_to_doctype": self.doctype, "attached_to_field": "image"}, fieldname="file_url"))
		if self.back_image:
			item_data["back_image"] = get_url(frappe.db.get_value("File", filters={"attached_to_name": self.name, "attached_to_doctype": self.doctype, "attached_to_field": "back_image"}, fieldname="file_url"))
		if self.additional_images:
			item_data["additional_images"] = []
			slideshow_file_list = frappe.get_all("File", fields = ["file_url"], filters={"attached_to_name": self.additional_images, "attached_to_doctype": "Website Slideshow"})
			for f in slideshow_file_list:
				item_data["additional_images"].append(get_url(f.file_url))
		
		if len(self.specifications):
			for s in self.specifications:
				item_data["specifications"].append({"attribute": s.hub_attribute, "value": s.value})
		
		if len(self.additional_specifications):
			for a in self.additional_specifications:
				item_data["additional_specifications"].append({"attribute": a.hub_attribute, "value": a.value})

		return item_data

def get_price(item_code, qty=1):
	from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
	hub_price_list = frappe.db.get_value("Hub Seller Setting", fieldname="price_list")
	hub_company = frappe.db.get_value("Hub Seller Setting", fieldname="company")
	hub_customer_group = frappe.db.get_value("Hub Seller Setting", fieldname="customer_group")
	template_item_code = frappe.db.get_value("Item", item_code, "variant_of")
	hub_default_tax_template = frappe.db.get_value("Hub Seller Setting", fieldname="default_tax_template")
	
	price = frappe.get_all("Item Price", fields=["price_list_rate", "currency", "valid_from"],
		filters=[["Item Price","valid_upto",">", getdate()],["Item Price","item_code","=",item_code],["Item Price","price_list","=", hub_price_list]])
	
	if not price:
		price = frappe.get_all("Item Price", fields=["price_list_rate", "currency", "valid_from"],
		filters=[["Item Price","valid_upto","is","not set"],["Item Price","item_code","=",item_code],["Item Price","price_list","=", hub_price_list]])

	if template_item_code and not price:
		price = frappe.get_all("Item Price", fields=["price_list_rate", "currency", "valid_from"],
			filters=[["Item Price","valid_upto",">", getdate()],["Item Price","item_code","=",template_item_code],["Item Price","price_list","=", hub_price_list]])
		
		if not price:
			price = frappe.get_all("Item Price", fields=["price_list_rate", "currency", "valid_from"],
				filters=[["Item Price","valid_upto","is","not set"],["Item Price","item_code","=",template_item_code],["Item Price","price_list","=", hub_price_list]])

	pricing_rule_dict = frappe._dict({
		"item_code": item_code,
		"qty": qty,
		"stock_qty": qty,
		"transaction_type": "selling",
		"price_list": hub_price_list,
		"company": hub_company,
		"conversion_rate": 1,
		"currency": frappe.db.get_value("Price List", hub_price_list, "currency"),
		"doctype": "Quotation",
		"customer_group": hub_customer_group if hub_customer_group else get_root_of("Customer Group")
	})
	pricing_rule = get_pricing_rule_for_item(pricing_rule_dict)
	price_obj = max(price, key=lambda item: item['valid_from'])
	# price/mrp without any rules applied
	mrp = flt(price_obj.price_list_rate, precision=2)
	if pricing_rule:
		if pricing_rule.pricing_rule_for == "Discount Percentage":
			price_obj.price_list_rate = flt(price_obj.price_list_rate * (1.0 - (flt(pricing_rule.discount_percentage) / 100.0)), precision=2)
		elif pricing_rule.pricing_rule_for == "Rate":
			price_obj.price_list_rate = pricing_rule.price_list_rate or 0
		elif pricing_rule.pricing_rule_for == "Discount Amount":
			price_obj.price_list_rate = flt((price_obj.price_list_rate - pricing_rule.discount_amount), precision=2)
	item_taxes = frappe.get_all("Item Tax", fields=["*"], filters={"parent": item_code})
	if len(item_taxes):
		taxes_with_validity = []
		taxes_with_no_validity = []
		for tax in item_taxes:
			if tax.valid_from:
				if getdate(tax.valid_from) <= getdate():
					taxes_with_validity.append(tax)
			else:
				taxes_with_no_validity.append(tax)
		if taxes_with_validity:
			taxes = sorted(taxes_with_validity, key = lambda i: i.valid_from, reverse=True)
		else:
			taxes = taxes_with_no_validity
		
		if not taxes_with_validity and (not taxes_with_no_validity):
			return mrp, price_obj.price_list_rate
		else:
			default_tax_template = frappe.get_doc("Sales Taxes and Charges Template", hub_default_tax_template)
			item_tax_rate = 0.0
			for default_tax in default_tax_template.taxes:
				for t in taxes:
					item_tax_template = frappe.get_doc("Item Tax Template", t.item_tax_template)
					for item_tax in item_tax_template.taxes:
						if item_tax.tax_type == default_tax.account_head:
							item_tax_rate += item_tax.tax_rate
			return flt(copy.deepcopy(flt(mrp*(1+item_tax_rate/100), precision=0)), precision=2), flt(copy.deepcopy(flt(price_obj.price_list_rate*(1+item_tax_rate/100), precision=0)), precision=2)	
	else:
		return mrp, price_obj.price_list_rate