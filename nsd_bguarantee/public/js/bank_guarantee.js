// Copyright (c) 2026, Nest Software Development and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bank Guarantee", {
	setup(frm) {
		frm.set_query("reference_doctype", () => {
			return {
				filters: [["DocType", "name", "in", ["Sales Order", "Purchase Order"]]]
			};
		});

		frm.set_query("dpaccount", () => {
			return {
				filters: [["Account", "is_group", "!=", 1]]
			};
		});

		frm.set_query("dpaccountc", () => {
			return {
				filters: [["Account", "is_group", "!=", 1]]
			};
		});

		frm.set_query("deduction_return", () => {
			return {
				filters: [
					["Account", "is_group", "!=", 1],
					["Account", "account_type", "in", ["Cash", "Bank"]]
				]
			};
		});

		frm.set_query("cash_account", () => {
			return {
				filters: [
					["Account", "is_group", "!=", 1],
					["Account", "account_type", "=", "Cash"]
				]
			};
		});

		frm.set_query("party_type", () => {
			return {
				filters: [["DocType", "name", "in", ["Customer", "Supplier"]]]
			};
		});

		frm.set_query("account_for_bank_facilities", () => {
			return {
				filters: frm.doc.bank ? [["Bank Account", "bank", "=", frm.doc.bank]] : []
			};
		});
	},

	onload(frm) {
		frm.set_df_property("reference_doctype", "read_only", 0);
	},

	bank_account(frm) {
		if (frm.doc.bank_account) {
			frappe.db.get_value("Bank Account", frm.doc.bank_account, "account", (r) => {
				if (r && r.account) {
					frm.set_value("account", r.account);
				}
			});
		}
	},

	bank_guarantee_purpose(frm) {
		if (frm.doc.bank_guarantee_purpose === "Secretariats") {
			frm.set_value("bg_type", "Providing");
		}
	},

	party(frm) {
		if (frm.doc.party) {
			frm.set_value("name_of_beneficiary", frm.doc.party);
			if (frm.doc.party_type === "Customer") {
				frm.set_value("customer", frm.doc.party);
			}
		}
	},

	customer(frm) {
		if (frm.doc.customer) {
			frm.set_value("name_of_beneficiary", frm.doc.customer);
		}
	},

	rate(frm) {
		if (frm.doc.banking_facilities === "With Facilities") {
			const rate = flt(frm.doc.rate);
			const amount = flt(frm.doc.amount);
			const bank_amount = (rate / 100) * amount;
			const rate2 = 100 - rate;
			const facility_amount = (rate2 / 100) * amount;

			frm.set_value("bank_amount", bank_amount);
			frm.set_value("rate2", rate2);
			frm.set_value("facility_amount", facility_amount);
		}
	},

	rate2(frm) {
		if (frm.doc.banking_facilities === "With Facilities") {
			const rate2 = flt(frm.doc.rate2);
			const rate = 100 - rate2;
			const amount = flt(frm.doc.amount);
			const bank_amount = (rate / 100) * amount;
			const facility_amount = (rate2 / 100) * amount;

			frm.set_value("rate", rate);
			frm.set_value("bank_amount", bank_amount);
			frm.set_value("facility_amount", facility_amount);
		}
	},

	amount(frm) {
		if (frm.doc.banking_facilities === "Without Facilities") {
			frm.set_value("rate", 100);
			frm.set_value("bank_amount", frm.doc.amount);
		} else if (frm.doc.banking_facilities === "With Facilities" && frm.doc.rate) {
			const rate = flt(frm.doc.rate);
			const amount = flt(frm.doc.amount);
			const bank_amount = (rate / 100) * amount;
			const rate2 = 100 - rate;
			const facility_amount = (rate2 / 100) * amount;

			frm.set_value("bank_amount", bank_amount);
			frm.set_value("facility_amount", facility_amount);
		}
	}
});
