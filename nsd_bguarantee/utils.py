# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

"""Shared utility functions for Nest Bank Guarantee."""

import frappe
from frappe.utils import getdate, nowdate


def is_guarantee_expired(end_date: str | None) -> bool:
	"""Check if the provided end date is past the current date."""
	if not end_date:
		return False
	return getdate(nowdate()) >= getdate(end_date)
