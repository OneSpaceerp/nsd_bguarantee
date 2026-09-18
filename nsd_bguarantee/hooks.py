app_name = "nsd_bguarantee"
app_title = "Nest Bank Guarantee"
app_publisher = "Nest Software Development"
app_description = "Bank Guarantee Management for ERPNext v16"
app_icon = "octicon octicon-file-directory"
app_color = "blue"
app_email = "info@nestsoftware.dev"
app_license = "MIT"

# Dependencies
# ------------
required_apps = ["erpnext"]

# Document Events
# ---------------
doc_events = {
	"Bank Guarantee": {
		"on_submit": "nsd_bguarantee.events.bank_guarantee.on_submit",
		"on_update_after_submit": "nsd_bguarantee.events.bank_guarantee.on_update_after_submit",
	}
}

# Client Scripts
# --------------
doctype_js = {
	"Bank Guarantee": "public/js/bank_guarantee.js"
}

# Fixtures
# --------
fixtures = [
	{"dt": "Custom Field", "filters": [["module", "in", ["Bank Guarantee", "Ecs Bguarantee"]]]},
	{"dt": "Property Setter", "filters": [["module", "in", ["Bank Guarantee", "Ecs Bguarantee"]]]},
]
