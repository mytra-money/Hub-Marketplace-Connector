# Copyright (c) 2024, pwctech technologies private limited and contributors
# For license information, please see license.txt

import frappe
import copy
from frappe.model.document import Document
from frappe import _
from frappe.utils.data import add_years, format_date, get_host_name, get_url
from frappe.integrations.utils import create_request_log
from hub_marketplace_connector.api.hub_services import HubServices

class HubSellerSetting(Document):
	def validate(self):
		self.add_keys()
		self.validate_contacts()
		self.validate_fulfilments()
		if not self.enabled:
			self.subscribe()
	
	def add_keys(self):
		self.subscriber_url = get_url("/api/method/hub_connect")

	def validate_contacts(self):
		support_contact = frappe.get_cached_doc("Contact", self.support_contact)
		if not ((support_contact.phone or support_contact.mobile_no) and support_contact.email_id):
			frappe.throw(_("Primary Phone Number / Mobile Number / Email not set in Contact doc for {0}").format(support_contact.name))
	
	def validate_fulfilments(self):
		if not len(self.warehouse_details):
			frappe.throw(_("Atleast one line item in warehouse details is required"))
		else:
			for warehouse in self.warehouse_details:
				self.validate_warehouse_address_and_contact(warehouse)
	
	def validate_warehouse_address_and_contact(self, warehouse):
		for i in ["Address", "Contact"]:
			filters = [
				["Dynamic Link", "link_doctype", "=", "Warehouse"],
				["Dynamic Link", "link_name", "=", warehouse.warehouse],
				["Dynamic Link", "parenttype", "=", i]
			]
			if i == "Address":
				existing_address = frappe.get_list("Address", filters)
				if len(existing_address):
					address_doc = frappe.get_doc("Address", existing_address[0].name)
					if not (address_doc.address_line1\
						and address_doc.city and address_doc.state\
						and address_doc.pincode and address_doc.country):
						frappe.throw(_("Mandatory fields i.e. State / Pincode not set in address doc for warehouse in row {0}").format(warehouse.idx))
					if not address_doc.address_line2:
						frappe.throw(_("Please split Address in Line 1 and Line 2 in address doc for warehouse in row {0}").format(warehouse.idx))
					if not any(l.link_doctype == "Company" and l.link_name == self.company for l in address_doc.links):
						address_doc.append("links", dict(link_doctype="Company", link_name=self.company))
						address_doc.save(ignore_permissions=True)
				else:
					frappe.throw(_("Address not set for warehouse in row {0}").format(warehouse.idx))
			else:
				existing_contacts = frappe.get_list("Contact", filters)
				if len(existing_contacts):
					contact_doc = frappe.get_doc("Contact", existing_contacts[0].name)
					if not (contact_doc.phone or contact_doc.mobile_no):
						frappe.throw(_("Primary Phone Number / Mobile Number not set in contact doc for warehouse in row {0}").format(warehouse.idx))
				else:
					frappe.throw(_("Contact not set for warehouse in row {0}").format(warehouse.idx))

	def subscribe(self):
		hub_user = frappe.get_cached_doc("User", self.hub_user)
		user_data = {
			"user": {
				"email": hub_user.email,
				"first_name": hub_user.first_name,
				"last_name": hub_user.last_name
			}
		}
		integration_request = create_request_log(user_data, service_name="Hub Marketplace Registration")
		try:
			response = HubServices().register_user(user_data)
			integration_response = copy.deepcopy(response)
			if response:
				if not response.get("api_key"):
					integration_request.status = "Failed"
				else:
					self.api_key = response.get("api_key")
					self.api_secret = response.get("api_secret")
					integration_request.status = "Completed"
					self.enabled = 1
					integration_response["api_secret"] = "**************"
			else:
				integration_request.status = "Failed"
			integration_request.output = frappe.as_json(integration_response, indent=4)
			integration_request.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(frappe.get_traceback(), frappe.as_json(user_data))
			frappe.throw("Error while registering to Hub Marketplace. Please check the error log for more details")
	
	def get_seller_data(self):
		company = frappe.get_cached_doc("Company", self.company)
		support_contact = frappe.get_cached_doc("Contact", self.support_contact)
		logo_file = frappe.get_value("File", fieldname = ["file_url"], filters={"attached_to_name": self.name, "attached_to_doctype": self.doctype})
		seller_data = {
			"seller_name": company.company_name,
			"brand": self.store_name,
			"logo": get_url(logo_file),
			"short_description": self.short_description,
			"long_description": self.long_description,
			"inactive": self.inactive,
			"allow_items_not_in_stock": self.allow_items_not_in_stock,
			"erpnext_url": self.subscriber_url,
			"mobile_number": support_contact.phone or support_contact.mobile_no,
			"email": support_contact.email_id,
			"warehouse_details": []
		}
		for warehouse in self.warehouse_details:
			filters = [
				["Dynamic Link", "link_doctype", "=", "Warehouse"],
				["Dynamic Link", "link_name", "=", warehouse.warehouse],
				["Dynamic Link", "parenttype", "=", "Address"]
			]
			warehouse_addresses = frappe.get_list("Address", filters)
			warehouse_address = frappe.get_doc("Address", warehouse_addresses[0].name)
			warehouse_settings = frappe.get_cached_doc("Hub Seller Warehouse Setting", warehouse.warehouse)
			warehouse_data = {
				"warehouse_id": warehouse.warehouse,
				"pickup_available": warehouse_settings.pickup_available,
				"delivery_available": warehouse_settings.delivery_available,
				"disabled": warehouse_settings.disabled,
				"address": {
					"address_line1": warehouse_address.address_line1,
					"address_line2": warehouse_address.address_line2,
					"city": warehouse_address.city,
					"state": warehouse_address.state,
					"pincode": warehouse_address.pincode, 
					"country": warehouse_address.country
				}
			}
			if warehouse_settings.delivery_available:
				warehouse_data["deliver_based_on"] = warehouse_settings.deliver_based_on
				warehouse_data["delivery_time"] = warehouse_settings.delivery_time
				if warehouse_settings.deliver_based_on == "Distance":
					warehouse_data["distance"] = warehouse_settings.distance
				elif warehouse_settings.deliver_based_on == "Pincode":
					warehouse_data["pincode"] = []
					for p in warehouse_settings.pincode_details:
						warehouse_data["pincode"].append({"from_pincode": p.from_pincode, "to_pincode": p.to_pincode})
			seller_data["warehouse_details"].append(warehouse_data)
		
		return seller_data