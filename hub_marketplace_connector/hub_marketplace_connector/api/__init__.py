import frappe
from frappe.utils.password import get_decrypted_password

@frappe.whitelist(allow_guest=True)
def handle():
    if validate_auth():
        return handle_request()
    
def handle_request():
    url_parts = frappe.request.path[1:].split("/",3)
    request = url_parts[-1] if url_parts[-1][0] != "/" else url_parts[-1][1:]
    data = frappe._dict(frappe.local.form_dict)
    data.pop("cmd")
    match request:
        case "ping":
            return "pong"
        case "capture_lead":
            return data
    
    raise frappe.ValidationError


def validate_auth():
    try:
        auth_header = frappe.get_request_header("Hub-Authorization").split(" ")
        auth_token = auth_header[1]
        api_key, api_secret = auth_token.split(":")
        doc_key = frappe.db.get_value("Hub Seller Setting", fieldname="api_key")
        doc_secret = get_decrypted_password("Hub Seller Setting", "Hub Seller Setting", fieldname="api_secret")
        if api_key == doc_key and api_secret==doc_secret:
            frappe.session.user = frappe.db.get_value("Hub Seller Setting", fieldname="hub_user")
            return True
        else:
            raise frappe.AuthenticationError
    except Exception:
        raise frappe.AuthenticationError