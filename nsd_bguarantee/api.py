# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_bank_guarantee_details(name: str):
	"""Fetch details of a Bank Guarantee with permission checks."""
	if not frappe.has_permission("Bank Guarantee", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	return frappe.get_doc("Bank Guarantee", name)
