# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import MagicMock

try:
	import frappe
	from frappe.tests import IntegrationTestCase
except (ImportError, ModuleNotFoundError):
	# Standalone fallback when running outside of Frappe bench
	import datetime
	import sys

	frappe = MagicMock()
	frappe._dict = dict
	frappe.ValidationError = Exception
	frappe.throw = MagicMock(side_effect=Exception("Frappe Validation Error"))
	frappe_utils = MagicMock()
	frappe_utils.flt = lambda val, precision=None: float(val or 0)
	frappe_utils.getdate = lambda d: datetime.date.fromisoformat(str(d)) if d else None
	frappe_utils.nowdate = lambda: datetime.date.today().isoformat()
	sys.modules["frappe"] = frappe
	sys.modules["frappe.utils"] = frappe_utils
	IntegrationTestCase = unittest.TestCase

from nsd_bguarantee.events.bank_guarantee import (
	bg_issue,
	bg_return,
	get_company,
	on_submit,
	on_update_after_submit,
)
from nsd_bguarantee.utils import is_guarantee_expired


class TestBankGuarantee(IntegrationTestCase):
	def test_is_guarantee_expired(self):
		self.assertTrue(is_guarantee_expired("2020-01-01"))
		self.assertFalse(is_guarantee_expired("2099-01-01"))
		self.assertFalse(is_guarantee_expired(None))

	def test_submit_validation_missing_posting_date(self):
		doc = frappe._dict({
			"name": "BG-TEST-001",
			"posting_date": None,
			"bank_guarantee_purpose": "Bank Guarantee",
		})
		with self.assertRaises(Exception):
			on_submit(doc)

	def test_backwards_compatibility_imports(self):
		from nsd_bguarantee.bank_guarantee.overrides.bank_guarantee.bank_guarantee import (
			on_submit_1,
			on_update_after_submit_1,
		)
		self.assertEqual(on_submit_1, on_submit)
		self.assertEqual(on_update_after_submit_1, on_update_after_submit)


if __name__ == "__main__":
	unittest.main()
