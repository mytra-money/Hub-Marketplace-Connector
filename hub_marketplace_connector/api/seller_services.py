import frappe

class sellerServices:
    def __init__(self, data):
        self.data = data
    
    def ping(self):
        return "pong"
    
    def capture_lead(self):
        lead = self.data
        lead = frappe.parse_json(lead)
        lead_doc = frappe.new_doc("Lead")
        for fieldname in ("lead_name", "company_name", "email_id", "phone"):
            lead_doc.set(fieldname, lead.get(fieldname))

        lead_doc.set("lead_owner", "")

        if not frappe.db.exists("Lead Source", "Hub Marketplace"):
            frappe.get_doc(
                {"doctype": "Lead Source", "source_name": "Hub Marketplace"}
            ).insert(ignore_permissions=True)

        lead_doc.set("source", "Hub Marketplace")

        try:
            lead_doc.save(ignore_permissions=True)
        except frappe.exceptions.DuplicateEntryError:
            frappe.clear_messages()
            lead_doc = frappe.get_doc("Lead", {"email_id": lead["email_id"]})

        lead_doc.add_comment(
            "Comment",
            text="""
            <div>
                <h5>{subject}</h5>
                <p>{message}</p>
            </div>
        """.format(
                subject=lead.get("subject"), message=lead.get("message")
            ),
        )

        return lead_doc
    
    
