# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Bank Guarantee"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Bank Guarantee",
			"width": 120,
		},
		{
			"label": _("No"),
			"fieldname": "bank_guarantee_number",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Beneficiary"),
			"fieldname": "name_of_beneficiary",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Purpose"),
			"fieldname": "bank_guarantee_purpose",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Bank"),
			"fieldname": "bank",
			"fieldtype": "Link",
			"options": "Bank",
			"width": 120,
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Extended Date"),
			"fieldname": "new_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Status"),
			"fieldname": "bank_guarantee_status",
			"fieldtype": "Data",
			"width": 90,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Bank %"),
			"fieldname": "bank_percent",
			"fieldtype": "Percent",
			"width": 80,
		},
		{
			"label": _("Bank Amount"),
			"fieldname": "bank_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Facility %"),
			"fieldname": "facility_percent",
			"fieldtype": "Percent",
			"width": 80,
		},
		{
			"label": _("Facility Amount"),
			"fieldname": "facility_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
	]


def get_data(filters):
	if not filters:
		filters = {}

	conditions = []
	if filters.get("type_of_letter_of_guarantee"):
		conditions.append("a.type_of_letter_of_guarantee = %(type_of_letter_of_guarantee)s")
	if filters.get("status_of_letter_of_guarantee"):
		conditions.append("a.status_of_letter_of_guarantee = %(status_of_letter_of_guarantee)s")
	if filters.get("bank_guarantee_purpose"):
		conditions.append("a.bank_guarantee_purpose = %(bank_guarantee_purpose)s")
	if filters.get("from_date"):
		conditions.append("a.start_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("a.end_date <= %(to_date)s")
	if filters.get("bg_type"):
		conditions.append("a.bg_type = %(bg_type)s")
	if filters.get("bank"):
		conditions.append("a.bank = %(bank)s")

	conditions_str = ""
	if conditions:
		conditions_str = " AND " + " AND ".join(conditions)

	query = f"""
		SELECT
			a.name AS name,
			a.bank_guarantee_number AS bank_guarantee_number,
			a.name_of_beneficiary AS name_of_beneficiary,
			a.bank_guarantee_purpose AS bank_guarantee_purpose,
			a.bank AS bank,
			a.bank_guarantee_status AS bank_guarantee_status,
			a.end_date AS end_date,
			a.start_date AS start_date,
			a.new_date AS new_date,
			a.amount AS amount,
			a.rate AS bank_percent,
			a.bank_amount AS bank_amount,
			a.rate2 AS facility_percent,
			a.facility_amount AS facility_amount
		FROM `tabBank Guarantee` a
		WHERE a.docstatus != 2 {conditions_str}
		ORDER BY a.creation DESC
	"""

	return frappe.db.sql(query, filters, as_dict=1)