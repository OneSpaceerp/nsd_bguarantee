# Copyright (c) 2026, Nest Software Development and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate


def get_company(doc) -> str:
	"""Resolve company for Bank Guarantee transactions."""
	company = doc.get("company")
	if not company:
		company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		frappe.throw(_("Please configure Default Company in Global Defaults or select Company."))
	return company


def on_submit(doc, method=None):
	"""Lifecycle hook triggered when Bank Guarantee is submitted."""
	if not doc.posting_date:
		frappe.throw(_("Please Enter Posting Date."))

	if not doc.bank and doc.bank_guarantee_purpose in ("Bank Guarantee", "Cheque"):
		frappe.throw(_("Select the Bank before submitting."))

	if not doc.rate and doc.bank_guarantee_purpose == "Bank Guarantee":
		frappe.throw(_("Enter the Bank Rate (%) before submitting."))

	if not doc.bank_amount and doc.bank_guarantee_purpose == "Bank Guarantee":
		frappe.throw(_("Enter the Bank Amount before submitting."))

	if not doc.dpaccount and doc.bank_guarantee_purpose != "Cheque":
		frappe.throw(_("Select the Insurance Account before submitting."))

	if not doc.dpaccountc and doc.bank_guarantee_purpose in ("Bank Guarantee", "Cheque"):
		frappe.throw(_("Select the Fees Account before submitting."))

	if not doc.cash_account and doc.bank_guarantee_purpose == "Cash":
		frappe.throw(_("Select the Cash Account before submitting."))

	if not doc.reference_date and doc.bank_guarantee_purpose == "Cheque":
		frappe.throw(_("Enter the Reference Date before submitting."))

	if doc.bank_guarantee_purpose == "Bank Guarantee" and flt(doc.bg_commission) < 1:
		frappe.throw(_("Bank Guarantee Commission cannot be zero!"))

	# Create issuance journal entry while posting_date is set
	bg_issue(doc)

	# Mark issued and clear posting date for future return workflow
	doc.db_set("issued", 1)
	doc.db_set("bank_guarantee_status", "Issued")
	doc.db_set("posting_date", None)


def on_update_after_submit(doc, method=None):
	"""Lifecycle hook triggered when Bank Guarantee is updated after submit."""
	today_date = getdate(nowdate())

	if doc.extend_validity and doc.new_date:
		doc.db_set("bank_guarantee_status", "Extended")

	if doc.bank_guarantee_status != "Returned":
		if doc.extend_validity and doc.new_date and today_date >= getdate(doc.new_date):
			doc.db_set("bank_guarantee_status", "Expired")
		elif not doc.extend_validity and doc.end_date and today_date >= getdate(doc.end_date):
			doc.db_set("bank_guarantee_status", "Expired")

	if doc.bank_guarantee_status == "Returned" and doc.bank_guarantee_purpose == "Deduction" and not doc.deduction_return:
		frappe.throw(_("Select the Return Account before submitting."))

	bg_return(doc)


def bg_issue(doc, method=None):
	"""Create and submit Journal Entry for Bank Guarantee issuance."""
	company = get_company(doc)

	if doc.party_type == "Customer":
		party_account = frappe.db.get_value("Company", company, "default_receivable_account")
	else:
		party_account = frappe.db.get_value("Company", company, "default_payable_account")

	amount = flt(doc.amount)
	bg_commission = flt(doc.bg_commission)
	bank_amount = flt(doc.bank_amount)
	facility_amount = flt(doc.facility_amount)
	cheque_no = doc.bank_guarantee_number or doc.name

	# Cash - Providing
	if doc.bank_guarantee_purpose == "Cash" and not doc.issued and doc.bg_type == "Providing":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.cash_account,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Cash Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Cash - Receiving
	elif doc.bank_guarantee_purpose == "Cash" and not doc.issued and doc.bg_type == "Receiving":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.cash_account,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Cash Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Bank Guarantee - Without Facilities
	elif doc.bank_guarantee_purpose == "Bank Guarantee" and not doc.issued and doc.banking_facilities == "Without Facilities":
		total_amount = amount + bg_commission
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccountc,
				"debit": bg_commission,
				"credit": 0,
				"debit_in_account_currency": bg_commission,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"debit": 0,
				"credit": bg_commission,
				"credit_in_account_currency": bg_commission,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Bank Guarantee Without Facilities {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, total_amount)

	# Bank Guarantee - With Facilities
	elif doc.bank_guarantee_purpose == "Bank Guarantee" and not doc.issued and doc.banking_facilities == "With Facilities":
		total_amount = amount + bg_commission
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccountc,
				"debit": bg_commission,
				"credit": 0,
				"debit_in_account_currency": bg_commission,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"debit": 0,
				"credit": bank_amount,
				"credit_in_account_currency": bank_amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"debit": 0,
				"credit": bg_commission,
				"credit_in_account_currency": bg_commission,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account_1,
				"debit": 0,
				"credit": facility_amount,
				"credit_in_account_currency": facility_amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Bank Guarantee With Facilities {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, total_amount)

	# Deduction - Providing
	elif doc.bank_guarantee_purpose == "Deduction" and not doc.issued and doc.bg_type == "Providing":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": party_account,
				"party_type": doc.party_type,
				"party": doc.party,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Deduction Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Deduction - Receiving
	elif doc.bank_guarantee_purpose == "Deduction" and not doc.issued and doc.bg_type == "Receiving":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": party_account,
				"party_type": doc.party_type,
				"party": doc.party,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Deduction Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Cheque - Providing
	elif doc.bank_guarantee_purpose == "Cheque" and not doc.issued and doc.bg_type == "Providing":
		i_ch_cr = frappe.db.get_value("Company", company, "acc1")
		if not i_ch_cr:
			frappe.throw(_("Please configure Cheques For Payment Deposits Account (acc1) in Company {0}").format(company))

		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"credit": 0,
				"debit": amount,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccountc,
				"credit": 0,
				"debit": bg_commission,
				"debit_in_account_currency": bg_commission,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": i_ch_cr,
				"credit": amount,
				"debit": 0,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"credit": bg_commission,
				"debit": 0,
				"credit_in_account_currency": bg_commission,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Cheque Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.reference_date, accounts, remark, amount)

	# Cheque - Receiving
	elif doc.bank_guarantee_purpose == "Cheque" and not doc.issued and doc.bg_type == "Receiving":
		r_ch_dr = frappe.db.get_value("Company", company, "acc3")
		r_ch_cr = frappe.db.get_value("Company", company, "acc2")
		if not r_ch_dr or not r_ch_cr:
			frappe.throw(_("Please configure Cheques accounts (acc2 and acc3) in Company {0}").format(company))

		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": r_ch_dr,
				"credit": 0,
				"debit": amount,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": r_ch_cr,
				"credit": amount,
				"debit": 0,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Issue Cheque Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.reference_date, accounts, remark, amount)


def bg_return(doc, method=None):
	"""Create and submit Journal Entry for Bank Guarantee return."""
	if doc.bank_guarantee_status != "Returned" or doc.returned:
		return

	if not doc.posting_date:
		frappe.throw(_("Please Enter Posting Date."))

	company = get_company(doc)

	if doc.party_type == "Customer":
		party_account = frappe.db.get_value("Company", company, "default_receivable_account")
	else:
		party_account = frappe.db.get_value("Company", company, "default_payable_account")

	amount = flt(doc.amount)
	bank_amount = flt(doc.bank_amount)
	facility_amount = flt(doc.facility_amount)
	cheque_no = doc.bank_guarantee_number or doc.name

	# Cash - Providing
	if doc.bank_guarantee_purpose == "Cash" and doc.bg_type == "Providing":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.cash_account,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Cash Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Cash - Receiving
	elif doc.bank_guarantee_purpose == "Cash" and doc.bg_type == "Receiving":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.cash_account,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Cash Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Bank Guarantee - Without Facilities
	elif doc.bank_guarantee_purpose == "Bank Guarantee" and doc.banking_facilities == "Without Facilities":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Bank Guarantee Without Facilities {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Bank Guarantee - With Facilities
	elif doc.bank_guarantee_purpose == "Bank Guarantee" and doc.banking_facilities == "With Facilities":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account,
				"debit": bank_amount,
				"credit": 0,
				"debit_in_account_currency": bank_amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.account_1,
				"debit": facility_amount,
				"credit": 0,
				"debit_in_account_currency": facility_amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Bank Guarantee With Facilities {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Deduction - Providing
	elif doc.bank_guarantee_purpose == "Deduction" and doc.bg_type == "Providing":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"party_type": doc.party_type,
				"party": doc.party,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.deduction_return,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Deduction Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Deduction - Receiving
	elif doc.bank_guarantee_purpose == "Deduction" and doc.bg_type == "Receiving":
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": amount,
				"party_type": doc.party_type,
				"party": doc.party,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.deduction_return,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Deduction Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.posting_date, accounts, remark, amount)

	# Cheque - Providing
	elif doc.bank_guarantee_purpose == "Cheque" and doc.bg_type == "Providing":
		i_ch_cr = frappe.db.get_value("Company", company, "acc1")
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": i_ch_cr,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": doc.dpaccount,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Cheque Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.reference_date, accounts, remark, amount)

	# Cheque - Receiving
	elif doc.bank_guarantee_purpose == "Cheque" and doc.bg_type == "Receiving":
		r_ch_dr = frappe.db.get_value("Company", company, "acc3")
		r_ch_cr = frappe.db.get_value("Company", company, "acc2")
		accounts = [
			{
				"doctype": "Journal Entry Account",
				"account": r_ch_cr,
				"debit": amount,
				"credit": 0,
				"debit_in_account_currency": amount,
				"user_remark": doc.name,
			},
			{
				"doctype": "Journal Entry Account",
				"account": r_ch_dr,
				"debit": 0,
				"credit": amount,
				"credit_in_account_currency": amount,
				"user_remark": doc.name,
			},
		]
		remark = _("Return Cheque Bank Guarantee {0}").format(doc.name)
		_make_journal_entry(company, doc.name, doc.posting_date, cheque_no, doc.reference_date, accounts, remark, amount)

	doc.db_set("returned", 1)
	doc.db_set("bank_guarantee_status", "Returned")


def _make_journal_entry(
	company: str,
	doc_name: str,
	posting_date: str,
	cheque_no: str,
	cheque_date: str,
	accounts: list,
	remark: str,
	total: float,
):
	"""Helper to instantiate, insert, and submit a Journal Entry."""
	je = frappe.get_doc({
		"doctype": "Journal Entry",
		"voucher_type": "Journal Entry",
		"reference_doctype": "Bank Guarantee",
		"reference_link": doc_name,
		"company": company,
		"posting_date": posting_date,
		"accounts": accounts,
		"cheque_no": cheque_no,
		"cheque_date": cheque_date or posting_date,
		"user_remark": remark,
		"total_debit": total,
		"total_credit": total,
		"remark": remark,
	})
	je.insert()
	je.submit()
	return je
