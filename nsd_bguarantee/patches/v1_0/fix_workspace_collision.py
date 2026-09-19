# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Delete colliding 'Bank Guarantee' Workspace from the database so that
	the route /desk/bank-guarantee correctly opens the DocType list view
	instead of intercepting it with the Workspace view.
	Also reload the 'Bank Guarantees' workspace and clear cache.
	"""
	# 1. Delete standard or customized 'Bank Guarantee' workspace
	if frappe.db.exists("Workspace", "Bank Guarantee"):
		frappe.delete_doc("Workspace", "Bank Guarantee", ignore_permissions=True, force=True)

	# 2. Safety cleanup of child tables and database records in case delete_doc bypassed anything
	frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = 'Bank Guarantee'")
	frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = 'Bank Guarantee'")
	frappe.db.sql("DELETE FROM `tabWorkspace Quick List` WHERE parent = 'Bank Guarantee'")
	frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'Bank Guarantee'")

	# 3. Clean up any custom workspace named 'bank-guarantee' or slug variations
	workspaces_to_remove = frappe.db.sql_list("""
		SELECT name FROM `tabWorkspace`
		WHERE name IN ('Bank Guarantee', 'bank-guarantee')
		   OR (module = 'Bank Guarantee' AND name NOT IN ('Bank Guarantees', 'bank-guarantees'))
	""")
	for ws_name in workspaces_to_remove:
		try:
			frappe.delete_doc("Workspace", ws_name, ignore_permissions=True, force=True)
		except Exception:
			pass

	# 4. Reload the new 'Bank Guarantees' workspace definition
	try:
		frappe.reload_doc("bank_guarantee", "workspace", "bank_guarantees", force=True)
	except Exception:
		pass

	# 5. Clear cache
	frappe.clear_cache()
