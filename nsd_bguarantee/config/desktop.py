# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

from frappe import _


def get_data():
	return [
		{
			"module_name": "Bank Guarantee",
			"color": "blue",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Bank Guarantee"),
		}
	]
