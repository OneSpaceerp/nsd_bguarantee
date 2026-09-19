# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Idempotent migration patch for v16:
	1. Migrate legacy 'Ecs Bguarantee' Module Def to 'Bank Guarantee'.
	2. Update records tagged with 'Ecs Bguarantee' module to 'Bank Guarantee'.
	3. Clean up old colliding workspace 'Bank Guarantee' so DocType route is clear.
	4. Ensure 'Bank Guarantees' workspace is correctly configured.
	"""
	# 1. Ensure 'Bank Guarantee' Module Def exists
	if not frappe.db.exists("Module Def", "Bank Guarantee"):
		frappe.get_doc({
			"doctype": "Module Def",
			"module_name": "Bank Guarantee",
			"app_name": "nsd_bguarantee",
			"package": "Bank Guarantee",
		}).insert(ignore_permissions=True)

	# 2. Update Custom Field module references
	frappe.db.sql("""
		UPDATE `tabCustom Field`
		SET module = 'Bank Guarantee'
		WHERE module = 'Ecs Bguarantee'
	""")

	# 3. Update Property Setter module references
	frappe.db.sql("""
		UPDATE `tabProperty Setter`
		SET module = 'Bank Guarantee'
		WHERE module = 'Ecs Bguarantee'
	""")

	# 4. Update Report module references
	frappe.db.sql("""
		UPDATE `tabReport`
		SET module = 'Bank Guarantee'
		WHERE name = 'Bank Guarantee Report'
	""")

	# 5. Delete old colliding workspace 'Bank Guarantee' that shares route with DocType
	if frappe.db.exists("Workspace", "Bank Guarantee"):
		frappe.delete_doc("Workspace", "Bank Guarantee", ignore_permissions=True, force=True)

	# 6. Update 'Bank Guarantees' workspace if present
	frappe.db.sql("""
		UPDATE `tabWorkspace`
		SET module = 'Bank Guarantee', app = 'nsd_bguarantee'
		WHERE name = 'Bank Guarantees'
	""")
