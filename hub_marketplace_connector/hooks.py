app_name = "hub_marketplace_connector"
app_title = "Hub Marketplace Connector"
app_publisher = "pwctech technologies private limited"
app_description = "This is the custom App for ERPNext users to connect with Hub Marketplace"
app_email = "contact@pwctech.in"
app_license = "mit"
extend_bootinfo = "hub_marketplace_connector.boot.set_bootinfo"

# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hub_marketplace_connector/css/hub_marketplace_connector.css"
# app_include_js = "/assets/hub_marketplace_connector/js/hub_marketplace_connector.js"

# include js, css files in header of web template
# web_include_css = "/assets/hub_marketplace_connector/css/hub_marketplace_connector.css"
# web_include_js = "/assets/hub_marketplace_connector/js/hub_marketplace_connector.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hub_marketplace_connector/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hub_marketplace_connector/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hub_marketplace_connector.utils.jinja_methods",
# 	"filters": "hub_marketplace_connector.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hub_marketplace_connector.install.before_install"
# after_install = "hub_marketplace_connector.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hub_marketplace_connector.uninstall.before_uninstall"
# after_uninstall = "hub_marketplace_connector.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hub_marketplace_connector.utils.before_app_install"
# after_app_install = "hub_marketplace_connector.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hub_marketplace_connector.utils.before_app_uninstall"
# after_app_uninstall = "hub_marketplace_connector.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hub_marketplace_connector.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"hub_marketplace_connector.tasks.all"
	# ],
	"daily": [
		"hub_marketplace_connector.tasks.daily"
	],
	"hourly": [
		"hub_marketplace_connector.tasks.hourly"
	],
	# "weekly": [
	# 	"hub_marketplace_connector.tasks.weekly"
	# ],
	# "monthly": [
	# 	"hub_marketplace_connector.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "hub_marketplace_connector.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"hub_marketplace_connector": "hub_marketplace_connector.hub_marketplace_connector.api.handle"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hub_marketplace_connector.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hub_marketplace_connector.utils.before_request"]
# after_request = ["hub_marketplace_connector.utils.after_request"]

# Job Events
# ----------
# before_job = ["hub_marketplace_connector.utils.before_job"]
# after_job = ["hub_marketplace_connector.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hub_marketplace_connector.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

